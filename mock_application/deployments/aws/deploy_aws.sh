#!/bin/bash
# Deploy Mock Travel Genie to AWS EC2
# This script sets up and deploys the fully mocked Travel Genie application on EC2

set -e

echo "=========================================="
echo "Deploying Mock Travel Genie to AWS EC2"
echo "=========================================="

# Configuration
INSTANCE_TYPE="${INSTANCE_TYPE:-t3.medium}"
KEY_NAME="${KEY_NAME:-your-key-name}"
SECURITY_GROUP="${SECURITY_GROUP:-travel-genie-sg}"
REGION="${AWS_REGION:-us-east-1}"

# Get project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DEPLOY_DIR="$PROJECT_ROOT/deployments/aws"

echo "Project root: $PROJECT_ROOT"
echo "Deployment directory: $DEPLOY_DIR"

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo "Error: AWS CLI not found. Please install it first."
    exit 1
fi

# Create security group if it doesn't exist
echo "Creating security group..."
aws ec2 create-security-group \
    --group-name "$SECURITY_GROUP" \
    --description "Security group for Travel Genie Mock" \
    2>/dev/null || echo "Security group already exists"

# Allow SSH and HTTP traffic
aws ec2 authorize-security-group-ingress \
    --group-name "$SECURITY_GROUP" \
    --protocol tcp \
    --port 22 \
    --cidr 0.0.0.0/0 \
    2>/dev/null || echo "SSH rule already exists"

aws ec2 authorize-security-group-ingress \
    --group-name "$SECURITY_GROUP" \
    --protocol tcp \
    --port 8501 \
    --cidr 0.0.0.0/0 \
    2>/dev/null || echo "Streamlit port rule already exists"

# Launch EC2 instance
echo "Launching EC2 instance..."
INSTANCE_ID=$(aws ec2 run-instances \
    --image-id ami-0c55b159cbfafe1f0 \
    --instance-type "$INSTANCE_TYPE" \
    --key-name "$KEY_NAME" \
    --security-groups "$SECURITY_GROUP" \
    --region "$REGION" \
    --query 'Instances[0].InstanceId' \
    --output text)

echo "Instance ID: $INSTANCE_ID"

# Wait for instance to be running
echo "Waiting for instance to be running..."
aws ec2 wait instance-running --instance-ids "$INSTANCE_ID" --region "$REGION"

# Get public IP
PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids "$INSTANCE_ID" \
    --region "$REGION" \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text)

echo "Public IP: $PUBLIC_IP"

# Wait for SSH to be available
echo "Waiting for SSH to be available..."
sleep 30

# Copy files to instance
echo "Copying files to instance..."
scp -r "$PROJECT_ROOT/mock_application" "ec2-user@$PUBLIC_IP:~/"
scp "$PROJECT_ROOT/requirements.txt" "ec2-user@$PUBLIC_IP:~/mock_application/" || true

# Run setup on instance
echo "Running setup on instance..."
ssh "ec2-user@$PUBLIC_IP" << ENDSSH
cd ~/mock_application

# Install Python 3.12 if needed
sudo yum update -y
sudo yum install -y python3.12 python3.12-pip

# Install dependencies
pip3.12 install --user -r requirements.txt streamlit

# Update config for AWS
cat > config/app_config.yaml << EOF
use_mock_llm: true
platform: aws
platform_tag: aws-$REGION
aws:
  region: $REGION
  enable_cloudwatch: false
EOF

# Create systemd service
sudo tee /etc/systemd/system/travel-genie-mock.service > /dev/null << EOSERVICE
[Unit]
Description=Travel Genie Mock Application
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/mock_application
ExecStart=/usr/bin/python3.12 -m streamlit run travel_genie_mock.py --server.port=8501 --server.address=0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
EOSERVICE

sudo systemctl daemon-reload
sudo systemctl enable travel-genie-mock
sudo systemctl start travel-genie-mock

echo "Setup complete!"
ENDSSH

echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo "Instance ID: $INSTANCE_ID"
echo "Public IP: $PUBLIC_IP"
echo "Access the application at: http://$PUBLIC_IP:8501"
echo ""
echo "To SSH into the instance:"
echo "  ssh -i ~/.ssh/$KEY_NAME.pem ec2-user@$PUBLIC_IP"
echo ""
echo "To view logs:"
echo "  ssh ec2-user@$PUBLIC_IP 'journalctl -u travel-genie-mock -f'"
echo ""
echo "To stop the instance:"
echo "  aws ec2 stop-instances --instance-ids $INSTANCE_ID --region $REGION"
