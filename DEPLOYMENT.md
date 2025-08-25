# 🚀 ArchetypeV2 Deployment Guide

This guide explains how to deploy the ArchetypeV2 backend and agent-worker services to Render using Docker.

## 📋 Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed and running
- [Git](https://git-scm.com/) for version control
- [Render](https://render.com/) account
- OpenAI API key
- Supabase credentials

## 🏗️ Project Structure

```
ArchetypeV2/
├── backend/                 # Backend API service
│   ├── Dockerfile          # Backend Docker configuration
│   ├── .dockerignore       # Backend Docker ignore rules
│   ├── main.py             # FastAPI application
│   ├── config.py           # Configuration settings
│   ├── requirements.txt    # Python dependencies
│   └── ...
├── agent_worker/           # Agent worker service
│   ├── Dockerfile          # Agent worker Docker configuration
│   ├── .dockerignore       # Agent worker Docker ignore rules
│   ├── server.py           # FastAPI application
│   ├── requirements.txt    # Python dependencies
│   └── ...
├── docker-compose.yml      # Local development setup
├── render.yaml             # Render deployment configuration
├── deploy.sh               # Local deployment testing script
└── requirements.txt        # Root dependencies
```

## 🔧 Local Development with Docker

### 1. Build and Test Locally

```bash
# Make the deployment script executable
chmod +x deploy.sh

# Run the deployment script (tests Docker builds and health checks)
./deploy.sh
```

### 2. Using Docker Compose

```bash
# Start both services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 3. Manual Docker Commands

```bash
# Build backend
docker build -t archetype-backend:latest ./backend

# Build agent-worker
docker build -t archetype-agent-worker:latest ./agent_worker

# Run backend
docker run -d --name backend \
  -p 8000:8000 \
  -e OPENAI_API_KEY="your-key" \
  -e SUPABASE_URL="your-url" \
  -e SUPABASE_ANON_KEY="your-key" \
  archetype-backend:latest

# Run agent-worker
docker run -d --name agent-worker \
  -p 8001:8001 \
  -e OPENAI_API_KEY="your-key" \
  archetype-agent-worker:latest
```

## 🌐 Deployment to Render

### 1. Environment Variables

Set these environment variables in your Render dashboard:

**Backend Service:**
- `OPENAI_API_KEY`: Your OpenAI API key
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_ANON_KEY`: Your Supabase anonymous key
- `PORT`: 8000 (auto-set by Render)

**Agent Worker Service:**
- `OPENAI_API_KEY`: Your OpenAI API key
- `PORT`: 8001 (auto-set by Render)

### 2. Render Configuration

The `render.yaml` file is configured for automatic deployment:

```yaml
services:
  - type: web
    name: archetype-backend
    env: docker
    plan: free
    dockerfilePath: ./backend/Dockerfile
    dockerContext: ./backend
    # ... configuration

  - type: web
    name: archetype-agent-worker
    env: docker
    plan: free
    dockerfilePath: ./agent_worker/Dockerfile
    dockerContext: ./agent_worker
    # ... configuration
```

### 3. Deployment Steps

1. **Push to GitHub**: Commit and push your code to a GitHub repository
2. **Connect to Render**: In Render dashboard, create a new "Blueprint" service
3. **Connect Repository**: Link your GitHub repository
4. **Deploy**: Render will automatically detect the `render.yaml` and deploy both services

### 4. Service URLs

After deployment, your services will be available at:
- **Backend**: `https://archetype-backend.onrender.com`
- **Agent Worker**: `https://archetype-agent-worker.onrender.com`

## 🧪 Testing Deployed Services

### Health Checks

```bash
# Test backend
curl https://archetype-backend.onrender.com/health

# Test agent-worker
curl https://archetype-agent-worker.onrender.com/health
```

### API Testing

```bash
# Test backend endpoints
curl -X POST https://archetype-backend.onrender.com/agent/run \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "persona": {"name": "Test", "bio": "Test user"}, "ux_question": "Is the site easy to navigate?"}'

# Test agent-worker endpoints
curl -X POST https://archetype-agent-worker.onrender.com/agent/run \
  -H "Content-Type: application/json" \
  -d '{"run_id": "test-123", "url": "https://example.com", "persona": {"name": "Test", "bio": "Test user"}, "ux_question": "Is the site easy to navigate?"}'
```

## 🔍 Troubleshooting

### Common Issues

1. **Port Already in Use**: Make sure ports 8000 and 8001 are not occupied
2. **Environment Variables**: Ensure all required environment variables are set
3. **Docker Build Failures**: Check that all dependencies are properly specified in requirements.txt
4. **Health Check Failures**: Verify that the health endpoints are working correctly

### Debug Commands

```bash
# Check running containers
docker ps

# View container logs
docker logs <container-name>

# Check container health
docker inspect <container-name> | grep Health -A 10

# Test health endpoints locally
curl -f http://localhost:8000/health
curl -f http://localhost:8001/health
```

### Render Logs

- Check the Render dashboard for build and runtime logs
- Monitor the "Events" tab for deployment status
- Use the "Logs" tab to view real-time application logs

## 📚 Additional Resources

- [Render Documentation](https://render.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Documentation](https://docs.docker.com/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Supabase Documentation](https://supabase.com/docs)

## 🤝 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review Render deployment logs
3. Verify environment variable configuration
4. Test locally with Docker before deploying
5. Check that all dependencies are properly specified

---

**Happy Deploying! 🎉**
