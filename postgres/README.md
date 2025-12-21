# PostgreSQL for Kubernetes

Complete PostgreSQL deployment manifests for the AI Chat Application.

## Structure

```
postgres/
├── k8s/                         # Kubernetes manifests
│   ├── postgres-deployment.yaml # Deployment, Service, and PVC
│   ├── postgres-secret.yaml     # Database credentials
│   ├── postgres-configmap.yaml  # Configuration
│   └── README.md               # Deployment instructions
└── README.md                   # This file
```

## Quick Start

```bash
# Deploy PostgreSQL to chat-app namespace
cd k8s
kubectl apply -f .
```

## Namespace Requirement

PostgreSQL is deployed in the `chat-app` namespace. Ensure the namespace exists:

```bash
kubectl create namespace chat-app
```

Or use the namespace manifest:

```bash
kubectl apply -f ../k8s/namespace.yaml
```
