# Redis Kubernetes Deployment

This directory contains Kubernetes configuration files for deploying Redis.

## Components

- **StatefulSet** (`statefulset.yaml`): Defines the Redis container with persistence
- **Service** (`service.yaml`): Headless service for Redis discovery
- **Secret** (`secret.yaml`): Stores the Redis password

## Deployment

```bash
kubectl apply -f ./redis/k8s/
```

## Configuration

### Default Values

- **Image**: redis:7-alpine
- **Port**: 6379
- **Storage**: 5Gi PVC
- **Authentication**: None (password disabled)
- **Memory Limits**: 256Mi max, 128Mi request
- **AOF**: Enabled for persistence

## Connection

From within the cluster, connect using:

```
redis://redis:6379
```

## Verification

Check if Redis is running:

```bash
kubectl get pods -l app=redis
kubectl exec -it redis-0 -- redis-cli ping
```

Expected output: `PONG`
