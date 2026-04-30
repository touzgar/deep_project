#!/bin/bash

# Deploy to Kubernetes
# Usage: ./scripts/deploy-k8s.sh

echo "Deploying to Kubernetes..."

# Create namespace
echo "Creating namespace..."
kubectl apply -f k8s/namespace.yaml

# Apply secrets and config
echo "Applying secrets and config..."
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/configmap.yaml

# Deploy database
echo "Deploying PostgreSQL..."
kubectl apply -f k8s/postgres-pvc.yaml
kubectl apply -f k8s/postgres-deployment.yaml

# Wait for database to be ready
echo "Waiting for PostgreSQL to be ready..."
kubectl wait --for=condition=ready pod -l app=postgres -n attendance-system --timeout=300s

# Deploy backend
echo "Deploying backend..."
kubectl apply -f k8s/backend-deployment.yaml

# Wait for backend to be ready
echo "Waiting for backend to be ready..."
kubectl wait --for=condition=ready pod -l app=backend -n attendance-system --timeout=300s

# Deploy frontend
echo "Deploying frontend..."
kubectl apply -f k8s/frontend-deployment.yaml

# Apply ingress
echo "Applying ingress..."
kubectl apply -f k8s/ingress.yaml

# Apply HPA
echo "Applying horizontal pod autoscalers..."
kubectl apply -f k8s/hpa.yaml

echo ""
echo "Deployment complete!"
echo ""
echo "Check status with:"
echo "  kubectl get pods -n attendance-system"
echo "  kubectl get services -n attendance-system"
echo "  kubectl get ingress -n attendance-system"
