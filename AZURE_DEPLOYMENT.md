# 🚀 Azure Backend Deployment Guide

This guide will help you deploy your FastAPI backend to Azure App Service and set up SSH tunneling to your DGX server.

## 📋 Prerequisites

1. **Azure Account**: You need an active Azure subscription
2. **Azure CLI**: Install Azure CLI on your machine
3. **Git**: For deployment
4. **SSH Access**: To your DGX server

## 🔧 Installation Steps

### Step 1: Install Azure CLI

```bash
# macOS
brew install azure-cli

# Linux
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Windows
# Download from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-windows
```

### Step 2: Login to Azure

```bash
az login
```

This will open a browser window for authentication.

### Step 3: Set Your Subscription (if you have multiple)

```bash
az account list --output table
az account set --subscription "Your-Subscription-Name"
```

## 🚀 Deployment

### Option 1: Automated Deployment (Recommended)

1. **Make the deployment script executable:**
   ```bash
   chmod +x azure-deploy.sh
   ```

2. **Run the deployment script:**
   ```bash
   ./azure-deploy.sh
   ```

3. **The script will:**
   - Create a resource group
   - Create an App Service plan
   - Create a web app
   - Configure environment variables
   - Set up the startup command

### Option 2: Manual Deployment

1. **Create Resource Group:**
   ```bash
   az group create --name sandbox-backend-rg --location eastus
   ```

2. **Create App Service Plan:**
   ```bash
   az appservice plan create \
     --name sandbox-backend-plan \
     --resource-group sandbox-backend-rg \
     --location eastus \
     --sku B1 \
     --is-linux
   ```

3. **Create Web App:**
   ```bash
   az webapp create \
     --name sandbox-backend-api \
     --resource-group sandbox-backend-rg \
     --plan sandbox-backend-plan \
     --runtime "PYTHON|3.12" \
     --deployment-local-git
   ```

4. **Configure Environment Variables:**
   ```bash
   az webapp config appsettings set \
     --resource-group sandbox-backend-rg \
     --name sandbox-backend-api \
     --settings \
     MONGO_URL="mongodb://localhost:27018/prepaire-lab" \
     REDIS_HOST="localhost" \
     REDIS_PORT="6379" \
     REDIS_PASSWORD="" \
     ENV="PRODUCTION" \
     USE_LOCAL_STORAGE="true" \
     LOCAL_STORAGE_PATH="./data"
   ```

5. **Configure Startup Command:**
   ```bash
   az webapp config set \
     --resource-group sandbox-backend-rg \
     --name sandbox-backend-api \
     --startup-file "uvicorn index:app --host 0.0.0.0 --port 8001"
   ```

## 🔗 SSH Tunneling Setup

### Step 1: Install sshpass (for automated tunneling)

```bash
# macOS
brew install sshpass

# Linux
sudo apt-get install sshpass
```

### Step 2: Set up SSH tunneling

```bash
chmod +x azure-tunnel.sh
./azure-tunnel.sh
```

This will create tunnels:
- **MongoDB**: `localhost:27018` → `DGX:27018`
- **Redis**: `localhost:6379` → `DGX:6379`

### Step 3: Verify tunnels are working

```bash
# Test MongoDB connection
nc -zv localhost 27018

# Test Redis connection
nc -zv localhost 6379
```

### Step 4: Manage tunnels

```bash
# Stop all tunnels
./stop-tunnels.sh

# Restart tunnels
./azure-tunnel.sh
```

## 📁 File Structure After Deployment

```
sandbox-BE/
├── azure-deploy.sh          # Azure deployment script
├── azure-tunnel.sh          # SSH tunneling script
├── stop-tunnels.sh          # Stop tunnels script
├── startup.sh               # Azure startup script
├── .azure/
│   └── config.yml          # Azure configuration
├── AZURE_DEPLOYMENT.md      # This file
├── requirements.txt         # Python dependencies
├── index.py                # FastAPI app
└── src/                    # Source code
```

## 🌐 Access Your Deployed Backend

After successful deployment, your backend will be available at:
- **Backend URL**: `https://sandbox-backend-api.azurewebsites.net`
- **API Documentation**: `https://sandbox-backend-api.azurewebsites.net/sandbox/docs`
- **Health Check**: `https://sandbox-backend-api.azurewebsites.net/sandbox/docs`

## 🔧 Configuration

### Environment Variables

The following environment variables are configured in Azure:

| Variable | Value | Description |
|----------|-------|-------------|
| `MONGO_URL` | `mongodb://localhost:27018/prepaire-lab` | MongoDB connection string |
| `REDIS_HOST` | `localhost` | Redis host (tunneled) |
| `REDIS_PORT` | `6379` | Redis port (tunneled) |
| `ENV` | `PRODUCTION` | Environment mode |
| `USE_LOCAL_STORAGE` | `true` | Use local storage |
| `LOCAL_STORAGE_PATH` | `./data` | Local storage path |

### Port Configuration

- **Backend Port**: 8001 (internal)
- **Azure Port**: 80 (external, automatically mapped)

## 🚨 Troubleshooting

### Common Issues

1. **Deployment Fails**
   - Check Azure CLI is installed and logged in
   - Verify you have sufficient permissions
   - Check resource group name conflicts

2. **SSH Tunneling Issues**
   - Verify DGX server credentials
   - Check firewall settings
   - Ensure ports are not already in use

3. **Backend Not Starting**
   - Check Azure App Service logs
   - Verify environment variables
   - Check startup command

### View Logs

```bash
# View Azure App Service logs
az webapp log tail \
  --resource-group sandbox-backend-rg \
  --name sandbox-backend-api
```

### Restart App Service

```bash
az webapp restart \
  --resource-group sandbox-backend-rg \
  --name sandbox-backend-api
```

## 🔄 Updating Your Frontend

After deployment, update your frontend API URLs from:
```typescript
// Old (local)
baseURL: "http://localhost:8001"

// New (Azure)
baseURL: "https://sandbox-backend-api.azurewebsites.net"
```

## 💰 Cost Optimization

- **App Service Plan**: B1 (Basic) is sufficient for development
- **Resource Group**: Delete when not needed to avoid charges
- **Auto-shutdown**: Consider enabling for non-production environments

## 🎯 Next Steps

1. ✅ Deploy backend to Azure
2. ✅ Set up SSH tunneling to DGX
3. ✅ Test API endpoints
4. ✅ Update frontend URLs
5. ✅ Monitor performance and logs

## 📞 Support

If you encounter issues:
1. Check Azure App Service logs
2. Verify SSH tunnel status
3. Test individual components
4. Review this documentation

---

**Happy Deploying! 🚀** 