#!/bin/bash

echo "🧪 RUNNING TESTS"
echo "================"
echo ""

# Run backend tests
echo "📋 Running Backend Tests..."
docker-compose --profile test up --build backend-test

# Check exit code
if [ $? -eq 0 ]; then
    echo "✅ Backend tests passed!"
else
    echo "❌ Backend tests failed!"
    exit 1
fi

echo ""

# Run frontend tests
echo "📋 Running Frontend Tests..."
docker-compose --profile test up --build frontend-test

# Check exit code
if [ $? -eq 0 ]; then
    echo "✅ Frontend tests passed!"
else
    echo "❌ Frontend tests failed!"
    exit 1
fi

echo ""
echo "================"
echo "🎉 ALL TESTS PASSED!"
echo "================"
echo ""
echo "📊 Test coverage report available at:"
echo "   Backend: backend/htmlcov/index.html"
echo ""
