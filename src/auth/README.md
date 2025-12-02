# Auth Service

## Overview

The Auth Service is a microservice component of the AI Chat Application that handles user authentication and authorization. It provides secure user registration, login functionality, and JWT token management for the entire application ecosystem.

This service is built with FastAPI and uses PostgreSQL as its database, with SQLAlchemy as the ORM. It integrates with other services in the chat application through the API Gateway.

## Features

- **User Registration**: Create new user accounts with secure password hashing
- **User Login**: Authenticate users and issue JWT access tokens
- **Token Validation**: Verify JWT tokens for protected endpoints
- **Password Security**: Uses Argon2 password hashing for enhanced security
- **Database Integration**: PostgreSQL with automatic table creation
- **FastAPI Framework**: High-performance async API with automatic OpenAPI documentation

## API Endpoints

### POST /register

Register a new user account.

**Request Body:**

```json
{
  "name": "string",
  "username": "string",
  "password": "string"
}
```

**Response (201 Created):**

```json
{
  "id": 1,
  "name": "string",
  "username": "string"
}
```

**Error Responses:**

- 409 Conflict: User already exists
- 500 Internal Server Error: Database error

### POST /token

Authenticate user and return JWT access token.

**Request Body (OAuth2 Form):**

```
username: string
password: string
```

**Response (200 OK):**

```json
{
  "access_token": "string",
  "token_type": "bearer"
}
```

**Error Response:**

- 401 Unauthorized: Incorrect username or password

### POST /validate

Validate a JWT token and return user information.

**Authorization:** Bearer token required

**Response (200 OK):**

```json
{
  "username": "string",
  "valid": true
}
```

**Error Response:**

- 401 Unauthorized: Invalid token

## Installation

### Prerequisites

- Python 3.12+
- PostgreSQL database
- Docker (for containerized deployment)

### Local Development Setup

1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   cd chat-app/src/auth
   ```

2. **Create virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables:**
   Create a `.env` file or export environment variables:

   ```bash
   export DB_HOST=localhost
   export DB_PORT=5432
   export DB_USER=postgres
   export DB_PASSWORD=your_password
   export DB_NAME=auth_db
   export JWT_SECRET=your_jwt_secret_key
   export ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

5. **Run the service:**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8001
   ```

### Docker Deployment

The service includes a Dockerfile for containerized deployment. Use Docker Compose from the project root:

```bash
cd ../..
docker-compose up auth
```

## Configuration

The service uses the following environment variables:

| Variable                      | Default         | Description                      |
| ----------------------------- | --------------- | -------------------------------- |
| `DB_HOST`                     | localhost       | PostgreSQL host                  |
| `DB_PORT`                     | 5432            | PostgreSQL port                  |
| `DB_USER`                     | postgres        | Database username                |
| `DB_PASSWORD`                 | haunted97!      | Database password                |
| `DB_NAME`                     | postgres        | Database name                    |
| `JWT_SECRET`                  | (random string) | Secret key for JWT signing       |
| `ALGORITHM`                   | HS256           | JWT algorithm                    |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 30              | Token expiration time in minutes |

## Dependencies

- **FastAPI**: Web framework
- **SQLAlchemy**: Database ORM
- **psycopg2-binary**: PostgreSQL driver
- **PyJWT**: JWT token handling
- **PassLib/PwdLib**: Password hashing with Argon2
- **Pydantic**: Data validation
- **Uvicorn**: ASGI server

## Development

### API Documentation

When running locally, visit `http://localhost:8001/docs` for interactive Swagger UI documentation.

### Database Migrations

The service uses SQLAlchemy with automatic table creation on startup. For production deployments, consider using Alembic for proper migration management.

### Testing

Add unit tests in a `tests/` directory using pytest.

## Integration

This service integrates with:

- **API Gateway**: Routes authentication requests
- **Chat Services**: Validates user tokens for WebSocket connections
- **AI Character Service**: Ensures authenticated access to character management

## Security Considerations

- JWT tokens expire after 30 minutes by default
- Passwords are hashed using Argon2
- Database connections use secure credentials
- Input validation through Pydantic models
- CORS and security headers should be configured in production

## Contributing

1. Follow the project's coding standards
2. Add tests for new features
3. Update documentation for API changes
4. Ensure all dependencies are properly versioned

## License

[Add license information here]
