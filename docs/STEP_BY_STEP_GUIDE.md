# Step-by-Step Guide: Deploy OpenBB ODP on DigitalOcean

This guide walks you through deploying OpenBB Open Data Platform on DigitalOcean from scratch.

---

## Prerequisites

- A **GitHub account** (for code syncing)
- A **DigitalOcean account** (sign up at https://digitalocean.com)
- A terminal/command line
- Basic familiarity with command line operations

---

## Step 0: Push Project to GitHub

### 0a. Create a GitHub Repository

1. Go to https://github.com/new
2. Name it `OpenBB-2025` (or your preferred name)
3. Keep it **Public** (or Private if you prefer)
4. **Don't** initialize with README (we already have one)
5. Click **Create repository**

### 0b. Push Your Local Code

```bash
cd /home/massimo/.claude/projects/web-projects/OpenBB-2025

# Add all files
git add .

# Commit
git commit -m "Initial commit: OpenBB ODP deployment setup"

# Add remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/OpenBB-2025.git

# Push
git branch -M main
git push -u origin main
```

### 0c. Verify

Go to `https://github.com/YOUR_USERNAME/OpenBB-2025` and confirm your files are there.

---

## Step 1: Create a DigitalOcean Account & API Token

1. Go to https://digitalocean.com and create an account
2. Navigate to **API** in the left sidebar (or go to https://cloud.digitalocean.com/account/api/tokens)
3. Click **Generate New Token**
4. Name it (e.g., "openbb-deployment")
5. Select **Full Access** (Read and Write)
6. Click **Generate Token**
7. **IMPORTANT**: Copy and save the token immediately - you won't see it again!

---

## Step 2: Install the DigitalOcean CLI (doctl)

### On macOS:
```bash
brew install doctl
```

### On Ubuntu/Debian Linux:
```bash
sudo snap install doctl
```

### On Windows:
Download from https://github.com/digitalocean/doctl/releases

### Verify Installation:
```bash
doctl version
```

---

## Step 3: Authenticate doctl with Your API Token

```bash
doctl auth init
```

When prompted, paste your API token from Step 1.

Verify authentication:
```bash
doctl account get
```

You should see your account email and droplet limit.

---

## Step 4: Configure Your Deployment

Navigate to the project directory:
```bash
cd /home/massimo/.claude/projects/web-projects/OpenBB-2025
```

Create your environment file:
```bash
cp .env.example .env
```

Edit the `.env` file:
```bash
nano .env
```

Update these values:
```
# Required: Get from https://my.openbb.co
OPENBB_PAT=your_personal_access_token_here

# Optional: Customize deployment
DO_DROPLET_NAME=openbb-server
DO_REGION=nyc1
DO_SIZE=s-2vcpu-4gb
```

### Available Regions:
| Code | Location |
|------|----------|
| nyc1, nyc3 | New York |
| sfo3 | San Francisco |
| ams3 | Amsterdam |
| sgp1 | Singapore |
| lon1 | London |
| fra1 | Frankfurt |
| tor1 | Toronto |
| blr1 | Bangalore |

### Available Sizes:
| Code | Specs | Price |
|------|-------|-------|
| s-1vcpu-2gb | 1 vCPU, 2GB RAM | $12/mo |
| s-2vcpu-4gb | 2 vCPU, 4GB RAM | $24/mo (recommended) |
| s-4vcpu-8gb | 4 vCPU, 8GB RAM | $48/mo |

---

## Step 5: Deploy to DigitalOcean

Run the deployment script:
```bash
./scripts/deploy-digitalocean.sh
```

The script will:
1. Create an SSH key for secure access
2. Add the SSH key to your DigitalOcean account
3. Create a new Droplet with Docker pre-installed
4. Configure the firewall
5. Install and start OpenBB

**This takes about 5-10 minutes.** Wait for the script to complete.

### Expected Output:
```
=== Droplet Created Successfully ===
Droplet ID: 123456789
Droplet IP: 167.99.123.45

=== Access Information ===
SSH Access:
  ssh -i ~/.ssh/openbb_do_key root@167.99.123.45

OpenBB API (after ~5 minutes for setup):
  http://167.99.123.45:6900

API Documentation:
  http://167.99.123.45:6900/docs
```

---

## Step 6: Verify the Deployment

### Wait for Setup to Complete (~5 minutes)

SSH into your server:
```bash
ssh -i ~/.ssh/openbb_do_key root@<YOUR_DROPLET_IP>
```

Check if Docker container is running:
```bash
docker ps
```

You should see:
```
CONTAINER ID   IMAGE           STATUS          PORTS                    NAMES
abc123def456   python:3.11     Up 2 minutes    0.0.0.0:6900->6900/tcp   openbb-odp
```

Check logs:
```bash
docker logs openbb-odp
```

Exit SSH:
```bash
exit
```

---

## Step 7: Test the API

### From Your Local Machine:

Test if API is responding:
```bash
curl http://<YOUR_DROPLET_IP>:6900/api/v1/coverage/providers
```

Open the API documentation in your browser:
```
http://<YOUR_DROPLET_IP>:6900/docs
```

---

## Step 8: (Optional) Set Up HTTPS with a Domain

### 8a. Point Your Domain to the Droplet

1. Go to your domain registrar (GoDaddy, Namecheap, Cloudflare, etc.)
2. Add an A record:
   - **Type**: A
   - **Name**: openbb (or @ for root domain)
   - **Value**: Your Droplet IP
   - **TTL**: 300 (or Auto)

3. Wait for DNS propagation (5-30 minutes)

Verify:
```bash
ping openbb.yourdomain.com
```

### 8b. Install SSL Certificate

SSH into your server:
```bash
ssh -i ~/.ssh/openbb_do_key root@<YOUR_DROPLET_IP>
```

Run the SSL setup script:
```bash
# Download the script
curl -o /opt/openbb/setup-ssl.sh https://raw.githubusercontent.com/YOUR_REPO/scripts/setup-ssl.sh

# Or copy it manually and run:
chmod +x /opt/openbb/setup-ssl.sh
./setup-ssl.sh openbb.yourdomain.com your-email@example.com
```

Your API is now available at:
```
https://openbb.yourdomain.com
https://openbb.yourdomain.com/docs
```

---

## Step 9: Configure Data Provider API Keys (Optional)

SSH into your server:
```bash
ssh -i ~/.ssh/openbb_do_key root@<YOUR_DROPLET_IP>
```

Edit the configuration:
```bash
nano /opt/openbb/user_settings.json
```

Add your API keys:
```json
{
  "credentials": {
    "fmp_api_key": "your_fmp_key",
    "polygon_api_key": "your_polygon_key",
    "fred_api_key": "your_fred_key"
  }
}
```

Restart the container:
```bash
docker restart openbb-odp
```

### Free API Keys:
- **FMP** (Financial Modeling Prep): https://financialmodelingprep.com/developer/docs/
- **Polygon**: https://polygon.io/
- **FRED** (Federal Reserve): https://fred.stlouisfed.org/docs/api/api_key.html

---

## Step 10: Share Access with Users

Send users this information:

**API Endpoint:**
```
http://<YOUR_DROPLET_IP>:6900
# or if using HTTPS:
https://openbb.yourdomain.com
```

**API Documentation:**
```
http://<YOUR_DROPLET_IP>:6900/docs
```

**Example Python Usage:**
```python
import requests

API_URL = "http://<YOUR_DROPLET_IP>:6900/api/v1"

# Get stock quote
response = requests.get(f"{API_URL}/equity/price/quote", params={"symbol": "AAPL"})
print(response.json())
```

---

## Troubleshooting

### Container Not Starting
```bash
ssh -i ~/.ssh/openbb_do_key root@<YOUR_DROPLET_IP>
docker logs openbb-odp
docker restart openbb-odp
```

### API Not Responding
```bash
# Check if port is open
curl http://localhost:6900/api/v1/coverage/providers

# Check firewall
ufw status
ufw allow 6900/tcp
```

### Out of Memory
Upgrade your droplet:
1. Go to DigitalOcean dashboard
2. Select your droplet
3. Click **Resize**
4. Choose a larger size
5. Click **Resize Droplet**

### Delete and Start Over
```bash
# List droplets
doctl compute droplet list

# Delete droplet
doctl compute droplet delete <DROPLET_ID>
```

---

## Managing Your Deployment

### Stop the Server (to save costs)
```bash
doctl compute droplet-action power-off <DROPLET_ID>
```

### Start the Server
```bash
doctl compute droplet-action power-on <DROPLET_ID>
```

### View Monthly Cost
```bash
doctl balance get
```

---

## Quick Reference

| Task | Command |
|------|---------|
| SSH into server | `ssh -i ~/.ssh/openbb_do_key root@<IP>` |
| View logs | `docker logs -f openbb-odp` |
| Restart OpenBB | `docker restart openbb-odp` |
| Check status | `docker ps` |
| List droplets | `doctl compute droplet list` |
| Delete droplet | `doctl compute droplet delete <ID>` |

---

## Costs Summary

| Item | Cost |
|------|------|
| Droplet (s-2vcpu-4gb) | $24/month |
| Bandwidth (first 4TB) | Free |
| Additional bandwidth | $0.01/GB |
| **Total (typical)** | **~$24/month** |

---

## Step 11: Set Up Auto-Deployment from GitHub (Optional)

This enables automatic deployment when you push to GitHub.

### 11a. Add GitHub Secrets

1. Go to your GitHub repo → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret** and add:

| Name | Value |
|------|-------|
| `DO_HOST` | Your Droplet IP (e.g., `167.99.123.45`) |
| `DO_SSH_KEY` | Contents of `~/.ssh/openbb_do_key` (private key) |

To get your private key:
```bash
cat ~/.ssh/openbb_do_key
```

### 11b. Test Auto-Deployment

Make a small change locally:
```bash
cd /home/massimo/.claude/projects/web-projects/OpenBB-2025
echo "# Updated" >> README.md
git add .
git commit -m "Test auto-deployment"
git push
```

Go to GitHub → **Actions** tab to see the deployment running.

### 11c. Manual Update (Alternative)

If not using GitHub Actions, SSH in and pull manually:
```bash
ssh -i ~/.ssh/openbb_do_key root@<YOUR_DROPLET_IP>
cd /opt/openbb
git pull origin main
cd docker
docker compose down
docker compose up -d --build
```

---

## Workflow Summary

```
Local Machine          GitHub              DigitalOcean
     │                    │                     │
     │  git push          │                     │
     ├───────────────────>│                     │
     │                    │   auto-deploy       │
     │                    ├────────────────────>│
     │                    │   (GitHub Actions)  │
     │                    │                     │
     │                    │      OR             │
     │                    │                     │
     │              ssh + git pull              │
     ├─────────────────────────────────────────>│
     │                    │                     │
```

---

## Next Steps

1. Set up monitoring with DigitalOcean Monitoring (free)
2. Configure automatic backups ($4.80/month)
3. Set up alerts for high CPU/memory usage
4. Consider using DigitalOcean Spaces for data storage

For more details, see [DEPLOYMENT.md](DEPLOYMENT.md) and [USER_ACCESS.md](USER_ACCESS.md).
