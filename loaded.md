Gathering project details for local and AWS deployment.


[7 tools called]

## Quick summary
FastAPI app using Claude API (via MCP) and free travel APIs. Setup is mostly in place.

## Local deployment

### 1. Prerequisites
```bash
# Check Python version
python3.12 --version  # Should be 3.12.x

# If not installed (macOS):
brew install python@3.12
```

### 2. Setup steps

1. Create virtual environment:
```bash
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp env.example .env
# Edit .env and add your API keys
```

4. Register required API keys:
   - Claude (Anthropic): https://console.anthropic.com/
   - OpenTripMap: https://opentripmap.io/product
   - OpenRouteService: https://openrouteservice.org/dev/#/signup
   - Unsplash: https://unsplash.com/developers
   - Eventbrite (optional): https://www.eventbrite.com/platform

5. Run the application:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

6. Test it:
```bash
# Health check
curl http://localhost:8000/health

# Query
curl "http://localhost:8000/query?q=weather in Paris&lat=48.8566&lon=2.3522"

# View API docs
open http://localhost:8000/docs
```

---

## AWS deployment options

### Option 1: Elastic Beanstalk (easiest)
1. Install EB CLI:
```bash
pip install awsebcli
```

2. Initialize:
```bash
eb init -p python-3.12 travelgenie
eb create travelgenie-env
eb setenv ANTHROPIC_API_KEY=xxx OPENTRIPMAP_KEY=xxx ...
eb open
```

3. Add `.ebextensions/python.config`:
```yaml
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: main:app
```

Pros: Easy, auto-scaling, load balancing  
Cons: Costs ~$15–30/month

---

### Option 2: EC2 (manual control)
1. Launch an EC2 instance (Ubuntu 22.04 LTS, t3.small or larger)
2. SSH and set up:
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.12
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install python3.12 python3.12-venv python3.12-dev -y

# Install nginx
sudo apt install nginx -y

# Clone your repo
git clone https://github.com/yourusername/travelgenie.git
cd travelgenie
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env file
nano .env  # Add your API keys
```

3. Create systemd service (`sudo nano /etc/systemd/system/travelgenie.service`):
```ini
[Unit]
Description=TravelGenie FastAPI
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/travelgenie
Environment="PATH=/home/ubuntu/travelgenie/venv/bin"
ExecStart=/home/ubuntu/travelgenie/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

4. Start the service:
```bash
sudo systemctl start travelgenie
sudo systemctl enable travelgenie
```

5. Configure Nginx (`sudo nano /etc/nginx/sites-available/travelgenie`):
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable and restart nginx:
```bash
sudo ln -s /etc/nginx/sites-available/travelgenie /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

6. Configure security:
   - Open ports 80/443 in EC2 Security Group
   - Use AWS Certificate Manager for HTTPS
   - Set up a domain with Route 53

Cost: ~$10–20/month (depends on instance size)

---

### Option 3: Docker + ECS
1. Create `Dockerfile`:
```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

2. Create `.dockerignore`:
```
venv/
__pycache__/
*.pyc
.env
.git/
logs/
data/
.idea/
```

3. Build and push to ECR:
```bash
aws ecr create-repository --repository-name travelgenie
aws ecr get-login-password | docker login --username AWS --password-stdin YOUR-AWS-ACCOUNT.dkr.ecr.REGION.amazonaws.com
docker build -t travelgenie .
docker tag travelgenie:latest YOUR-AWS-ACCOUNT.dkr.ecr.REGION.amazonaws.com/travelgenie:latest
docker push YOUR-AWS-ACCOUNT.dkr.ecr.REGION.amazonaws.com/travelgenie:latest
```

4. Create an ECS service:
   - Define task with environment variables
   - Set ALB as target
   - Configure auto-scaling

---

## Production readiness

### Security
1. Add a `.gitignore` entry for `.env`
2. Store secrets in AWS Secrets Manager or Parameter Store
3. Use a stronger `SECRET_KEY`
4. Set HTTPS/TLS and require authentication for /docs
5. Review CORS origins

### Performance
1. Use Gunicorn workers:
```bash
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

2. Replace in-memory cache with Redis:
```bash
# Update .env
CACHE_BACKEND=redis
REDIS_URL=redis://your-redis-endpoint:6379/0
```

3. Consider PostgreSQL for scaling

### Monitoring
1. CloudWatch logs and metrics
2. Set up health checks
3. Add Sentry or similar
4. Implement rate limiting

---

## Deployment comparison

| Option | Cost/Month | Difficulty | Scalability | Control |
|--------|-----------|-----------|-------------|---------|
| Local | $0 | Easy | None | Full |
| Elastic Beanstalk | $15–30 | Easy | Auto | Medium |
| EC2 | $10–20 | Medium | Manual | High |
| ECS + Fargate | $20–40 | Hard | Auto | High |

---

## Recommended path
1. Start local for development
2. Deploy to Elastic Beanstalk or Render for initial production (simpler than EC2)
3. Move to EC2 + Docker if you need more control
4. ECS for containerized, auto-scaling services

Should I generate a deployment script for any of these?