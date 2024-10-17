# Referral System API

API with JWT / Google OAuth2 authentication and a referral system.

## Tech Stack

- **Backend Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Database**: [PostgreSQL](https://www.postgresql.org/)
- **Caching**: [Redis](https://redis.io/)
- **Containerization**: [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/)
- **Migrations**: [Alembic](https://alembic.sqlalchemy.org/)
- **ORM**: [SQLAlchemy](https://www.sqlalchemy.org/)
- **Validation and Serialization**: [Pydantic](https://pydantic-docs.helpmanual.io/)
- **Testing**: [pytest](https://pytest.org/)
- **Asynchronous Programming**: Fully asynchronous implementation

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/sxw111/referral-system-api.git
   cd referral-system-api
   ```

2. Edit the `.env` file by adding your data.

3. Build and Run the Docker Containers:

   ```bash
   docker-compose up --build
   ```

4. Open your browser and go to http://localhost:8000/docs to view the Swagger documentation and interact with the API.

## Project Structure

```shell
.vscode/
├── settings.json                       # VSCode settings
app/
├── auth/
    ├── google_auth.py                  # Google OAuth authentication endpoints and setup
    ├── models.py                       # User SQLAlchemy and Pydantic models
    ├── service.py                      # Business logic for authentication and user operations
    ├── views.py                        # API endpoints for authentication and user management
├── database/
    ├── core.py                         # Core database connection and setup
├── jwt/
    ├── models.py                       # Pydantic models related to JWT handling
├── referrals/
    ├── models.py                       # Referrals Pydantic models
    ├── service.py                      # Business logic for referral system operations
    ├── utils.py                        # Utility functions for the referral system
    ├── views.py                        # API endpoints for referral system management
├── api.py                              # Defines the main router and includes all application routers
├── config.py                           # Configuration settings for the application, including environment variables and application metadata
├── exceptions.py                       # Custom exception classes for error handling
├── main.py                             # Entry point for the FastAPI application
├── models.py                           # Base class for Pydantic models with custom configuration
├── security.py                         # Security-related functions
migrations/                             # Alembic migrations
.dockerignore                           # Excludes unnecessary files and directories from Docker image builds
.env                                    # File for storing sensitive environment variables
.flake8                                 # Configuration file for Flake8 code linter
.gitattributes                          # Configuration file for specifying attributes for Git repositories
.gitignore                              # File specifying files and directories Git should ignore
.pre-commit-config.yaml                 # Configuration file for managing pre-commit hooks to automate code checks and formatting
Dockerfile                              # Script defining steps to create a Docker image
LICENSE                                 # File containing terms and conditions for software usage and distribution
README.md                               # Project overview and instructions for users and developers
alembic.ini                             # Configuration file for Alembic database migrations
docker-compose.yml                      # Configuration file for Docker Compose
poetry.lock                             # Automatically generated file containing locked dependencies for Poetry
pyproject.toml                          # Configuration file for Python projects, specifying project metadata and dependencies
```

## Contributing

Your contributions are appreciated! Fork the repository, open issues, and submit pull requests.