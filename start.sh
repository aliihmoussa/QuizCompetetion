#!/bin/bash

# Quiz Competition App Startup Script

echo "🏆 Starting Quiz Competition App..."
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed (try both old and new versions)
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from env.example..."
    cp env.example .env
fi

# Start services
echo "🚀 Starting Docker containers..."
$COMPOSE_CMD up --build

echo ""
echo "✅ Quiz Competition App is running!"
echo "🌐 Access the app at: http://localhost:8501"

