# Deployment Guide

Detailed deployment instructions for various platforms.

## Table of Contents

1. [Local Development](#local-development)
2. [ngrok (Quick Testing)](#ngrok-quick-testing)
3. [Railway](#railway)
4. [Render](#render)
5. [Google Cloud Run](#google-cloud-run)
6. [Docker Deployment](#docker-deployment)
7. [AWS EC2](#aws-ec2)

---

## Local Development

Perfect for development and testing.

```bash
# Setup
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
playwright install chromium

# Configure
cp .env.example .env
# Edit .env with your credentials

# Run
python app.py
```

**Pros:** Easy setup, full control
**Cons:** Not accessible from internet, must keep computer on

---

## ngrok (Quick Testing)

Expose your local server to the internet instantly.

### Setup

1. Download ngrok: https://ngrok.com/download
2. Sign up for free account
3. Install authtoken:
   ```bash
   ngrok authtoken YOUR_AUTH_TOKEN
   ```

### Run

```bash
# Terminal 1: Start your app
python app.py

# Terminal 2: Start ngrok
ngrok http 8000
```

You'll get a URL like: `https://abc123.ngrok-free.app`

**Use this URL in your Google Form:** `https://abc123.ngrok-free.app/quiz`

### Pros
- Instant deployment
- Free tier available
- No server setup needed

### Cons
- URL changes on restart (unless you have paid plan)
- Computer must stay on
- Free tier has limits

---

## Railway

Cloud deployment with automatic HTTPS and easy setup.

### Setup

1. Install Railway CLI:
   ```bash
   npm i -g @railway/cli
   ```

2. Login:
   ```bash
   railway login
   ```

3. Initialize project:
   ```bash
   railway init
   ```

4. Add environment variables:
   ```bash
   railway variables set EMAIL="your-email@example.com"
   railway variables set SECRET="your-secret"
   railway variables set ANTHROPIC_API_KEY="sk-ant-..."
   ```

5. Deploy:
   ```bash
   railway up
   ```

6. Get your URL:
   ```bash
   railway domain
   ```

### Pros
- Free tier: $5 credit/month
- Automatic HTTPS
- Easy deployment
- Built-in monitoring

### Cons
- Credit-based (not unlimited free)
- May need credit card for verification

---

## Render

Free web service deployment with automatic deploys from Git.

### Setup

1. Create account at https://render.com

2. Click "New +" → "Web Service"

3. Connect your GitHub repository

4. Configure:
   - **Name:** llm-quiz-solver
   - **Environment:** Python 3
   - **Build Command:**
     ```bash
     pip install -r requirements.txt && playwright install chromium && playwright install-deps chromium
     ```
   - **Start Command:**
     ```bash
     python app.py
     ```

5. Add Environment Variables:
   - `EMAIL` = your-email@example.com
   - `SECRET` = your-secret
   - `ANTHROPIC_API_KEY` = sk-ant-...
   - `PYTHON_VERSION` = 3.11.0

6. Click "Create Web Service"

Your app will be at: `https://llm-quiz-solver.onrender.com`

### Pros
- Free tier available
- Automatic deploys on git push
- Free SSL
- No credit card required

### Cons
- Free tier spins down after inactivity (takes ~30s to wake up)
- Limited build minutes on free tier

### Tips
- Keep service alive with UptimeRobot pinging /health every 5 minutes
- Deploy at least 1 hour before quiz time to ensure it's warmed up

---

## Google Cloud Run

Serverless container deployment.

### Setup

1. Install Google Cloud SDK:
   ```bash
   curl https://sdk.cloud.google.com | bash
   ```

2. Initialize and login:
   ```bash
   gcloud init
   gcloud auth login
   ```

3. Create project (or use existing):
   ```bash
   gcloud projects create llm-quiz-solver
   gcloud config set project llm-quiz-solver
   ```

4. Enable required APIs:
   ```bash
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable run.googleapis.com
   ```

5. Create .env.yaml:
   ```yaml
   EMAIL: "your-email@example.com"
   SECRET: "your-secret"
   ANTHROPIC_API_KEY: "sk-ant-..."
   ```

6. Deploy:
   ```bash
   gcloud run deploy llm-quiz-solver \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --env-vars-file .env.yaml \
     --memory 1Gi \
     --timeout 300
   ```

Your app will be at: `https://llm-quiz-solver-xxx-uc.a.run.app`

### Pros
- Scalable
- Pay only for use
- Free tier: 2M requests/month
- Google reliability

### Cons
- More complex setup
- Requires GCP account
- May need credit card

---

## Docker Deployment

Run anywhere Docker is supported.

### Build and Run Locally

```bash
# Build
docker build -t llm-quiz-solver .

# Run
docker run -d \
  --name quiz-solver \
  -p 8000:8000 \
  -e EMAIL="your-email@example.com" \
  -e SECRET="your-secret" \
  -e ANTHROPIC_API_KEY="sk-ant-..." \
  llm-quiz-solver
```

### Using Docker Compose

```bash
# Create .env file first

# Run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Deploy to Docker Hub

```bash
# Login
docker login

# Tag
docker tag llm-quiz-solver your-username/llm-quiz-solver:latest

# Push
docker push your-username/llm-quiz-solver:latest
```

Then deploy to any Docker-compatible host (DigitalOcean, Linode, etc.)

### Pros
- Portable
- Consistent environment
- Works everywhere

### Cons
- Requires Docker knowledge
- Need hosting for public access

---

## AWS EC2

Deploy on Amazon EC2 instance.

### Setup

1. Launch EC2 instance:
   - AMI: Ubuntu 22.04
   - Instance type: t2.micro (free tier)
   - Security group: Allow port 8000 (or use nginx on 80/443)

2. SSH into instance:
   ```bash
   ssh -i your-key.pem ubuntu@ec2-xx-xx-xx-xx.compute.amazonaws.com
   ```

3. Install dependencies:
   ```bash
   sudo apt update
   sudo apt install -y python3.11 python3.11-venv python3-pip git
   ```

4. Clone and setup:
   ```bash
   git clone your-repo-url
   cd LLM-Analysis-Quiz
   python3.11 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   playwright install chromium
   playwright install-deps chromium
   ```

5. Configure .env:
   ```bash
   cp .env.example .env
   nano .env  # Edit with your values
   ```

6. Run with systemd (keeps running after logout):
   ```bash
   sudo nano /etc/systemd/system/quiz-solver.service
   ```

   ```ini
   [Unit]
   Description=LLM Quiz Solver
   After=network.target

   [Service]
   Type=simple
   User=ubuntu
   WorkingDirectory=/home/ubuntu/LLM-Analysis-Quiz
   Environment="PATH=/home/ubuntu/LLM-Analysis-Quiz/venv/bin"
   ExecStart=/home/ubuntu/LLM-Analysis-Quiz/venv/bin/python app.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable quiz-solver
   sudo systemctl start quiz-solver
   ```

7. Setup nginx (optional, for port 80):
   ```bash
   sudo apt install nginx
   sudo nano /etc/nginx/sites-available/quiz-solver
   ```

   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

   ```bash
   sudo ln -s /etc/nginx/sites-available/quiz-solver /etc/nginx/sites-enabled/
   sudo systemctl restart nginx
   ```

### Pros
- Full control
- Free tier for 12 months
- Can handle high load

### Cons
- More setup required
- Need to manage server
- Security configuration needed

---

## Monitoring and Maintenance

### Health Checks

All platforms support health checks. Configure:

- **Endpoint:** `/health`
- **Interval:** 30 seconds
- **Timeout:** 10 seconds
- **Healthy threshold:** 2
- **Unhealthy threshold:** 3

### Logging

View logs:

- **Local:** `tail -f quiz_solver.log`
- **Docker:** `docker logs -f quiz-solver`
- **Railway:** `railway logs`
- **Render:** View in dashboard
- **Cloud Run:** Google Cloud Console
- **EC2:** `journalctl -u quiz-solver -f`

### Keeping Alive (Render free tier)

Render spins down after 15min inactivity. Use UptimeRobot:

1. Sign up at https://uptimerobot.com
2. Add monitor:
   - Type: HTTP(s)
   - URL: `https://your-app.onrender.com/health`
   - Interval: 5 minutes

---

## Pre-Quiz Checklist

- [ ] Application deployed and accessible
- [ ] Health endpoint returns 200
- [ ] Test with invalid secret (should return 403)
- [ ] Test with valid secret (should return 200)
- [ ] Logs are being written
- [ ] Environment variables set correctly
- [ ] Anthropic API key has credits
- [ ] Service will stay up during quiz time
- [ ] Monitor is set up (if using Render)
- [ ] URL submitted in Google Form

---

## Troubleshooting

### 502 Bad Gateway
- Service crashed, check logs
- Memory limit exceeded, increase allocation

### Service won't start
- Check environment variables
- Verify Playwright installed
- Check port isn't in use

### Timeout errors
- Increase timeout settings
- Check network connectivity
- Verify quiz URLs are accessible

### High costs
- Check if service is being abused
- Review API usage
- Consider adding rate limiting

---

## Cost Estimates

| Platform | Free Tier | Paid (if needed) |
|----------|-----------|------------------|
| ngrok | Limited requests | $8/month for static domain |
| Railway | $5 credit/month | $0.000463/GB-hour |
| Render | 750 hours/month | $7/month |
| Google Cloud Run | 2M requests/month | ~$0.40/1M requests |
| AWS EC2 | t2.micro free for 12mo | $8.50/month after |

**For this quiz, free tiers are more than sufficient.**

---

## Recommended Setup for Quiz

1. **Development:** Local + ngrok
2. **Production (Quiz Day):** Railway or Render
3. **Backup:** Have ngrok ready as fallback

Deploy to Railway/Render 1 day before quiz to ensure stability.
