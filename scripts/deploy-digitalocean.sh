#!/bin/bash
set -e

echo "=== OpenBB DigitalOcean Deployment Script ==="
echo ""

# Load environment variables
if [ -f ../.env ]; then
    source ../.env
fi

# Configuration
DROPLET_NAME="${DO_DROPLET_NAME:-openbb-server}"
REGION="${DO_REGION:-nyc1}"
SIZE="${DO_SIZE:-s-2vcpu-4gb}"
IMAGE="${DO_IMAGE:-docker-20-04}"
GITHUB_REPO="${GITHUB_REPO:-}"

# Check for GitHub repo
if [ -z "$GITHUB_REPO" ]; then
    echo "Warning: GITHUB_REPO not set in .env"
    echo "Example: GITHUB_REPO=username/OpenBB-2025"
    echo ""
    read -p "Enter your GitHub repo (username/repo): " GITHUB_REPO
fi

# Check for doctl CLI
if ! command -v doctl &> /dev/null; then
    echo "Error: doctl (DigitalOcean CLI) is not installed."
    echo ""
    echo "Install it using:"
    echo "  - macOS: brew install doctl"
    echo "  - Linux: snap install doctl"
    echo "  - Or download from: https://github.com/digitalocean/doctl/releases"
    echo ""
    echo "After installation, authenticate with:"
    echo "  doctl auth init"
    exit 1
fi

# Verify authentication
echo "Verifying DigitalOcean authentication..."
if ! doctl account get &> /dev/null; then
    echo "Error: Not authenticated with DigitalOcean."
    echo "Run: doctl auth init"
    exit 1
fi

echo "Authenticated successfully!"
echo ""

# Create SSH key if needed
SSH_KEY_PATH="$HOME/.ssh/openbb_do_key"
if [ ! -f "$SSH_KEY_PATH" ]; then
    echo "Creating SSH key for deployment..."
    ssh-keygen -t ed25519 -f "$SSH_KEY_PATH" -N "" -C "openbb-deployment"
fi

# Add SSH key to DigitalOcean if not already added
SSH_KEY_FINGERPRINT=$(ssh-keygen -l -E md5 -f "$SSH_KEY_PATH.pub" | awk '{print $2}' | sed 's/MD5://')
if ! doctl compute ssh-key list | grep -q "$SSH_KEY_FINGERPRINT"; then
    echo "Adding SSH key to DigitalOcean..."
    SSH_KEY_CONTENT=$(cat "$SSH_KEY_PATH.pub")
    doctl compute ssh-key create openbb-deploy-key --public-key "$SSH_KEY_CONTENT"
fi

SSH_KEY_ID=$(doctl compute ssh-key list --format ID,FingerPrint --no-header | grep "$SSH_KEY_FINGERPRINT" | awk '{print $1}')

echo ""
echo "Creating Droplet with the following configuration:"
echo "  Name: $DROPLET_NAME"
echo "  Region: $REGION"
echo "  Size: $SIZE (2 vCPU, 4GB RAM)"
echo "  Image: $IMAGE"
echo ""

# Create cloud-init user data
USER_DATA=$(cat <<EOF
#!/bin/bash
set -e

# Update system
apt-get update && apt-get upgrade -y

# Docker should already be installed on docker image, but ensure docker-compose
apt-get install -y docker-compose-plugin git

# Clone from GitHub
cd /opt
git clone https://github.com/${GITHUB_REPO}.git openbb
cd /opt/openbb

# Configure firewall
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 6900/tcp
ufw --force enable

# Build and start the service
cd /opt/openbb/docker
docker compose up -d --build

echo "OpenBB deployment complete!"
EOF
)

# Create the droplet
echo "Creating Droplet..."
DROPLET_INFO=$(doctl compute droplet create "$DROPLET_NAME" \
    --region "$REGION" \
    --size "$SIZE" \
    --image "$IMAGE" \
    --ssh-keys "$SSH_KEY_ID" \
    --user-data "$USER_DATA" \
    --wait \
    --format ID,Name,PublicIPv4 \
    --no-header)

DROPLET_ID=$(echo "$DROPLET_INFO" | awk '{print $1}')
DROPLET_IP=$(echo "$DROPLET_INFO" | awk '{print $3}')

echo ""
echo "=== Droplet Created Successfully ==="
echo "Droplet ID: $DROPLET_ID"
echo "Droplet IP: $DROPLET_IP"
echo ""
echo "=== Access Information ==="
echo ""
echo "SSH Access:"
echo "  ssh -i $SSH_KEY_PATH root@$DROPLET_IP"
echo ""
echo "OpenBB API (after ~5 minutes for setup):"
echo "  http://$DROPLET_IP:6900"
echo ""
echo "API Documentation:"
echo "  http://$DROPLET_IP:6900/docs"
echo ""
echo "=== Next Steps ==="
echo "1. Wait 5-10 minutes for the server to complete setup"
echo "2. SSH into the server and verify: docker logs openbb-odp"
echo "3. Access the API at http://$DROPLET_IP:6900/docs"
echo "4. For HTTPS, see docs/DEPLOYMENT.md"
echo ""

# Save deployment info
cat > ../deployment-info.txt <<INFO
OpenBB Deployment Information
=============================
Date: $(date)
Droplet ID: $DROPLET_ID
Droplet Name: $DROPLET_NAME
Droplet IP: $DROPLET_IP
Region: $REGION
Size: $SIZE

SSH Command: ssh -i $SSH_KEY_PATH root@$DROPLET_IP
API URL: http://$DROPLET_IP:6900
API Docs: http://$DROPLET_IP:6900/docs
INFO

echo "Deployment info saved to deployment-info.txt"
