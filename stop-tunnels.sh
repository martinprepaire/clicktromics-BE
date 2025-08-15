#!/bin/bash

# Stop SSH Tunnels Script
# This script stops all active SSH tunnels

echo "🛑 Stopping all SSH tunnels..."

if [ -f .tunnel_pids ]; then
    echo "🧹 Cleaning up tunnels..."
    while read -r pid; do
        if kill -0 $pid 2>/dev/null; then
            kill $pid
            echo "   ✅ Killed tunnel PID: $pid"
        else
            echo "   ⚠️  Tunnel PID $pid already stopped"
        fi
    done < .tunnel_pids
    rm -f .tunnel_pids
    echo "✅ All tunnels stopped"
else
    echo "ℹ️  No active tunnels found"
fi

# Also kill any remaining ssh processes
pkill -f "ssh.*-L.*27018" 2>/dev/null
pkill -f "ssh.*-L.*6379" 2>/dev/null

echo "🔍 Checking for remaining SSH processes..."
ps aux | grep "ssh.*-L" | grep -v grep || echo "   No SSH tunnel processes found" 