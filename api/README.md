# RL service 

This service provides a Flask API with PostgreSQL database backend, allowing to provide actions for some time range using some default RL
environment.

## Prerequisites

- Python 3.8+
- Docker and Docker Compose
- pip (Python package installer)

## Setup Instructions

1. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Start PostgreSQL using Docker**:
   ```bash
   docker-compose up -d
   ```
   This will start:
   - PostgreSQL on port 5432
   - PgAdmin on port 8080 (accessible at http://localhost:8080)

4. **Database migrations**:
   ```bash
   flask db upgrade
   ```
   This will create all necessary database tables.

5. **Run the Flask application**:
   ```bash
   flask run
   ```
   The API will be available at http://localhost:5000

## Database access

### PostgreSQL default connection details
- Host: localhost
- Port: 5432
- Database: docker
- Username: docker
- Password: docker

### PgAdmin default access
- URL: http://localhost:8080
- Email: admin@example.com
- Password: admin

## Development

### Creating new migrations

When you make changes to database models, create a new migration:
  ```bash
  flask db migrate -m "description"

  flask db upgrade
  ```

### Rolling back migrations

To undo the last migration:
  ```bash
  flask db downgrade
  ```



