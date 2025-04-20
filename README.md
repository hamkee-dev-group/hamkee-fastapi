# Hamkee API

**Hamkee API** is a powerful scaffolding tool designed to help developers quickly and easily start implementing an API using **FastAPI**.

## Overview

Starting a new **FastAPI** project often involves repetitive tasks such as setting up a logger, managing environment variables, and configuring HTTP clients for third-party services. **Hamkee API** aims to streamline these tasks, allowing you to focus on writing your API endpoints and business logic from the outset.

## Features

- **Predefined Directory Structure**: Provides a well-organized directory structure to manage your code efficiently.
- **Batteries Included**: Comes with reusable services that offer generic functionalities commonly needed in API development.
- **Python Interpreter Management**: Automatically handles everything related to the Python interpreter. Specify your desired Python version or let **Hamkee API** select one for you.
- **Docker Integration**: Generates Docker and Docker Compose files for containerized deployment, complete with hot-reloading for seamless development.
- **Dependency Management**: Simplifies managing dependencies and third-party libraries using [Rye](https://rye.astral.sh/).

## Getting Started

### Prerequisites

- Python 3.9+ 
- [Rye](https://rye.astral.sh/) (for dependency management)
- Docker and Docker Compose (optional, for containerized deployment)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/hamkee-dev-group/hamkee-fastapi.git
   cd hamkee-fastapi
   ```

2. Set up the project environment:
   ```bash
   ./scripts/devel/install.sh
   ```

   You should see something like:
   ```bash
        ----------------------------------------
        Welcome to Hamkee FastAPI Installation 
        ----------------------------------------


        ==== Installation Overview ====

        ℹ This script will execute the following steps:

        1. Create these files:
        - pyproject.toml
        - docker-compose.yml
        - dev.dockerfile

        ℹ Do you want to proceed? (y/n)
        y

        ==== Creating Project Files ====

        ✓ pyproject.toml file created.
        ✓ docker-compose.yml file created.
        ✓ dev.dockerfile file created.

        ℹ Do you want to proceed with the installation? (y/n)
        y

        ==== Installing Rye ====

        ✓ Rye is already installed.

        ==== Installing Dependencies ====

        → Setting up Python 3.12...
   ```

### Project Structure

```
hamkee-fastapi/
├── app/
│   ├── api/                 # API routes
│   ├── core/                # Core functionality and config
│   ├── models/              # Pydantic models
│   ├── services/            # Shared services
│   └── main.py              # Application entry point
├── tests/                   # Test directory
├── docker/                  # Docker configuration
├── pyproject.toml           # Python project configuration
└── README.md                # This file
```

## Usage

### Starting the API Locally

```bash
rye run uvicorn app.main:app --reload
```

### Using Docker

```bash
docker-compose up -d
```

The API will be available at `http://localhost:8000`.

### API Documentation

Once the server is running, you can access the interactive API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Configuration

Hamkee API uses environment variables for configuration. Create a `.env` file in the project root:

```
DEBUG=True
LOG_LEVEL=INFO
DATABASE_URL=postgresql://user:password@localhost/dbname
API_KEY=your_api_key_here
```

## Development Workflow

1. Create new endpoints in the `app/api/` directory
2. Define models in `app/models/`
3. Implement business logic in `app/services/`
4. Add tests in the `tests/` directory
5. Run tests with `rye run pytest`

## Contributing

We welcome contributions from the community! Here's how you can contribute:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -am 'Add new feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Submit a pull request

## License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0). See the [LICENSE](LICENSE) file for details.

The AGPL license ensures that anyone who uses this software over a network must make the source code available to users of that network.

## Contact

For questions or support, please open an issue on our [GitHub repository](https://github.com/yourusername/hamkee-fastapi/issues).
