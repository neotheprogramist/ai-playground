# AI Model Deployment System

This project consists of two main components:
- A Flask API service with PostgreSQL backend
- An Internet Computer Protocol (ICP) canister for model hosting

## Setup & Installation

1. **Install for relative imports**
```bash
pip install -e .
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

## Components

### 1. API Service
The API service provides endpoints for model inference and data management. To set up and run:

1. Navigate to the `api/` directory
2. Follow the setup instructions in `api/README.md`, including:
   - Setting up environment variables
   - Starting PostgreSQL with Docker
   - **Important**: Running database migrations to set up the schema
   - Starting the Flask server

> ⚠️ **Note**: After starting PostgreSQL with Docker, you must run the database migrations 
> to create the required schema structure. Without this step, the API won't work properly.

### 2. ICP Canister
The ICP canister handles model hosting on the Internet Computer. To deploy:

1. Navigate to `icp-canister/` directory
2. Follow the setup instructions in `icp-canister/README.md`, including:
   - Starting the local replica
   - Deploying the canister
   - Uploading your model

## Development

For development instructions, refer to the respective README files in each component's directory.
