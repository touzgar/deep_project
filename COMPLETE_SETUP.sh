#!/bin/bash

echo "🎯 COMPLETE PROJECT SETUP"
echo "========================="
echo ""
echo "This script will:"
echo "1. Fix the login issue (bcrypt)"
echo "2. Test the application"
echo "3. Prepare for GCP deployment"
echo ""
read -p "Press Enter to continue..."

# Step 1: Fix login issue
echo ""
echo "🔧 STEP 1: Fixing Login Issue"
echo "=============================="
chmod +x FINAL_COMPLETE_FIX.sh
./FINAL_COMPLETE_FIX.sh

if [ $? -ne 0 ]; then
    echo "❌ Login fix failed. Please check the errors above."
    exit 1
fi

# Step 2: Run tests
echo ""
echo "🧪 STEP 2: Running Tests"
echo "========================"
read -p "Do you want to run tests? (y/n): " run_tests

if [ "$run_tests" = "y" ]; then
    chmod +x run_tests.sh
    ./run_tests.sh
fi

# Step 3: GCP Deployment
echo ""
echo "🌐 STEP 3: GCP Deployment"
echo "========================="
echo ""
echo "To deploy to GCP, you need:"
echo "1. A GCP account (get $300 free credits)"
echo "2. Google Cloud SDK installed"
echo "3. A project ID"
echo ""
read -p "Do you want to deploy to GCP now? (y/n): " deploy_gcp

if [ "$deploy_gcp" = "y" ]; then
    read -p "Enter your GCP Project ID: " project_id
    export GCP_PROJECT_ID=$project_id
    
    chmod +x scripts/deploy-gcp.sh
    ./scripts/deploy-gcp.sh
else
    echo ""
    echo "📋 To deploy to GCP later, run:"
    echo "   export GCP_PROJECT_ID=your-project-id"
    echo "   chmod +x scripts/deploy-gcp.sh"
    echo "   ./scripts/deploy-gcp.sh"
fi

echo ""
echo "=============================="
echo "🎉 SETUP COMPLETE!"
echo "=============================="
echo ""
echo "📋 Your application is ready!"
echo ""
echo "🌐 Access your application:"
echo "   Frontend: http://localhost:5173"
echo "   Backend:  http://localhost:8000"
echo ""
echo "👤 Login credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "📚 Documentation:"
echo "   - PROJECT_COMPLETION_SUMMARY.md"
echo "   - GCP_DEPLOYMENT_GUIDE.md"
echo ""
