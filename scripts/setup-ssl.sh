#!/bin/bash
set -e

# This script sets up SSL certificates using Let's Encrypt on your DigitalOcean droplet
# Run this AFTER the droplet is created and you have a domain pointing to it

echo "=== SSL Certificate Setup for OpenBB ==="
echo ""

if [ -z "$1" ]; then
    echo "Usage: $0 <domain-name> [email]"
    echo "Example: $0 openbb.yourdomain.com admin@yourdomain.com"
    exit 1
fi

DOMAIN="$1"
EMAIL="${2:-admin@$DOMAIN}"

echo "Setting up SSL for: $DOMAIN"
echo "Email for notifications: $EMAIL"
echo ""

# Install certbot
apt-get update
apt-get install -y certbot python3-certbot-nginx

# Stop any running nginx container
docker stop openbb-nginx 2>/dev/null || true

# Get certificate
certbot certonly --standalone \
    -d "$DOMAIN" \
    --non-interactive \
    --agree-tos \
    --email "$EMAIL"

# Create SSL directory for nginx
mkdir -p /opt/openbb/ssl

# Copy certificates
cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem /opt/openbb/ssl/cert.pem
cp /etc/letsencrypt/live/$DOMAIN/privkey.pem /opt/openbb/ssl/key.pem

# Update nginx config
cat > /opt/openbb/nginx.conf <<NGINX
events {
    worker_connections 1024;
}

http {
    upstream openbb_api {
        server openbb-platform:6900;
    }

    server {
        listen 80;
        server_name $DOMAIN;
        return 301 https://\$host\$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name $DOMAIN;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;

        location / {
            proxy_pass http://openbb_api;
            proxy_http_version 1.1;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }
    }
}
NGINX

# Update docker-compose to include nginx
cat > /opt/openbb/docker-compose.yml <<COMPOSE
version: '3.8'

services:
  openbb-platform:
    image: python:3.11-slim
    container_name: openbb-odp
    restart: unless-stopped
    volumes:
      - openbb-data:/root/.openbb_platform
    environment:
      - OPENBB_API_HOST=0.0.0.0
      - OPENBB_API_PORT=6900
    command: >
      bash -c "pip install openbb &&
               python -c 'from openbb import obb; import uvicorn; uvicorn.run(\"openbb_core.api.rest_api:app\", host=\"0.0.0.0\", port=6900)'"
    networks:
      - openbb-net

  nginx:
    image: nginx:alpine
    container_name: openbb-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - openbb-platform
    networks:
      - openbb-net

volumes:
  openbb-data:

networks:
  openbb-net:
    driver: bridge
COMPOSE

# Restart services
cd /opt/openbb
docker compose down
docker compose up -d

# Set up auto-renewal
echo "0 0 1 * * certbot renew --quiet && cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem /opt/openbb/ssl/cert.pem && cp /etc/letsencrypt/live/$DOMAIN/privkey.pem /opt/openbb/ssl/key.pem && docker restart openbb-nginx" | crontab -

echo ""
echo "=== SSL Setup Complete ==="
echo ""
echo "Your OpenBB API is now available at:"
echo "  https://$DOMAIN"
echo "  https://$DOMAIN/docs"
echo ""
