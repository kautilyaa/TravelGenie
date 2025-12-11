#!/bin/bash
#SBATCH --job-name=travel-genie-mock
#SBATCH --output=travel-genie-mock-%j.out
#SBATCH --error=travel-genie-mock-%j.err
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=24:00:00
#SBATCH --account=your-account-name

# Load modules
module load python/3.12 || module load python3/3.12

# Set working directory
cd ~/mock_application

# Set environment variables
export PORT=8501
export HOST=0.0.0.0

# Start Streamlit application
streamlit run travel_genie_mock.py \
    --server.port=$PORT \
    --server.address=$HOST \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false

# Note: To access the application, you'll need to set up port forwarding
# From your local machine:
# ssh -L 8501:compute-node:8501 zaratan.umd.edu
# Then access at http://localhost:8501
