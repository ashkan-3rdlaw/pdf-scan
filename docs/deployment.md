# PDF Scan Service - Render.com Deployment Guide

## Overview

This guide walks you through deploying the PDF Scan Service on Render.com using the quick start approach with in-memory backend.

## Prerequisites

- GitHub/GitLab/Bitbucket account
- Render.com account (free tier available)
- Your PDF scan service repository pushed to Git

## Quick Start Deployment

### Step 1: Prepare Repository

Ensure your repository contains:
- `requirements.txt` (created for Render compatibility)
- `render.yaml` (Infrastructure as Code configuration)
- `src/pdf_scan/` (application code)

### Step 2: Create Render Account

1. Go to [render.com](https://render.com/)
2. Sign up with your Git provider (GitHub/GitLab/Bitbucket)
3. Connect your account

### Step 3: Deploy Web Service

#### Option A: Using Render Dashboard (Recommended for first deployment)

1. **Create New Service**
   - Click "New" → "Web Service"
   - Select "Build and deploy from a Git repository"
   - Click "Next"

2. **Connect Repository**
   - Select your PDF scan repository
   - Choose the branch (usually `main`)
   - Click "Next"

3. **Configure Service**
   - **Name**: `pdf-scan-service` (or your preferred name)
   - **Environment**: `Python 3`
   - **Build Command**: `uv sync --frozen`
   - **Start Command**: `uv run python -m pdf_scan.main`
   - **Instance Type**: `Free` (for testing)

4. **Set Environment Variables**
   ```bash
   DATABASE_BACKEND=memory
   APP_HOST=0.0.0.0
   APP_PORT=$PORT
   APP_RELOAD=false
   ```

5. **Deploy**
   - Click "Create Web Service"
   - Monitor the deployment logs
   - Wait for "Deploy successful" message

#### Option B: Using render.yaml (Infrastructure as Code)

1. **Deploy from Blueprint**
   - Click "New" → "Blueprint"
   - Select your repository
   - Render will automatically detect `render.yaml`
   - Click "Apply"

### Step 4: Test Deployment

Once deployed, your service will be available at:
`https://your-service-name.onrender.com`

#### Test Endpoints

1. **Health Check**
   ```bash
   curl https://your-service-name.onrender.com/health
   ```
   Expected response:
   ```json
   {
     "status": "healthy",
     "version": "0.1.0"
   }
   ```

2. **Upload Test**
   ```bash
   curl -X POST -F "file=@tests/fixtures/sample_without_pii.pdf" \
     https://your-service-name.onrender.com/upload
   ```

3. **Findings Test**
   ```bash
   curl https://your-service-name.onrender.com/findings
   ```

4. **Metrics Test**
   ```bash
   curl https://your-service-name.onrender.com/metrics
   ```

## Configuration Details

### Environment Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `DATABASE_BACKEND` | `memory` | Use in-memory backend (no external dependencies) |
| `APP_HOST` | `0.0.0.0` | Bind to all interfaces |
| `APP_PORT` | `$PORT` | Use Render's assigned port |
| `APP_RELOAD` | `false` | Disable auto-reload in production |

### Render-Specific Notes

- **Port**: Render automatically assigns a port via `$PORT` environment variable
- **File System**: Ephemeral (data lost on restart) - perfect for in-memory backend
- **Free Tier**: Service sleeps after 15 minutes of inactivity
- **HTTPS**: Automatic SSL certificates
- **Zero Downtime**: Automatic deploys with zero downtime

## Monitoring and Maintenance

### Health Monitoring

- Use `/health` endpoint for health checks
- Render provides built-in monitoring
- Set up alerts for service failures

### Logs

- Access logs via Render Dashboard
- Monitor for errors and performance issues
- Use `/metrics` endpoint for performance data

### Updates

- Push changes to your Git repository
- Render automatically redeploys
- Zero downtime updates

## Troubleshooting

### Common Issues

1. **Build Failures**
   - Check `requirements.txt` syntax
   - Verify Python version compatibility
   - Check build logs for specific errors

2. **Service Won't Start**
   - Verify start command syntax
   - Check environment variables
   - Ensure port binding is correct

3. **Health Check Failures**
   - Verify `/health` endpoint works locally
   - Check service logs for errors
   - Ensure service is binding to `0.0.0.0:$PORT`

### Debug Commands

```bash
# Test locally with Render-like environment
export PORT=8000
uv run python -m pdf_scan.main

# Check service health
curl http://localhost:8000/health
```

## Future Upgrades

### Phase 9.1: ClickHouse Integration
- Set up external ClickHouse service
- Update environment variables
- Test data persistence

### Phase 9.2: Custom Domain
- Add custom domain in Render Dashboard
- Configure DNS settings
- Test SSL certificates

### Phase 9.3: Production Configuration
- Upgrade to paid instance
- Configure autoscaling
- Set up monitoring alerts

### Phase 9.4: Persistent Storage
- Add persistent disk
- Configure file storage
- Note: Disables zero-downtime deploys

## Security Considerations

- All traffic is HTTPS by default
- Environment variables are secure
- No sensitive data stored in memory
- Consider adding authentication for production use

## Cost Optimization

- Free tier: Good for testing and demos
- Paid tiers: Better performance and reliability
- Monitor usage and scale as needed

## Support

- Render Documentation: [render.com/docs](https://render.com/docs)
- Service Logs: Available in Render Dashboard
- Health Checks: Use `/health` endpoint
- Metrics: Use `/metrics` endpoint
