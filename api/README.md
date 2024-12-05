# RL Service API

A Flask API service with PostgreSQL backend for providing RL environment actions over specified time ranges.

## Prerequisites

- Python 3.8+
- Docker and Docker Compose
- pip (Python package installer)

## Quick Start

1. **Python virtual environment setup**
Navigate back to root folder, read readme and do as it says

2. **Environment variables setup**
   ```bash
   # Copy and configure environment variables
   cp .env.example .env
   ```

   Ensure mainnet is chosen in .env, if not you have to deploy the model manually and upload it.

3. **Database Setup**
   ```bash
   # Start PostgreSQL and PgAdmin
   docker-compose up -d

   # Initialize database schema
   flask db init
   flask db upgrade
   ```

4. **Run the API**
   ```bash
   flask run
   ```
   Access the API at http://localhost:5000

## Database Configuration

### PostgreSQL
- Host: localhost
- Port: 5432
- Database: docker
- Username: docker
- Password: docker

### PgAdmin
- URL: http://localhost:8080
- Email: admin@example.com
- Password: admin

## Database Management (not essential until developing)

### Creating Migrations
```bash
# Generate migration after model changes
flask db migrate -m "description"

# Apply the migration
flask db upgrade
```

### Rollback Changes
```bash
flask db downgrade
```

## Troubleshooting

1. **Database Connection Issues**
   - Ensure Docker containers are running: `docker ps`
   - Check PostgreSQL logs: `docker logs <postgres-container-id>`
   - Verify `.env` database credentials match Docker Compose settings

2. **Migration Issues**
   - If `flask db upgrade` fails, ensure you've run `flask db init` first
   - Check if migrations directory exists
   - Verify database connection settings

3. **Connecting with Pgadmin**
   - Ensure the host is called the same as container defined inside compose configuration, this will be **postgres** for current configuration

## Development Notes

- The API runs in debug mode by default for development
- Use PgAdmin for database inspection and manual queries
- Always run migrations after pulling new changes
- Keep your virtual environment activated while working



