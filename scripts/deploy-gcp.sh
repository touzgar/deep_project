#!/bin/bash

# GCP Deployment Script
# This script deploys the attendance system to Google Cloud Platform

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🌐 DEPLOYING TO GOOGLE CLOUD PLATFORM"
echo "======================================"
echo ""

# Check if PROJECT_ID is set
if [ -z "$GCP_PROJECT_ID" ]; then
    echo -e "${RED}❌ Error: GCP_PROJECT_ID environment variable is not set${NC}"
    echo "Please set it with: export GCP_PROJECT_ID=your-project-id"
    exit 1
fi

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ Error: gcloud CLI is not installed${NC}"
    echo "Install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}❌ Error: kubectl is not installed${NC}"
    echo "Install it with: gcloud components install kubectl"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites check passed${NC}"
echo ""

# Set project
echo "📋 Setting GCP project..."
gcloud config set project $GCP_PROJECT_ID

# Enable required APIs
echo "📋 Enabling required APIs..."
gcloud services enable container.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable monitoring.googleapis.com
gcloud services enable logging.googleapis.com

# Configure Docker for GCR
echo "📋 Configuring Docker for GCR..."
gcloud auth configure-docker

# Build and push backend image
echo "🔨 Building and pushing backend image..."
cd backend
docker build -t gcr.io/$GCP_PROJECT_ID/attendance-backend:latest .
docker push gcr.io/$GCP_PROJECT_ID/attendance-backend:latest
cd ..

# Build and push frontend image
echo "🔨 Building and pushing frontend image..."
cd frontend
docker build -t gcr.io/$GCP_PROJECT_ID/attendance-frontend:latest \
  --build-arg VITE_API_URL=http://EXTERNAL_IP/api/v1 .
docker push gcr.io/$GCP_PROJECT_ID/attendance-frontend:latest
cd ..

# Create GKE cluster (if it doesn't exist)
echo "📋 Checking if GKE cluster exists..."
if ! gcloud container clusters describe attendance-cluster --region=europe-west1 &> /dev/null; then
    echo "🔨 Creating GKE cluster..."
    gcloud container clusters create attendance-cluster \
      --num-nodes=3 \
      --machine-type=e2-medium \
      --region=europe-west1 \
      --enable-autoscaling \
      --min-nodes=2 \
      --max-nodes=5 \
      --enable-autorepair \
      --enable-autoupgrade
else
    echo -e "${GREEN}✅ Cluster already exists${NC}"
fi

# Get cluster credentials
echo "📋 Getting cluster credentials..."
gcloud container clusters get-credentials attendance-cluster --region=europe-west1

# Update deployment files with GCR images
echo "📋 Updating deployment files..."
sed -i "s|image: .*attendance-backend.*|image: gcr.io/$GCP_PROJECT_ID/attendance-backend:latest|g" k8s/backend-deployment.yaml
sed -i "s|image: .*attendance-frontend.*|image: gcr.io/$GCP_PROJECT_ID/attendance-frontend:latest|g" k8s/frontend-deployment.yaml

# Deploy to Kubernetes
echo "🚀 Deploying to Kubernetes..."
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/postgres-pvc.yaml
kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/ingress.yaml
kubectl apply -f k8s/hpa.yaml

# Wait for deployments
echo "⏳ Waiting for deployments to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/attendance-backend -n attendance-system
kubectl wait --for=condition=available --timeout=300s deployment/attendance-frontend -n attendance-system

# Get external IP
echo ""
echo "======================================"
echo -e "${GREEN}🎉 DEPLOYMENT COMPLETE!${NC}"
echo "======================================"
echo ""
echo "📋 Cluster Information:"
kubectl get nodes
echo ""
echo "📋 Pods Status:"
kubectl get pods -n attendance-system
echo ""
echo "📋 Services:"
kubectl get services -n attendance-system
echo ""
echo "📋 Ingress (External IP):"
kubectl get ingress -n attendance-system
echo ""
echo -e "${YELLOW}⚠️  Note: It may take 5-10 minutes for the external IP to be assigned${NC}"
echo ""
echo "📋 To check the external IP later, run:"
echo "   kubectl get ingress -n attendance-system"
echo ""
echo "📋 To view logs:"
echo "   kubectl logs -f deployment/attendance-backend -n attendance-system"
echo "   kubectl logs -f deployment/attendance-frontend -n attendance-system"
echo ""
