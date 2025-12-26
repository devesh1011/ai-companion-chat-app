# Chat Application - AI-Powered Real-Time Chat System

A microservices-based real-time chat application that integrates AI characters. Users can have conversations with AI-powered characters in real-time using WebSockets.

## Architecture Overview

![System Architecture](Screenshot 2025-12-26 at 10.15.38 PM.png)

## Services

### 1. **Gateway** (API Gateway)

- **Port**: 8000
- **Purpose**: Single entry point for all client requests
- **Routes**:
  - `POST /login` - User authentication
  - `POST /register` - User registration
  - `GET /characters` - List available AI characters
  - `GET /characters/id/{char_id}` - Get character details

### 2. **Auth Service**

- **Port**: 3001
- **Purpose**: JWT token generation and validation
- **Endpoints**:
  - `POST /token` - Login with username/password
  - `POST /register` - Register new user
  - `POST /validate` - Validate JWT token
- **Database**: PostgreSQL

### 3. **Chat WebSocket Service** (chat-ws)

- **Port**: 8004
- **Purpose**: Real-time bidirectional communication via WebSocket
- **Endpoints**:
  - `WS /ws/{character_id}?token={jwt_token}` - WebSocket connection
  - `GET /health` - Health check
- **Flow**:
  1. Accepts WebSocket connection with JWT token
  2. Creates chat session in PostgreSQL
  3. Publishes user messages to RabbitMQ (`chat.user.msg` queue)
  4. Stores messages in PostgreSQL and Redis
  5. Sends echo response back to client

### 4. **AI Character Service**

- **Port**: 3000
- **Purpose**: Manage AI character data and prompts
- **Endpoints**:
  - `GET /api/characters` - List all characters
  - `GET /api/characters/id/{character_id}` - Get character details
  - `POST /api/characters` - Create new character
- **Database**: PostgreSQL

### 5. **AI Consumer**

- **Purpose**: Processes user messages and generates AI responses
- **Flow**:
  1. Listens to RabbitMQ `chat.user.msg` queue
  2. Fetches AI character's system prompt
  3. Retrieves conversation history from Redis/PostgreSQL
  4. Calls Google Generative AI (Gemini) for response
  5. Publishes response to `chat.ai.msg` queue
- **Uses**: LangChain + Google Generative AI

### 6. **Message Dispatcher**

- **Purpose**: Persists AI responses and maintains conversation cache
- **Flow**:
  1. Listens to RabbitMQ `chat.ai.msg` queue
  2. Saves AI message to PostgreSQL
  3. Stores message in Redis for fast access
- **Database**: PostgreSQL, Redis

## Technology Stack

- **Backend Framework**: FastAPI, Uvicorn
- **Database**: PostgreSQL 16
- **Message Queue**: RabbitMQ
- **Cache**: Redis
- **Real-time**: WebSocket
- **AI/LLM**: LangChain + Google Generative AI (Gemini 3-Flash)
- **Container Orchestration**: Kubernetes (Minikube)
- **Container Runtime**: Docker
- **Async**: aio-pika, asyncio
- **Authentication**: JWT

## Prerequisites

- Docker Desktop
- Minikube (for local K8s deployment)
- kubectl
- Python 3.12+
- Google API Key (for Gemini AI)

## Getting Started

### 1. Clone and Setup

```bash
cd /Users/devesh1011/code_with_devesh/chat-app
```

### 2. Start Minikube

```bash
minikube start
eval $(minikube docker-env)
```

### 3. Build and Push Docker Images

```bash
# Build all services
cd src/auth && docker build -t deveshk237572/auth:latest .
cd ../chat-ws && docker build -t deveshk237572/chat-ws:latest .
cd ../ai_character && docker build -t deveshk237572/ai-character:latest .
cd ../ai-consumer && docker build -t deveshk237572/ai-consumer:latest .
cd ../message-dispatcher && docker build -t deveshk237572/message-dispatcher:latest .
cd ../gateway && docker build -t deveshk237572/gateway:latest .

# Push to registry (or use local images)
docker push deveshk237572/auth:latest
docker push deveshk237572/chat-ws:latest
docker push deveshk237572/ai-character:latest
docker push deveshk237572/ai-consumer:latest
docker push deveshk237572/message-dispatcher:latest
docker push deveshk237572/gateway:latest
```

### 4. Deploy Infrastructure

```bash
# PostgreSQL
cd postgres/k8s
kubectl apply -f .

# RabbitMQ
cd ../../rabbit/k8s
kubectl apply -f .

# Redis
cd ../../redis/k8s
kubectl apply -f .

# Wait for infrastructure to be ready
kubectl get pods
```

### 5. Deploy Services

```bash
# Auth Service
cd src/auth/k8s
kubectl apply -f .

# AI Character Service
cd ../../ai_character/k8s
kubectl apply -f .

# Chat WebSocket Service
cd ../../chat-ws/k8s
kubectl apply -f .

# AI Consumer
cd ../../ai-consumer/k8s
kubectl apply -f .

# Message Dispatcher
cd ../../message-dispatcher/k8s
kubectl apply -f .

# Gateway
cd ../../gateway/k8s
kubectl apply -f .
```

### 6. Verify Deployment

```bash
kubectl get pods
kubectl get svc

# Check logs
kubectl logs deployment/gateway
kubectl logs deployment/chat-ws -f
kubectl logs deployment/ai-consumer -f
```

## API Usage

### 1. Register User

```bash
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "name": "Test User",
    "password": "password123"
  }'
```

### 2. Login

```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=password123"
```

Response:

```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

### 3. Get Available Characters

```bash
curl -X GET http://localhost:8000/characters \
  -H "Authorization: Bearer {access_token}"
```

### 4. Connect to WebSocket

```bash
# Using wscat or Postman WebSocket feature
ws://localhost:8004/ws/{character_id}?token={access_token}

# Send message
{
  "content": "Hello, Tony Stark!"
}

# Receive responses
{
  "type": "connection",
  "message": "Connected to chat",
  "session_id": "...",
  "username": "testuser",
  "character_id": "..."
}

{
  "type": "echo",
  "role": "user",
  "content": "Hello, Tony Stark!",
  "timestamp": "..."
}

{
  "role": "ai",
  "content": "AI response from character..."
}
```

## Environment Variables

### Chat-WS (`src/chat-ws/k8s/configmap.yaml`)

```yaml
DB_HOST: postgres-headless
DB_PORT: 5432
DB_NAME: chat_db
RABBITMQ_HOST: rabbitmq-headless
REDIS_HOST: redis
REDIS_PORT: 6379
AUTH_SVC_ADDR: ai-companion-auth-service:3001
```

### AI-Consumer (`src/ai-consumer/k8s/configmap.yaml`)

```yaml
DATABASE_URL: postgresql+psycopg2://chat_user:chat_password@postgres-headless:5432/chat_db
AI_CHAR_SVC_ADDR: ai-character-service:3000
QUEUE_NAME: chat.user.msg
RABBITMQ_HOST: rabbitmq-headless
REDIS_HOST: redis
REDIS_PORT: 6379
```

## Message Flow

1. **User sends message via WebSocket**

   - Chat-WS receives message
   - Stores in PostgreSQL (messages table)
   - Caches in Redis
   - Publishes to RabbitMQ `chat.user.msg` queue
   - Echoes back to user

2. **AI Consumer processes**

   - Consumes from `chat.user.msg` queue
   - Fetches character's system prompt
   - Retrieves conversation history
   - Calls Gemini API for response
   - Publishes to `chat.ai.msg` queue

3. **Message Dispatcher persists**
   - Consumes from `chat.ai.msg` queue
   - Saves AI response to PostgreSQL
   - Stores in Redis for fast retrieval
   - Sends the message to Websocket server using gRPC

## Database Schema

### Messages Table

```sql
CREATE TABLE messages (
  id UUID PRIMARY KEY,
  username VARCHAR NOT NULL,
  character_id UUID NOT NULL,
  session_id UUID NOT NULL,
  content TEXT NOT NULL,
  role VARCHAR NOT NULL, -- 'user' or 'ai'
  created_at TIMESTAMP WITH TIME ZONE,
  updated_at TIMESTAMP WITH TIME ZONE,
  INDEX idx_user_character (username, character_id),
  INDEX idx_session_messages (session_id),
  INDEX idx_message_role (role)
);
```

### ChatSession Table

```sql
CREATE TABLE chat_sessions (
  id UUID PRIMARY KEY,
  username VARCHAR NOT NULL,
  character_id UUID NOT NULL,
  status VARCHAR NOT NULL, -- 'ACTIVE' or 'CLOSED'
  created_at TIMESTAMP WITH TIME ZONE,
  updated_at TIMESTAMP WITH TIME ZONE
);
```

## Monitoring

### View Pod Logs

```bash
# Gateway
kubectl logs deployment/gateway -f

# Chat WebSocket Service
kubectl logs deployment/chat-ws -f

# AI Consumer
kubectl logs deployment/ai-consumer -f

# Message Dispatcher
kubectl logs deployment/message-dispatcher -f
```

### RabbitMQ Management UI

```bash
kubectl port-forward svc/rabbitmq 15672:15672
# Visit http://localhost:15672
# Username: guest, Password: guest
```

### Check Queue Status

```bash
kubectl exec -it rabbitmq-0 -- rabbitmqctl list_queues name messages consumers
```

## Troubleshooting

### Messages not being consumed

1. Check if RabbitMQ connection is alive
2. Verify queue binding: `kubectl exec -it rabbitmq-0 -- rabbitmqctl list_bindings`
3. Check consumer logs for connection errors

### WebSocket connection fails

1. Verify JWT token is valid
2. Check chat-ws pod logs
3. Ensure auth service is running

### AI responses not generating

1. Check Google API key is set correctly
2. Verify ai-consumer pod is running
3. Check RabbitMQ message queue
4. Review ai-consumer logs

### Database connection errors

1. Verify PostgreSQL pod is running
2. Check database credentials in configmaps
3. Ensure database is initialized

## License

MIT
