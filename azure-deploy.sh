#!/bin/bash

# Azure Backend Deployment Script
# This script deploys your FastAPI backend to Azure App Service

echo "🚀 Starting Azure Backend Deployment..."

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI is not installed. Please install it first:"
    echo "   https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Check if logged in to Azure
if ! az account show &> /dev/null; then
    echo "🔐 Please login to Azure first:"
    az login
fi

# Configuration variables (update these)
RESOURCE_GROUP="sandbox-backend-rg"
LOCATION="eastus"
APP_SERVICE_PLAN="sandbox-backend-plan"
APP_NAME="sandbox-backend-api"
PYTHON_VERSION="3.12"

echo "📋 Using configuration:"
echo "   Resource Group: $RESOURCE_GROUP"
echo "   Location: $LOCATION"
echo "   App Service Plan: $APP_SERVICE_PLAN"
echo "   App Name: $APP_NAME"
echo "   Python Version: $PYTHON_VERSION"

# Create resource group
echo "🏗️ Creating resource group..."
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create app service plan
echo "📊 Creating app service plan..."
az appservice plan create \
    --name $APP_SERVICE_PLAN \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --sku B1 \
    --is-linux

# Create web app
echo "🌐 Creating web app..."
az webapp create \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --plan $APP_SERVICE_PLAN \
    --runtime "PYTHON|$PYTHON_VERSION" \
    --deployment-local-git

# Configure environment variables
echo "⚙️ Configuring environment variables..."
az webapp config appsettings set \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --settings \
    MONGO_URL="mongodb://localhost:27018/prepaire-lab" \
    REDIS_HOST="localhost" \
    REDIS_PORT="6379" \
    REDIS_PASSWORD="" \
    ENV="PRODUCTION" \
    USE_LOCAL_STORAGE="true" \
    LOCAL_STORAGE_PATH="./data"

# Configure startup command
echo "🚀 Configuring startup command..."
az webapp config set \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --startup-file "uvicorn index:app --host 0.0.0.0 --port 8001"

# Get deployment URL
DEPLOYMENT_URL=$(az webapp show \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --query "defaultHostName" \
    --output tsv)

echo "✅ Deployment completed successfully!"
echo "🌐 Your backend is now available at: https://$DEPLOYMENT_URL"
echo "📚 API Documentation: https://$DEPLOYMENT_URL/sandbox/docs"
echo ""
echo "🔧 Next steps:"
echo "   1. Set up SSH tunneling to your DGX server"
echo "   2. Update your frontend API URLs to point to Azure"
echo "   3. Test the API endpoints" 