#!/bin/bash

# Fix permissions for TextLeaf directories
# Run this script on the server to fix permission issues

echo "🔧 Fixing TextLeaf directory permissions..."

cd /opt/textleaf

# Create directories if they don't exist
mkdir -p uploads output static/backgrounds static/audio

# Set proper ownership (user ID 1000 is the appuser in Docker)
sudo chown -R 1000:1000 uploads output static

# Set permissions to allow read/write/execute
sudo chmod -R 777 uploads output static

echo "✅ Permissions fixed!"
echo ""
echo "📊 Current permissions:"
ls -la uploads/ output/ static/

echo ""
echo "🚀 Now rebuild and restart Docker containers:"
echo "   docker-compose down"
echo "   docker-compose build --no-cache"
echo "   docker-compose up -d"
