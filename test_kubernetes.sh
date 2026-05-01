#!/bin/bash

echo "🎯 KUBERNETES LOCAL TESTING"
echo "============================"
echo ""

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed"
    echo "Install it with: sudo snap install kubectl --classic"
    exit 1
fi

# Check if minikube is installed
if ! command -v minikube &> /dev/null; then
    echo "❌ minikube is not installed"
    echo "Install it with:"
    echo "  curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64"
    echo "  sudo install minikube-linux-amd64 /usr/local/bin/minikube"
    exit 1
fi

echo "✅ Prerequisites installed"
echo ""

# Start Minikube if not running
echo "📋 Checking Minikube status..."
if ! minikube status &> /dev/null; then
    echo "🚀 Starting Minikube..."
    minikube start --driver=docker
else
    echo "✅ Minikube is already running"
fi

# Enable ingress
echo "📋 Enabling ingress addon..."
minikube addons enable ingress

# Point Docker to Minikube
echo "📋 Configuring Docker for Minikube..."
eval $(minikube docker-env)

# Build images
echo "🔨 Building Docker images..."
cd backend
docker build -t attendance-backend:latest .
cd ..

cd frontend
docker build -t attendance-frontend:latest .
cd ..

# Create local k8s directory
echo "📋 Preparing Kubernetes manifests..."
mkdir -p k8s-local
cp k8s/*.yaml k8s-local/

# Update for local deployment
sed -i 's/imagePullPolicy: Always/imagePullPolicy: Never/g' k8s-local/backend-deployment.yaml
sed -i 's/imagePullPolicy: Always/imagePullPolicy: Never/g' k8s-local/frontend-deployment.yaml
sed -i 's|image: .*attendance-backend.*|image: attendance-backend:latest|g' k8s-local/backend-deployment.yaml
sed -i 's|image: .*attendance-frontend.*|image: attendance-frontend:latest|g' k8s-local/frontend-deployment.yaml

# Deploy to Kubernetes
echo "🚀 Deploying to Kubernetes..."
kubectl apply -f k8s-local/namespace.yaml
kubectl apply -f k8s-local/secrets.yaml
kubectl apply -f k8s-local/configmap.yaml
kubectl apply -f k8s-local/postgres-pvc.yaml
kubectl apply -f k8s-local/postgres-deployment.yaml
kubectl apply -f k8s-local/backend-deployment.yaml
kubectl apply -f k8s-local/frontend-deployment.yaml

# Wait for deployments
echo "⏳ Waiting for deployments to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/attendance-backend -n attendance-system
kubectl wait --for=condition=available --timeout=300s deployment/attendance-frontend -n attendance-system

# Test deployments
echo ""
echo "============================"
echo "✅ KUBERNETES TESTS"
echo "============================"
echo ""

# Test 1: Check pods
echo "📋 Test 1: Checking pods..."
pods_running=$(kubectl get pods -n attendance-system --no-headers | grep Running | wc -l)
if [ "$pods_running" -ge 2 ]; then
    echo "✅ All pods are running ($pods_running pods)"
else
    echo "❌ Some pods are not running"
    kubectl get pods -n attendance-system
    exit 1
fi

# Test 2: Check services
echo ""
echo "📋 Test 2: Checking services..."
services=$(kubectl get services -n attendance-system --no-headers | wc -l)
if [ "$services" -ge 2 ]; then
    echo "✅ All services are created ($services services)"
else
    echo "❌ Services are missing"
    kubectl get services -n attendance-system
    exit 1
fi

# Test 3: Test backend API
echo ""
echo "📋 Test 3: Testing backend API..."
kubectl port-forward -n attendance-system service/backend-service 8000:8000 &
PORT_FORWARD_PID=$!
sleep 5

response=$(curl -s http://localhost:8000)
if [[ $response == *"Welcome"* ]]; then
    echo "✅ Backend API is responding"
else
    echo "❌ Backend API is not responding"
fi

kill $PORT_FORWARD_PID 2>/dev/null

# Test 4: Check logs
echo ""
echo "📋 Test 4: Checking logs for errors..."
backend_pod=$(kubectl get pods -n attendance-system -l app=attendance-backend -o jsonpath='{.items[0].metadata.name}')
errors=$(kubectl logs $backend_pod -n attendance-system | grep -i "error" | grep -v "ERROR" | wc -l)
if [ "$errors" -eq 0 ]; then
    echo "✅ No errors in backend logs"
else
    echo "⚠️  Found $errors errors in logs"
fi

# Summary
echo ""
echo "============================"
echo "🎉 KUBERNETES TESTS COMPLETE!"
echo "============================"
echo ""
echo "📊 Cluster Information:"
kubectl get nodes
echo ""
echo "📋 Pods Status:"
kubectl get pods -n attendance-system
echo ""
echo "📋 Services:"
kubectl get services -n attendance-system
echo ""
echo "🌐 To access the application:"
echo "   1. Run: minikube tunnel (in a separate terminal)"
echo "   2. Or use port forwarding:"
echo "      kubectl port-forward -n attendance-system service/frontend-service 8080:80"
echo "      kubectl port-forward -n attendance-system service/backend-service 8000:8000"
echo ""
echo "📋 Useful commands:"
echo "   kubectl get all -n attendance-system"
echo "   kubectl logs -f deployment/attendance-backend -n attendance-system"
echo "   kubectl describe pod <pod-name> -n attendance-system"
echo "   minikube dashboard"
echo ""
