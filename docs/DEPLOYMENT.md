# OpenBB Open Data Platform - DigitalOcean Deployment Guide

## Overview

This guide covers deploying OpenBB ODP on DigitalOcean with remote user access.

## Prerequisites

1. **DigitalOcean Account**: Sign up at https://digitalocean.com
2. **doctl CLI**: DigitalOcean command-line tool
3. **Domain (optional)**: For HTTPS access

### Install doctl

```bash
# macOS
brew install doctl

# Linux (snap)
sudo snap install doctl

# Authenticate
doctl auth init
```

## Quick Deployment

### 1. Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings
```

### 2. Deploy to DigitalOcean

```bash
chmod +x scripts/deploy-digitalocean.sh
./scripts/deploy-digitalocean.sh
```

### 3. Access the API

After deployment (~5-10 minutes):
- API: `http://<droplet-ip>:6900`
- Documentation: `http://<droplet-ip>:6900/docs`

## Remote User Access

### Option 1: Direct API Access (HTTP)

Users can access the API directly via HTTP:

```python
import requests

API_URL = "http://<droplet-ip>:6900"

# Get available endpoints
response = requests.get(f"{API_URL}/openapi.json")

# Example: Get stock data
response = requests.get(f"{API_URL}/api/v1/equity/price/quote?symbol=AAPL")
print(response.json())
```

### Option 2: HTTPS with Domain (Recommended for Production)

1. Point your domain to the droplet IP
2. SSH into the server:
   ```bash
   ssh -i ~/.ssh/openbb_do_key root@<droplet-ip>
   ```
3. Run SSL setup:
   ```bash
   curl -o setup-ssl.sh https://raw.githubusercontent.com/<repo>/scripts/setup-ssl.sh
   chmod +x setup-ssl.sh
   ./setup-ssl.sh your-domain.com your-email@example.com
   ```

### Option 3: Using ngrok (Quick Testing)

On the server:
```bash
# Install ngrok
snap install ngrok

# Expose the API
ngrok http 6900
```

## User Authentication

OpenBB supports multiple authentication methods:

### API Keys (Recommended)

Configure API keys for data providers in `/opt/openbb/.openbb_platform/user_settings.json`:

```json
{
  "credentials": {
    "fmp_api_key": "your_key",
    "polygon_api_key": "your_key"
  }
}
```

### Personal Access Token (PAT)

1. Get your PAT from https://my.openbb.co
2. Set environment variable:
   ```bash
   export OPENBB_PAT=your_pat_here
   ```

## Firewall Configuration

The deployment script configures UFW:
- Port 22 (SSH)
- Port 80 (HTTP)
- Port 443 (HTTPS)
- Port 6900 (OpenBB API)

To restrict access to specific IPs:
```bash
ufw delete allow 6900/tcp
ufw allow from <trusted-ip> to any port 6900
```

## Monitoring

### View Logs
```bash
docker logs -f openbb-odp
```

### Check Status
```bash
docker ps
curl http://localhost:6900/api/v1/health
```

## Scaling

For higher traffic:
1. Upgrade droplet size via DigitalOcean console
2. Or use DigitalOcean Kubernetes (DOKS) for auto-scaling

## Costs

Estimated monthly costs:
- s-2vcpu-4gb droplet: ~$24/month
- Bandwidth: $0.01/GB (first 4TB free)
- Total: ~$24-30/month

## Troubleshooting

### API Not Responding
```bash
# Check if container is running
docker ps

# View logs
docker logs openbb-odp

# Restart service
docker restart openbb-odp
```

### SSL Certificate Issues
```bash
# Check certificate status
certbot certificates

# Manually renew
certbot renew --force-renewal
```
