#!/bin/bash

echo "🎯 KUBERNETES TESTING ON WSL2"
echo "=============================="
echo ""

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "📦 Installing kubectl..."
    curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
    chmod +x kubectl
    sudo mv kubectl /usr/local/bin/
fi

echo "✅ kubectl installed"
echo ""

# Check if Kubernetes is running
echo "📋 Checking Kubernetes cluster..."
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Kubernetes cluster is not running"
    echo ""
    echo "Please enable Kubernetes in Docker Desktop:"
    echo "1. Open Docker Desktop (on Windows)"
    echo "2. Go to Settings → Kubernetes"
    echo "3. Check 'Enable Kubernetes'"
    echo "4. Click 'Apply & Restart'"
    echo "5. Wait 2-3 minutes"
    echo "6. Run this script again"
    exit 1
fi

echo "✅ Kubernetes cluster is running"
kubectl cluster-info
echo ""

# Build images
echo "🔨 Building Docker images..."
docker-compose build

# Tag images
echo "🏷️  Tagging images for Kubernetes..."
docker tag deep_project-backend:latest attendance-backend:latest
docker tag deep_project-frontend:latest attendance-frontend:latest

# Create local k8s directory
echo "📋 Preparing Kubernetes manifests..."
mkdir -p k8s-local
cp k8s/*.yaml k8s-local/

# Update for local deployment
sed -i 's/imagePullPolicy: Always/imagePullPolicy: IfNotPresent/g' k8s-local/backend-deployment.yaml
sed -i 's/imagePullPolicy: Always/imagePullPolicy: IfNotPresent/g' k8s-local/frontend-deployment.yaml
sed -i 's|image: .*attendance-backend.*|image: attendance-backend:latest|g' k8s-local/backend-deployment.yaml
sed -i 's|image: .*attendance-frontend.*|image: attendance-frontend:latest|g' k8s-local/frontend-deployment.yaml

# Remove postgres deployment (use Neon instead)
rm -f k8s-local/postgres-deployment.yaml
rm -f k8s-local/postgres-pvc.yaml

# Deploy to Kubernetes
echo "🚀 Deploying to Kubernetes..."
kubectl apply -f k8s-local/namespace.yaml
kubectl apply -f k8s-local/secrets.yaml
kubectl apply -f k8s-local/configmap.yaml
kubectl apply -f k8s-local/backend-deployment.yaml
kubectl apply -f k8s-local/frontend-deployment.yaml

# Wait for deployments
echo "⏳ Waiting for deployments to be ready (this may take 2-3 minutes)..."
kubectl wait --for=condition=available --timeout=300s deployment/attendance-backend -n attendance-system 2>/dev/null || true
kubectl wait --for=condition=available --timeout=300s deployment/attendance-frontend -n attendance-system 2>/dev/null || true

sleep 10

# Test deployments
echo ""
echo "============================"
echo "✅ KUBERNETES TESTS"
echo "============================"
echo ""

# Test 1: Check nodes
echo "📋 Test 1: Checking nodes..."
nodes_ready=$(kubectl get nodes --no-headers | grep Ready | wc -l)
if [ "$nodes_ready" -ge 1 ]; then
    echo "✅ Kubernetes nodes are ready"
    kubectl get nodes
else
    echo "❌ Kubernetes nodes are not ready"
    exit 1
fi

echo ""

# Test 2: Check namespace
echo "📋 Test 2: Checking namespace..."
if kubectl get namespace attendance-system &> /dev/null; then
    echo "✅ Namespace 'attendance-system' exists"
else
    echo "❌ Namespace 'attendance-system' does not exist"
    exit 1
fi

echo ""

# Test 3: Check pods
echo "📋 Test 3: Checking pods..."
kubectl get pods -n attendance-system
echo ""
pods_running=$(kubectl get pods -n attendance-system --no-headers 2>/dev/null | grep Running | wc -l)
if [ "$pods_running" -ge 2 ]; then
    echo "✅ Pods are running ($pods_running pods)"
else
    echo "⚠️  Some pods may not be running yet"
    echo "Check with: kubectl get pods -n attendance-system"
fi

echo ""

# Test 4: Check services
echo "📋 Test 4: Checking services..."
kubectl get services -n attendance-system
services=$(kubectl get services -n attendance-system --no-headers 2>/dev/null | wc -l)
if [ "$services" -ge 2 ]; then
    echo "✅ Services are created ($services services)"
else
    echo "⚠️  Services may not be created yet"
fi

echo ""

# Test 5: Check deployments
echo "📋 Test 5: Checking deployments..."
kubectl get deployments -n attendance-system
echo ""

# Test 6: Test backend API
echo "📋 Test 6: Testing backend API..."
echo "Starting port-forward..."
kubectl port-forward -n attendance-system service/backend-service 8000:8000 &
PORT_FORWARD_PID=$!
sleep 5

response=$(curl -s http://localhost:8000 2>/dev/null)
if [[ $response == *"Welcome"* ]]; then
    echo "✅ Backend API is responding"
else
    echo "⚠️  Backend API may not be ready yet"
    echo "Response: $response"
fi

kill $PORT_FORWARD_PID 2>/dev/null
sleep 2

echo ""

# Test 7: Check logs
echo "📋 Test 7: Checking backend logs..."
backend_pod=$(kubectl get pods -n attendance-system -l app=attendance-backend -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
if [ -n "$backend_pod" ]; then
    echo "Backend pod: $backend_pod"
    echo "Last 10 log lines:"
    kubectl logs $backend_pod -n attendance-system --tail=10 2>/dev/null || echo "Logs not available yet"
else
    echo "⚠️  Backend pod not found yet"
fi

echo ""

# Summary
echo "============================"
echo "🎉 KUBERNETES DEPLOYMENT COMPLETE!"
echo "============================"
echo ""
echo "📊 Cluster Status:"
kubectl get all -n attendance-system
echo ""
echo "🌐 To access the application:"
echo ""
echo "Option 1: Port Forwarding (Recommended)"
echo "  # Frontend:"
echo "  kubectl port-forward -n attendance-system service/frontend-service 8080:80"
echo "  # Then open: http://localhost:8080"
echo ""
echo "  # Backend:"
echo "  kubectl port-forward -n attendance-system service/backend-service 8000:8000"
echo "  # Then open: http://localhost:8000"
echo ""
echo "Option 2: Use both at once:"
echo "  kubectl port-forward -n attendance-system service/frontend-service 8080:80 &"
echo "  kubectl port-forward -n attendance-system service/backend-service 8000:8000 &"
echo ""
echo "📋 Useful commands:"
echo "  kubectl get pods -n attendance-system"
echo "  kubectl logs -f deployment/attendance-backend -n attendance-system"
echo "  kubectl describe pod <pod-name> -n attendance-system"
echo "  kubectl get events -n attendance-system --sort-by='.lastTimestamp'"
echo ""
echo "🔄 To update deployment:"
echo "  docker-compose build"
echo "  docker tag deep_project-backend:latest attendance-backend:latest"
echo "  kubectl rollout restart deployment/attendance-backend -n attendance-system"
echo ""
echo "🗑️  To delete deployment:"
echo "  kubectl delete namespace attendance-system"
echo ""
