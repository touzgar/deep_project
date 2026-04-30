#!/bin/bash

# Build Docker images for production
# Usage: ./scripts/build-images.sh

# No registry needed - building locally
VERSION=${1:-"latest"}

echo "Building Docker images locally..."
echo "Version: $VERSION"

# Build backend
echo "Building backend image..."
docker build -t attendance-backend:${VERSION} -f backend/Dockerfile backend/
docker tag attendance-backend:${VERSION} attendance-backend:latest

# Build frontend
echo "Building frontend image..."
docker build -t attendance-frontend:${VERSION} -f frontend/Dockerfile frontend/
docker tag attendance-frontend:${VERSION} attendance-frontend:latest

echo ""
echo "✅ Build complete!"
echo ""
echo "Images created:"
echo "  - attendance-backend:latest"
echo "  - attendance-frontend:latest"
echo ""
echo "To run locally with Docker Compose:"
echo "  docker-compose up"
echo ""
echo "To deploy to Kubernetes:"
echo "  ./scripts/deploy-k8s.sh"
