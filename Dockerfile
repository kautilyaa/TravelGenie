FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements.txt
COPY requirements.txt .

# Install the specified packages
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY slack_bot.py .
COPY claude_orchestrator.py .
COPY dynamodb_database.py .
COPY servers/ ./servers/

# Add environment variables from .env file  
RUN export $(cat .env | xargs)  

# Copy .env 
# COPY .env .

# Run the Slack bot
CMD ["python", "slack_bot.py"]