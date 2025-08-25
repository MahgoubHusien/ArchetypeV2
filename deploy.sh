#!/bin/bash

# ArchetypeV2 Deployment Script
# This script helps build and test Docker images locally before deploying to Render

set -e

echo "🚀 ArchetypeV2 Deployment Script"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

print_status "Docker is running ✓"

# Check if required environment variables are set
if [ -z "$OPENAI_API_KEY" ]; then
    print_warning "OPENAI_API_KEY environment variable is not set"
    print_warning "Please set it before deploying: export OPENAI_API_KEY='your-key-here'"
fi

if [ -z "$SUPABASE_URL" ]; then
    print_warning "SUPABASE_URL environment variable is not set"
    print_warning "Please set it before deploying: export SUPABASE_URL='your-url-here'"
fi

if [ -z "$SUPABASE_ANON_KEY" ]; then
    print_warning "SUPABASE_ANON_KEY environment variable is not set"
    print_warning "Please set it before deploying: export SUPABASE_ANON_KEY='your-key-here'"
fi

# Build Docker images
print_status "Building Docker images..."

print_status "Building backend image..."
docker build -t archetype-backend:latest ./backend

print_status "Building agent-worker image..."
docker build -t archetype-agent-worker:latest ./agent_worker

print_status "Docker images built successfully ✓"

# Test images locally
print_status "Testing Docker images locally..."

print_status "Starting backend container..."
docker run -d --name test-backend \
    -p 8000:8000 \
    -e OPENAI_API_KEY="$OPENAI_API_KEY" \
    -e SUPABASE_URL="$SUPABASE_URL" \
    -e SUPABASE_ANON_KEY="$SUPABASE_ANON_KEY" \
    archetype-backend:latest

# Wait for backend to start
sleep 10

# Test backend health
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_status "Backend health check passed ✓"
else
    print_error "Backend health check failed"
    docker logs test-backend
    docker stop test-backend
    docker rm test-backend
    exit 1
fi

print_status "Starting agent-worker container..."
docker run -d --name test-agent-worker \
    -p 8001:8001 \
    -e OPENAI_API_KEY="$OPENAI_API_KEY" \
    archetype-agent-worker:latest

# Wait for agent-worker to start
sleep 10

# Test agent-worker health
if curl -f http://localhost:8001/health > /dev/null 2>&1; then
    print_status "Agent-worker health check passed ✓"
else
    print_error "Agent-worker health check failed"
    docker logs test-agent-worker
    docker stop test-agent-worker
    docker rm test-agent-worker
    exit 1
fi

print_status "All health checks passed ✓"

# Clean up test containers
print_status "Cleaning up test containers..."
docker stop test-backend test-agent-worker
docker rm test-backend test-agent-worker

print_status "Local testing completed successfully ✓"
echo ""
print_status "Next steps:"
echo "1. Push your code to GitHub"
echo "2. Connect your repository to Render"
echo "3. Deploy using the render.yaml configuration"
echo ""
print_status "Your services will be available at:"
echo "  - Backend: https://archetype-backend.onrender.com"
echo "  - Agent Worker: https://archetype-agent-worker.onrender.com"
