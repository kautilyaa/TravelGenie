# Google Colab Deployment Guide for Mock Travel Genie

This guide explains how to deploy the fully mocked Travel Genie application on Google Colab.

## Prerequisites

- Google account
- Access to Google Colab (free tier available)

## Quick Start

### Option 1: Using the Notebook

1. Open `colab_setup.ipynb` in Google Colab
2. Upload the `mock_application` directory to Colab
3. Run all cells in order
4. Access the application via the ngrok URL (if enabled) or Colab's built-in preview

### Option 2: Manual Setup

1. **Open Google Colab**: Go to https://colab.research.google.com

2. **Install Dependencies**:
```python
!pip install streamlit pyyaml requests psutil pyngrok -q
```

3. **Upload Files**:
   - Upload the entire `mock_application` directory
   - Or clone from repository if available

4. **Configure**:
```python
import os
os.makedirs('config', exist_ok=True)

config_content = """
use_mock_llm: true
platform: colab
platform_tag: colab-free-tier
"""

with open('config/app_config.yaml', 'w') as f:
    f.write(config_content)
```

5. **Run Application**:
```python
!streamlit run travel_genie_mock.py --server.port=7860 --server.address=0.0.0.0
```

6. **Expose Publicly (Optional)**:
```python
from pyngrok import ngrok
ngrok.set_auth_token("YOUR_NGROK_TOKEN")
public_url = ngrok.connect(7860)
print(f"Public URL: {public_url}")
```

## Configuration

Edit `config/app_config.yaml`:

```yaml
use_mock_llm: true
platform: colab
platform_tag: colab-free-tier
colab:
  port: 7860
  enable_ngrok: false
```

## Limitations

### Free Tier
- **Session timeout**: 12 hours maximum
- **Memory**: ~12.7 GB RAM
- **Disk**: ~107 GB storage
- **GPU**: Limited availability, may disconnect
- **CPU**: Shared resources, variable performance

### Pro Tier ($9.99/month)
- Longer session times
- Better GPU availability
- Priority access to resources
- More stable connections

## Monitoring

Metrics are collected automatically and saved to `metrics.json` in the Colab environment.

To view metrics:
```python
import json
with open('metrics.json', 'r') as f:
    metrics = json.load(f)
    print(json.dumps(metrics, indent=2))
```

## Accessing the Application

### Via ngrok (Recommended)
1. Get ngrok token from https://dashboard.ngrok.com
2. Set token in notebook
3. Access via ngrok URL

### Via Colab Preview
1. Click on the localhost URL shown in Streamlit output
2. Use Colab's built-in preview (may have limitations)

## Troubleshooting

### Session Disconnected
- Colab free tier sessions timeout after inactivity
- Solution: Use Colab Pro or restart session

### Out of Memory
- Free tier has limited RAM
- Solution: Reduce concurrent requests or upgrade to Pro

### Port Already in Use
- Change port in config: `colab.port: 7861`
- Or kill existing process: `!pkill -f streamlit`

### ngrok Not Working
- Verify ngrok token is correct
- Check if ngrok is installed: `!pip install pyngrok`
- Try restarting ngrok connection

## Cost Comparison

- **Free Tier**: $0/month (with limitations)
- **Pro Tier**: $9.99/month (better resources)
- **Pro+ Tier**: $49.99/month (even better resources)

## Advantages and Disadvantages

### Advantages
- **Free tier available**: No cost for basic testing
- **Easy setup**: No infrastructure management
- **GPU access**: Free GPU for testing (limited)
- **No API keys needed**: Fully mocked application

### Disadvantages
- **Session timeouts**: 12-hour limit on free tier
- **Resource limits**: Shared CPU, limited memory
- **No persistence**: Files lost when session ends
- **Unreliable**: May disconnect unexpectedly
- **No auto-scaling**: Manual restart required
- **Limited monitoring**: Basic resource metrics only

## Best Use Cases

- **Development and testing**: Quick prototyping
- **Demonstrations**: Showcasing the application
- **Learning**: Understanding the system
- **Temporary deployments**: Short-term testing

## Not Suitable For

- **Production workloads**: Unreliable and limited
- **Long-running services**: Session timeouts
- **High-traffic applications**: Resource constraints
- **Enterprise use**: No SLAs or support
