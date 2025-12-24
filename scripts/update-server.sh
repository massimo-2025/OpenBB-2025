#!/bin/bash
# Run this ON the DigitalOcean server to pull latest changes from GitHub

set -e

cd /opt/openbb

echo "Pulling latest changes from GitHub..."
git pull origin main

echo "Rebuilding and restarting containers..."
docker compose down
docker compose up -d --build

echo "Done! Checking status..."
docker ps
