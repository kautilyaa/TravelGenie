#!/bin/bash
# Zaratan Setup Script for Mock Travel Genie
# Sets up the mock Travel Genie application on Zaratan HPC cluster

set -e

echo "=========================================="
echo "Setting up Mock Travel Genie on Zaratan"
echo "=========================================="

# Configuration
PARTITION="${PARTITION:-gpu}"
GPUS="${GPUS:-1}"
CPUS="${CPUS:-8}"
MEMORY="${MEMORY:-32G}"
TIME_LIMIT="${TIME_LIMIT:-24:00:00}"

# Check if we're on Zaratan
if [[ ! "$HOSTNAME" == *"zaratan"* ]]; then
    echo "Warning: This script is designed for Zaratan HPC cluster"
    echo "Current hostname: $HOSTNAME"
fi

# Load modules
echo "Loading modules..."
module load python/3.12 || module load python3/3.12 || echo "Python module not found, using system Python"

# Create directory for mock_application
echo "Creating directories..."
mkdir -p ~/mock_application
cd ~/mock_application

# Install dependencies in user space
echo "Installing dependencies..."
pip install --user streamlit pyyaml requests psutil

# Create config directory
mkdir -p config

# Create app_config.yaml
cat > config/app_config.yaml << EOF
use_mock_llm: true
platform: zaratan
platform_tag: zaratan-gpu

zaratan:
  partition: $PARTITION
  gpus: $GPUS
  cpus: $CPUS
  memory: $MEMORY
  time_limit: $TIME_LIMIT
  enable_slurm_metrics: true

metrics:
  enabled: true
  save_to_file: true
  metrics_file: "metrics.json"

reporting:
  enabled: true
  output_format: ["markdown", "html"]
  output_directory: "reports"
EOF

echo ""
echo "Setup complete!"
echo ""
echo "To start the application, submit a SLURM job:"
echo "  sbatch slurm_job.sh"
echo ""
echo "Or run interactively:"
echo "  srun --partition=$PARTITION --gres=gpu:$GPUS --cpus-per-task=$CPUS --mem=$MEMORY --time=$TIME_LIMIT --pty bash"
echo "  cd ~/mock_application"
echo "  streamlit run travel_genie_mock.py --server.port=8501 --server.address=0.0.0.0"
echo ""
echo "Note: Make sure to copy the mock_application files to ~/mock_application first!"
