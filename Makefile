.PHONY: start start-docker test add-dependency list-dependencies reinstall help

# Default target
help:
	@echo "Hamkee FastAPI Development Commands"
	@echo "----------------------------------"
	@echo "make start          - Start the FastAPI server locally"
	@echo "make start-docker   - Start the FastAPI server using Docker"
	@echo "make test           - Run all tests"
	@echo "make add-dependency DEP=package_name - Add a new Python dependency"
	@echo "make list-dependencies - Show all installed Python dependencies"
	@echo "make reinstall      - Reinstall everything from scratch"

# Start the project locally
start:
	@echo "Starting FastAPI server locally..."
	PYTHONPATH=`pwd`/app rye run fastapi run app/main.py

# Start the project with Docker
start-docker:
	@echo "Starting FastAPI server with Docker..."
	docker compose -f docker-compose.yml up

# Run all tests
test:
	@echo "Running tests..."
	rye run pytest

# Add a new dependency (usage: make add-dependency DEP=package_name)
add-dependency:
	@if [ -z "$(DEP)" ]; then \
		echo "Error: Please specify a dependency. Example: make add-dependency DEP=requests"; \
		exit 1; \
	fi
	@echo "Adding dependency: $(DEP)..."
	rye add $(DEP)

# Show all installed Python dependencies
list-dependencies:
	@echo "Listing all dependencies..."
	rye list

# Reinstall everything from scratch
reinstall:
	@echo "Reinstalling everything from scratch..."
	./scripts/devel/install.sh
