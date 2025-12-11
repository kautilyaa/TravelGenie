# AWS EC2 Deployment Guide for Mock Travel Genie

This guide explains how to deploy the fully mocked Travel Genie application on AWS EC2.

## Prerequisites

1. **AWS Account** with EC2 access
2. **AWS CLI** installed and configured (`aws configure`)
3. **EC2 Key Pair** created in your AWS region
4. **Python 3.12+** on your local machine

## Quick Start

### 1. Configure AWS Credentials

```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter default region (e.g., us-east-1)
# Enter default output format (json)
```

### 2. Set Environment Variables

```bash
export AWS_REGION="us-east-1"
export KEY_NAME="your-key-name"  # Your EC2 key pair name
export INSTANCE_TYPE="t3.medium"  # Optional, defaults to t3.medium
```

### 3. Deploy

```bash
cd mock_application/deployments/aws
chmod +x deploy_aws.sh
./deploy_aws.sh
```

The script will:
- Create a security group
- Launch an EC2 instance
- Install dependencies
- Configure the application
- Start the service

### 4. Access the Application

After deployment, you'll see the public IP address. Access the application at:
```
http://<PUBLIC_IP>:8501
```

## Manual Deployment

If you prefer manual deployment:

### 1. Launch EC2 Instance

```bash
aws ec2 run-instances \
    --image-id ami-0c55b159cbfafe1f0 \
    --instance-type t3.medium \
    --key-name your-key-name \
    --security-groups travel-genie-sg
```

### 2. SSH into Instance

```bash
ssh -i ~/.ssh/your-key.pem ec2-user@<PUBLIC_IP>
```

### 3. Install Dependencies

```bash
sudo yum update -y
sudo yum install -y python3.12 python3.12-pip
pip3.12 install --user streamlit pyyaml requests psutil
```

### 4. Copy Application Files

From your local machine:
```bash
scp -r mock_application ec2-user@<PUBLIC_IP>:~/
```

### 5. Configure and Run

```bash
cd ~/mock_application
# Edit config/app_config.yaml to set platform: aws
python3.12 -m streamlit run travel_genie_mock.py --server.port=8501 --server.address=0.0.0.0
```

## Configuration

Edit `config/app_config.yaml`:

```yaml
use_mock_llm: true
platform: aws
platform_tag: aws-us-east-1
aws:
  region: us-east-1
  enable_cloudwatch: false  # Set to true for CloudWatch metrics
```

## Monitoring

### View Logs

```bash
ssh ec2-user@<PUBLIC_IP>
journalctl -u travel-genie-mock -f
```

### CloudWatch Metrics

If CloudWatch is enabled, metrics will be available in:
- CloudWatch Console → Metrics → TravelGenie/Mock
- CloudWatch Logs → /travel-genie-mock

## Cost Estimation

Approximate costs per hour:
- **t3.micro**: $0.0104/hour (~$7.50/month)
- **t3.small**: $0.0208/hour (~$15/month)
- **t3.medium**: $0.0416/hour (~$30/month)
- **t3.large**: $0.0832/hour (~$60/month)

## Stopping/Starting Instance

```bash
# Stop instance
aws ec2 stop-instances --instance-ids <INSTANCE_ID>

# Start instance
aws ec2 start-instances --instance-ids <INSTANCE_ID>

# Terminate instance (destroys it permanently)
aws ec2 terminate-instances --instance-ids <INSTANCE_ID>
```

## Troubleshooting

### Cannot connect to application

1. Check security group allows port 8501
2. Verify instance is running: `aws ec2 describe-instances --instance-ids <INSTANCE_ID>`
3. Check service status: `ssh ec2-user@<IP> 'systemctl status travel-genie-mock'`

### High latency

1. Check instance type (upgrade if needed)
2. Monitor CloudWatch metrics for resource usage
3. Check application logs for errors

### Metrics not appearing in CloudWatch

1. Verify IAM role has CloudWatch permissions
2. Check `enable_cloudwatch: true` in config
3. Verify region matches CloudWatch region

## Advantages of AWS Deployment

- **Production-grade infrastructure**: Reliable, scalable, enterprise-ready
- **Auto-scaling**: Automatically scale based on demand
- **Monitoring**: CloudWatch provides comprehensive monitoring
- **High availability**: Multi-AZ deployment options
- **Security**: IAM, VPC, security groups
- **Persistent storage**: EBS volumes for data persistence
- **Load balancing**: ALB/ELB for traffic distribution
- **Enterprise support**: 24/7 support and SLAs
