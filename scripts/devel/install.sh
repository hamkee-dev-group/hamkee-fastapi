#!/usr/bin/env bash

#-------------------------------------------------------
# Color and formatting helper functions
#-------------------------------------------------------
function print_header() {
    echo -e "\n\033[1;34m==== $1 ====\033[0m\n"
}

function print_success() {
    echo -e "\033[1;32m✓ $1\033[0m"
}

function print_info() {
    echo -e "\033[1;36mℹ $1\033[0m"
}

function print_warning() {
    echo -e "\033[1;33m⚠ $1\033[0m"
}

function print_error() {
    echo -e "\033[1;31m✗ $1\033[0m"
}

function print_step() {
    echo -e "\033[1;36m→ $1\033[0m"
}

function print_divider() {
    echo -e "\033[1;34m----------------------------------------\033[0m"
}

#-------------------------------------------------------
# Environment and configuration functions
#-------------------------------------------------------
function rye_installed() {
  if [ -f "$HOME/.rye/env" ]; then
    return 0
  else
    return 1
  fi
}

function hamkee_api_config_file_exists() {
  if [ -f ".env" ]; then
    return 0
  else
    return 1
  fi
}

function read_hamkee_api_config_file() {
  if hamkee_api_config_file_exists; then
    source .env
  fi
}

#-------------------------------------------------------
# File generation functions
#-------------------------------------------------------
function generate_pyproject_toml() {
  sed -e "s/\$NAME/$PROJECT_NAME/g" \
      -e "s/\$DESCRIPTION/$PROJECT_DESCRIPTION/g" \
      -e "s/\$AUTHOR_NAME/$PROJECT_AUTHOR_NAME/g" \
      -e "s/\$AUTHOR_EMAIL/$PROJECT_AUTHOR_EMAIL/g" \
      -e "s/\$PYTHON_VERSION/$PYTHON_VERSION/g" \
      ./scripts/files/pyproject.sample.toml > pyproject.toml
      
  print_success "pyproject.toml file created."
}

function generate_docker_compose() {
  sed -e "s/\$PORT/$API_PORT/g" \
      -e "s/\$PROJECT_NAME/$PROJECT_NAME/g" \
      -e "s/\$HOST/$API_HOST/g" \
      ./scripts/files/docker-compose.sample.yml > docker-compose.yml
      
  print_success "docker-compose.yml file created."
}

function generate_dev_dockerfile() {
  mkdir -p dockerfiles
  sed -e "s/\$PORT/$API_PORT/g" \
      ./scripts/files/dev.dockerfile > ./dockerfiles/dev.dockerfile
      
  print_success "dev.dockerfile file created."
}

function create_files() {
  print_header "Creating Project Files"
  
  read_hamkee_api_config_file
  generate_pyproject_toml
  generate_docker_compose
  generate_dev_dockerfile
  
  echo
  print_info "Do you want to proceed with the installation? (\033[1my/n\033[0m)"
  read install_proceed
  if [ "$install_proceed" != "y" ]; then
    print_warning "Installation cancelled."
    exit 1
  fi
}

#-------------------------------------------------------
# Installation functions
#-------------------------------------------------------
function install_rye() {
  print_header "Installing Rye"
  
  if rye_installed; then
    print_success "Rye is already installed."
    return
  fi

  if ! command -v rye &> /dev/null; then
    print_step "Downloading and installing Rye..."
    curl -sSf https://rye-up.com/get | bash
    print_success "Rye installation completed."
  fi
}

function install_dependencies_with_rye() {
  print_header "Installing Dependencies"
  
  source "$HOME/.rye/env"

  # Be sure to have the python version installed
  print_step "Setting up Python $PYTHON_VERSION..."
  rye fetch "$PYTHON_VERSION"
  rye pin "$PYTHON_VERSION"

  print_step "Installing project dependencies..."
  rye sync
  rye add fastapi[standard] pydantic-settings httpx loguru hypercorn result 
  rye add --dev pytest pytest-mock pytest-cov pre-commit mkdocs-material mkdocs-material[imaging] 
  rye sync
  
  print_success "All dependencies installed successfully."
}

#-------------------------------------------------------
# Main script execution
#-------------------------------------------------------
clear

# Welcome message
print_divider
echo -e "\033[1;35m Welcome to Hamkee FastAPI Installation \033[0m"
print_divider
echo

# Check if .env file exists and echo a message to the user
if ! hamkee_api_config_file_exists; then
  print_error "Before proceeding, you must create an .env file with the project settings."
  print_info "You can use the provided env.file.example file as a template."
  echo
  exit 1
fi

# Show installation steps
print_header "Installation Overview"
print_info "This script will execute the following steps:"
echo
echo -e "1. \033[1mCreate these files\033[0m:"
echo -e "   - pyproject.toml" 
echo -e "   - docker-compose.yml"
echo -e "   - dev.dockerfile"

if ! rye_installed; then
  echo
  echo -e "2. \033[1mInstall Rye\033[0m:"
  echo -e "   - It will check if Rye is already installed. If not, it will install it."
  echo -e "   - Rye provides a unified experience to \033[1minstall and manage Python installations.\033[0m"
  echo -e "   - Learn more about Rye at https://rye-up.com/"
fi

echo

# Ask user if they want to proceed
print_info "Do you want to proceed? (\033[1my/n\033[0m)"
read install_proceed
if [ "$install_proceed" != "y" ]; then
  print_warning "Installation cancelled."
  exit 1
fi

# Check that .env file exists 
if ! hamkee_api_config_file_exists; then
  print_error "You must create a .env file, use provided 'env.file.example' file as a template."
  exit 1
fi

create_files

# Install Rye if needed
install_rye

# Check if 'rye' is installed, if not, quit the script
if ! rye_installed; then
  print_error "Rye is not installed. Please install it and try again."
  exit 1
fi 

install_dependencies_with_rye

# Final success message
print_header "Installation Complete"
print_success "All dependencies installed successfully!"
print_divider
print_info "Open a new terminal or run \033[1msource ~/.rye/env\033[0m"
print_info "Type \033[1mpython\033[0m and you'll get a Python interpreter running version $PYTHON_VERSION"
