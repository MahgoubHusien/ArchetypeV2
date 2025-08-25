# 🚀 Render Deployment Guide

## 📋 Overview
This guide explains how to deploy the ArchetypeV2 AI agent and backend services to Render using the `render.yaml` configuration file.

## 🏗️ Services Architecture
- **Backend API**: Main API service handling agent management and summaries
- **Agent Worker**: Service for running AI agents and processing transcripts

## 🔧 Prerequisites
1. [Render Account](https://render.com/) (free tier available)
2. Git repository with your code
3. Environment variables ready

## 📁 Files Created/Modified
- `render.yaml` - Render service definitions
- `backend/main.py` - Updated for Render compatibility
- `agent_worker/server.py` - Updated for Render compatibility
- `requirements.txt` - Added production dependencies
- `agent_worker/static/` - Static files directory

## 🚀 Deployment Steps

### 1. **Push Code to Git**
```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### 2. **Deploy Using render.yaml**

#### Option A: Automatic Deployment (Recommended)
1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" → "Blueprint"
3. Connect your Git repository
4. Select the repository containing `render.yaml`
5. Render will automatically create both services

#### Option B: Manual Service Creation
If you prefer to create services manually, use these settings:

**Backend Service:**
- **Name**: `archetype-backend`
- **Environment**: Python 3
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn backend.main:app -b 0.0.0.0:$PORT --workers 1`

**Agent Worker Service:**
- **Name**: `archetype-agent-worker`
- **Environment**: Python 3
- **Build Command**: `pip install -r requirements.txt && mkdir -p agent_worker/static`
- **Start Command**: `gunicorn agent_worker.server:app -b 0.0.0.0:$PORT --workers 1`

### 3. **Set Environment Variables**

#### Backend Service Variables:
```bash
OPENAI_API_KEY=your_openai_key_here
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_key
PYTHONPATH=/opt/render/project/src
```

#### Agent Worker Service Variables:
```bash
OPENAI_API_KEY=your_openai_key_here
PYTHONPATH=/opt/render/project/src
```

## 🌐 Service URLs
After deployment, your services will be available at:
- **Backend**: `https://archetype-backend.onrender.com`
- **Agent Worker**: `https://archetype-agent-worker.onrender.com`

## 🧪 Testing Deployment

### Health Checks
```bash
# Test backend
curl https://archetype-backend.onrender.com/health

# Test agent worker
curl https://archetype-agent-worker.onrender.com/health
```

### API Endpoints
```bash
# Test backend API
curl -X POST https://archetype-backend.onrender.com/agent/run \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "persona": {
      "name": "Test User",
      "bio": "A test user for deployment verification."
    },
    "ux_question": "Test the deployment by exploring this website."
  }'
```

## 🔍 Monitoring & Debugging

### Render Dashboard
- Monitor service health and performance
- View build logs and deployment status
- Check resource usage

### Service Logs
- Access real-time logs in Render dashboard
- Monitor for errors and performance issues

### Health Check Endpoints
Both services expose `/health` endpoints for monitoring:
- Backend: Returns `{"status":"healthy","service":"agent-api"}`
- Agent Worker: Returns `{"ok":true,"service":"agent-worker"}`

## 🚨 Common Issues & Solutions

### 1. **Build Failures**
- Check `requirements.txt` for missing dependencies
- Verify Python version compatibility
- Check build logs for specific error messages

### 2. **Service Won't Start**
- Verify start command syntax
- Check environment variables are set correctly
- Ensure port binding uses `$PORT` environment variable

### 3. **CORS Issues**
- Backend CORS is configured for Render domains
- Update frontend API endpoints to use Render URLs
- Check CORS configuration in `backend/main.py`

### 4. **Static Files Not Found**
- Agent worker creates `static` directory during build
- Verify `agent_worker/static/` exists
- Check file permissions

## 🔄 Updating Services
- Push changes to your Git repository
- Render automatically redeploys on git push
- Monitor deployment status in dashboard

## 💰 Cost Considerations
- **Free Tier**: 750 hours/month per service
- **Paid Plans**: Start at $7/month per service
- Monitor usage in Render dashboard

## 📞 Support
- [Render Documentation](https://render.com/docs)
- [Render Community](https://community.render.com/)
- Check service logs for debugging information

## 🎯 Next Steps
After successful deployment:
1. Update frontend API endpoints to use Render URLs
2. Test all API endpoints
3. Monitor service performance
4. Set up custom domains if needed
5. Configure monitoring and alerts
