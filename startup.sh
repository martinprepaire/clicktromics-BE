#!/bin/bash

# Azure App Service Startup Script
# This script runs when your Azure App Service starts

echo "🚀 Starting Sandbox Backend on Azure..."

# Set environment variables if not already set
export MONGO_URL=${MONGO_URL:-"mongodb://localhost:27018/prepaire-lab"}
export REDIS_HOST=${REDIS_HOST:-"localhost"}
export REDIS_PORT=${REDIS_PORT:-"6379"}
export REDIS_PASSWORD=${REDIS_PASSWORD:-""}
export ENV=${ENV:-"PRODUCTION"}
export USE_LOCAL_STORAGE=${USE_LOCAL_STORAGE:-"true"}
export LOCAL_STORAGE_PATH=${LOCAL_STORAGE_PATH:-"./data"}

# Create data directory if it doesn't exist
mkdir -p $LOCAL_STORAGE_PATH

# Install bio-core-lib if not already installed
if ! python -c "import bio_core" 2>/dev/null; then
    echo "📦 Installing bio-core-lib..."
    pip install git+https://LOudPrepaire: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@github.com/LOudPrepaire/bio-core-lib.git@v1.0.12
fi

# Start the FastAPI application
echo "🌐 Starting FastAPI server on port 8001..."
python -m uvicorn index:app --host 0.0.0.0 --port 8001 