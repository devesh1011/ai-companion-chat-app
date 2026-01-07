# AI Chat Application 💬

**What is this?** A real-time chat platform where users converse with AI characters powered by Google Gemini, built with microservices architecture.

**Why does it exist?** Demonstrates production-grade distributed systems patterns: event-driven architecture, message queues, caching, real-time WebSockets, and containerized deployments.

**Problem solved:** Handles scalable, real-time AI conversations with persistent state, async processing, and fault-tolerant message handling across independent services.

## Quick Start (2 minutes)

### Prerequisites

- Docker Desktop, Minikube, kubectl, Python 3.12+, Google API Key

### Run Locally

```bash
cd /Users/devesh1011/code_with_devesh/chat-app
minikube start
eval $(minikube docker-env)

# Build & deploy all services
./deploy.sh  # (create this script with all kubectl apply commands)

# Or manually:
cd src && for dir in auth chat-ws ai_character ai-consumer message-dispatcher gateway; do
  cd $dir && docker build -t deveshk237572/$dir:latest . && cd ..
done
cd ../.. && kubectl apply -f postgres/k8s && kubectl apply -f rabbit/k8s && kubectl apply -f redis/k8s
kubectl apply -f src/*/k8s
```

### Test the API

```bash
# Login
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=password123"

# Get characters
curl -X GET http://localhost:8000/characters \
  -H "Authorization: Bearer {access_token}"

# Connect WebSocket
ws://localhost:8004/ws/{character_id}?token={access_token}
# Send: {"content": "Hello!"}
```

## Architecture

**Frontend**: React + TypeScript (WebSocket client)
**Backend**: 6 microservices (FastAPI)

- **Gateway**: API routing & auth
- **Auth**: JWT token generation
- **Chat-WS**: WebSocket server, session management
- **AI Character**: Character data & prompts
- **AI Consumer**: LLM processing (RabbitMQ consumer)
- **Message Dispatcher**: Persistence & caching

**Data Flow**: User Message → WebSocket → RabbitMQ → AI Consumer → Gemini API → Message Dispatcher → PostgreSQL/Redis → Response to Client

## Tech Stack

| Layer              | Tech                                             |
| ------------------ | ------------------------------------------------ |
| **Frontend**       | React, TypeScript, WebSocket                     |
| **Backend**        | FastAPI, Python, Uvicorn                         |
| **Database**       | PostgreSQL 16                                    |
| **Queue**          | RabbitMQ                                         |
| **Cache**          | Redis                                            |
| **AI/LLM**         | Google Generative AI (Gemini 3-Flash), LangChain |
| **Infrastructure** | Kubernetes (Minikube), Docker                    |
| **Auth**           | JWT                                              |

## Services Detail

| Service            | Port | Purpose                               |
| ------------------ | ---- | ------------------------------------- |
| Gateway            | 8000 | API routing, auth, character listing  |
| Auth               | 3001 | JWT token generation & validation     |
| Chat-WS            | 8004 | WebSocket connections, session mgmt   |
| AI Character       | 3000 | Character data & system prompts       |
| AI Consumer        | -    | Gemini API calls, response generation |
| Message Dispatcher | -    | Persistence, caching, notification    |

## Key Design Patterns

- **Event-Driven**: RabbitMQ for decoupled async processing
- **Caching**: Redis for fast conversation history retrieval
- **Containerized**: All services in Docker, orchestrated by Kubernetes
- **Stateless**: Services can scale horizontally
- **Async-First**: FastAPI with asyncio for high concurrency

## Environment Setup

Set these in `k8s/configmap.yaml` files:

- `GOOGLE_API_KEY` - For Gemini AI
- `DATABASE_URL` - PostgreSQL connection
- `RABBITMQ_HOST`, `REDIS_HOST` - Infrastructure addresses

## Monitoring

```bash
# Check all pods
kubectl get pods

# View logs
kubectl logs -f deployment/gateway
kubectl logs -f deployment/chat-ws
kubectl logs -f deployment/ai-consumer

# RabbitMQ UI
kubectl port-forward svc/rabbitmq 15672:15672
# Visit http://localhost:15672 (guest/guest)
```

## Development

```bash
# Run individual service locally
cd src/gateway
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend
bun install
bun run dev
```

## License

MIT
