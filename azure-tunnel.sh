#!/bin/bash

# Azure to DGX Server SSH Tunneling Script
# This script sets up SSH tunneling from your Azure backend to your DGX server

echo "🔗 Setting up SSH tunneling from Azure to DGX server..."

# DGX Server Configuration
DGX_HOST="94.202.21.171"
DGX_USER="dgx"
DGX_PASSWORD="prepaire2025"

# Local ports for tunneling
MONGO_PORT="27018"
REDIS_PORT="6379"

echo "📋 Tunneling Configuration:"
echo "   DGX Host: $DGX_HOST"
echo "   DGX User: $DGX_USER"
echo "   MongoDB Port: $MONGO_PORT"
echo "   Redis Port: $REDIS_PORT"

# Function to create tunnel
create_tunnel() {
    local local_port=$1
    local remote_port=$2
    local service_name=$3
    
    echo "🔗 Creating tunnel for $service_name..."
    echo "   Local port $local_port -> DGX port $remote_port"
    
    # Create SSH tunnel in background
    sshpass -p "$DGX_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
        -L $local_port:localhost:$remote_port \
        $DGX_USER@$DGX_HOST \
        -N &
    
    local tunnel_pid=$!
    echo "   ✅ $service_name tunnel created with PID: $tunnel_pid"
    
    # Store PID for later cleanup
    echo $tunnel_pid >> .tunnel_pids
}

# Check if sshpass is installed
if ! command -v sshpass &> /dev/null; then
    echo "❌ sshpass is not installed. Installing..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        brew install sshpass
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        sudo apt-get update && sudo apt-get install -y sshpass
    else
        echo "❌ Please install sshpass manually for your OS"
        exit 1
    fi
fi

# Clean up any existing tunnels
if [ -f .tunnel_pids ]; then
    echo "🧹 Cleaning up existing tunnels..."
    while read -r pid; do
        if kill -0 $pid 2>/dev/null; then
            kill $pid
            echo "   Killed tunnel PID: $pid"
        fi
    done < .tunnel_pids
    rm -f .tunnel_pids
fi

# Create tunnels
create_tunnel $MONGO_PORT 27018 "MongoDB"
create_tunnel $REDIS_PORT 6379 "Redis"

echo ""
echo "✅ SSH tunneling setup completed!"
echo "🔗 MongoDB: localhost:$MONGO_PORT -> DGX:27018"
echo "🔗 Redis: localhost:$REDIS_PORT -> DGX:6379"
echo ""
echo "📊 To verify tunnels are working:"
echo "   MongoDB: nc -zv localhost $MONGO_PORT"
echo "   Redis: nc -zv localhost $REDIS_PORT"
echo ""
echo "🛑 To stop all tunnels: ./stop-tunnels.sh"
echo "🔄 To restart tunnels: ./azure-tunnel.sh" 