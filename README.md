# OpenBB Open Data Platform - DigitalOcean Deployment

Deploy the OpenBB Open Data Platform (ODP) on DigitalOcean for remote access.

## Quick Start

### Local Development

```bash
# Set up local environment
chmod +x scripts/setup-local.sh
./scripts/setup-local.sh

# Activate environment
source venv/bin/activate
```

### Deploy to DigitalOcean

```bash
# 1. Install doctl (DigitalOcean CLI)
# macOS: brew install doctl
# Linux: snap install doctl

# 2. Authenticate
doctl auth init

# 3. Configure
cp .env.example .env
# Edit .env with your settings

# 4. Deploy
chmod +x scripts/deploy-digitalocean.sh
./scripts/deploy-digitalocean.sh
```

## Project Structure

```
OpenBB-2025/
├── docker/
│   ├── Dockerfile           # OpenBB container image
│   └── docker-compose.yml   # Multi-service deployment
├── config/
│   ├── user_settings.json   # OpenBB configuration
│   └── nginx.conf           # Reverse proxy config
├── scripts/
│   ├── setup-local.sh       # Local development setup
│   ├── deploy-digitalocean.sh  # DO deployment
│   └── setup-ssl.sh         # SSL certificate setup
├── docs/
│   ├── DEPLOYMENT.md        # Full deployment guide
│   └── USER_ACCESS.md       # Remote access guide
├── .env.example             # Environment template
└── README.md
```

## Requirements

- Python 3.10+
- Docker (for containerized deployment)
- doctl CLI (for DigitalOcean deployment)

## Documentation

- [Deployment Guide](docs/DEPLOYMENT.md)
- [User Access Guide](docs/USER_ACCESS.md)
- [OpenBB Documentation](https://docs.openbb.co)

## Costs

DigitalOcean Droplet (s-2vcpu-4gb): ~$24/month
