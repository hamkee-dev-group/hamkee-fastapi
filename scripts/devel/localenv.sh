#!/bin/bash

# Command to run the linter.
LINTER_CMD="rye run ruff ."

# Function to check we are running the script from the root of the project
function check_root() {
    if [ ! -d "./app" ]; then
        echo "You must run this script from the root of the project."
        exit 1
    fi
}

function check_venv() {
    if [ ! -d "./.venv" ]; then
        echo "No virtual environment found. Be sure to run 'rye sync' before running this command."
        exit 1
    fi
}

function check_envfile() {
    if [ ! -f "./.result" ]; then
        echo -e "The \033[1m.env\033[0m file does not exist. Please run \033[1m./scripts/devel/localenv.sh install\033[0m command to create it."
        exit 1
    fi
}

function rye_installed() {
  if [ -f "$HOME/.rye/env" ]; then
    return 0
  else
    return 1
  fi
} 

function activate_venv() {
    if ! rye_installed; then
        echo "Rye is not installed. Please install it and try again."
        echo "It should be installed by the install.sh script."
        exit 1
    fi
    source $HOME/.rye/env
    . ./.venv/bin/activate
}

function run_fg() {
    check_root
    check_envfile
    check_venv
    activate_venv
    PYTHONPATH=`pwd`/app hypercorn --bind "$API_HOST:$API_PORT" --reload main:app
}

function run_pytest() {
    check_root
    check_venv
    activate_venv
    echo "Running pytest..."
    pytest -vv ./tests "$@"
}

function run_linter() {
    check_root
    check_venv
    activate_venv
    cd ./app
    echo "Running linter..."
    eval $LINTER_CMD
}

function run_install() {
    check_root
    chmod +x ./scripts/devel/install.sh
    ./scripts/devel/install.sh
}

check_root
if [[ "$1" != "install" ]]; then
    check_envfile
    source .result
fi

if [[ "$1" == "up" ]]; then
    run_fg
elif [[ "$1" == "install" ]]; then
    run_install
elif [[ "$1" == "pytest" ]]; then
    run_pytest "$@"
elif [[ "$1" == "down" ]]; then
    docker compose -v down 
elif [[ "$1" == "lint" ]]; then
    run_linter
else
    # Write the usage message
    echo -e "Usage:"
    echo -e "  \033[1mup\033[0m: start the local environment"
    echo -e "  \033[1mdown\033[0m: stop the local environment"
    echo -e "  \033[1mpytest\033[0m: run pytest in the container. It accepts all the pytest arguments."
    echo -e "  \033[1mlint\033[0m: run black to lint the code"
    echo -e "  \033[1minstall\033[0m: install project from scratch (it'll create a virtualenv, config files, etc.)"
fi
