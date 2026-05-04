#!/bin/bash
# Docker setup script for IPL Playoff Predictor Backend

set -e

echo "🐳 IPL Playoff Predictor - Docker Setup"
echo "======================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

echo "✅ Docker is installed"

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker Compose is available"

# Build the Docker image
echo ""
echo "📦 Building Docker image..."
docker build -t ipl-predictor:latest .

echo ""
echo "✅ Docker image built successfully!"

# Option to run the container
echo ""
read -p "Do you want to start the container now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🚀 Starting container with docker-compose..."
    docker-compose up -d
    
    echo ""
    echo "✅ Container is running!"
    echo ""
    echo "📋 Quick Commands:"
    echo "   View logs:    docker-compose logs -f"
    echo "   Stop:         docker-compose down"
    echo "   Restart:      docker-compose restart"
    echo ""
    echo "🌐 Test the API:"
    echo "   Health:       curl http://localhost:8000/health"
    echo "   Probabilities: curl http://localhost:8000/probabilities"
fi

echo ""
echo "✨ Setup complete!"
