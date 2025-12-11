# Zaratan HPC Deployment Guide for Mock Travel Genie

This guide explains how to deploy the fully mocked Travel Genie application on Zaratan HPC cluster (UMD).

## Prerequisites

1. **Zaratan Account**: UMD account with Zaratan access
2. **SSH Access**: Ability to SSH to zaratan.umd.edu
3. **SLURM Access**: Access to GPU partition (if using GPU)

## Quick Start

### 1. SSH to Zaratan

```bash
ssh zaratan.umd.edu
```

### 2. Run Setup Script

```bash
cd ~
# Copy mock_application directory to Zaratan first
# Then run:
cd mock_application/deployments/zaratan
bash zaratan_setup.sh
```

### 3. Submit SLURM Job

```bash
# Edit slurm_job.sh to set your account name
# Then submit:
sbatch slurm_job.sh
```

### 4. Check Job Status

```bash
squeue -u $USER
```

### 5. Access Application

From your local machine, set up SSH tunnel:

```bash
ssh -L 8501:compute-node:8501 zaratan.umd.edu
```

Then access at: http://localhost:8501

## Manual Setup

### 1. Load Modules

```bash
module load python/3.12
```

### 2. Install Dependencies

```bash
cd ~/mock_application
pip install --user streamlit pyyaml requests psutil
```

### 3. Configure

Edit `config/app_config.yaml`:

```yaml
use_mock_llm: true
platform: zaratan
platform_tag: zaratan-gpu
zaratan:
  partition: gpu
  gpus: 1
  cpus: 8
  memory: 32G
```

### 4. Run Interactively

```bash
srun --partition=gpu --gres=gpu:1 --cpus-per-task=8 --mem=32G --time=24:00:00 --pty bash
cd ~/mock_application
streamlit run travel_genie_mock.py --server.port=8501 --server.address=0.0.0.0
```

## SLURM Job Configuration

Edit `slurm_job.sh`:

```bash
#!/bin/bash
#SBATCH --job-name=travel-genie-mock
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=24:00:00
#SBATCH --account=your-account-name  # Change this!
```

## Monitoring

### View Job Status

```bash
squeue -u $USER
squeue -j <JOB_ID>
```

### View Job Output

```bash
cat travel-genie-mock-<JOB_ID>.out
cat travel-genie-mock-<JOB_ID>.err
```

### View Job Details

```bash
scontrol show job <JOB_ID>
```

### Get Job Metrics

```bash
sacct -j <JOB_ID> --format=JobID,Elapsed,TotalCPU,MaxRSS,MaxVMSize
```

## Accessing the Application

### Option 1: SSH Tunnel (Recommended)

From your local machine:

```bash
# Get compute node name from squeue output
squeue -u $USER

# Create tunnel
ssh -L 8501:<COMPUTE_NODE>:8501 zaratan.umd.edu

# Access at http://localhost:8501
```

### Option 2: ngrok (If Allowed)

On compute node:

```bash
pip install --user pyngrok
ngrok http 8501
```

## Resource Limits

- **GPU Partition**: Limited GPU availability, queue times vary
- **CPU Partition**: More available, but no GPU
- **Memory**: Up to 256G per job
- **Time Limit**: Up to 7 days (168 hours)
- **Concurrent Jobs**: Limited by account allocation

## Cost

- **Free for UMD users**: No direct cost
- **Subject to allocation limits**: May have usage quotas
- **Queue time**: May wait in queue for resources

## Troubleshooting

### Job Stuck in Queue

- Check queue status: `squeue`
- Check partition availability: `sinfo`
- Try different partition or reduce resource requirements

### Cannot Connect to Application

- Verify job is running: `squeue -j <JOB_ID>`
- Check compute node name: `scontrol show job <JOB_ID>`
- Verify SSH tunnel is set up correctly
- Check firewall rules

### Out of Memory

- Increase memory request: `--mem=64G`
- Reduce concurrent requests in application
- Check memory usage: `sacct -j <JOB_ID> --format=MaxRSS`

### Application Crashes

- Check error log: `cat travel-genie-mock-<JOB_ID>.err`
- Check system logs: `dmesg | tail`
- Verify all dependencies are installed

## Advantages and Disadvantages

### Advantages
- **Free for UMD users**: No cost
- **High-performance GPUs**: Access to powerful GPUs
- **Large memory**: Up to 256G per job
- **Long-running jobs**: Up to 7 days
- **Academic resources**: Designed for research

### Disadvantages
- **Queue times**: May wait for resources
- **Limited availability**: Shared cluster resources
- **Complex setup**: Requires SLURM knowledge
- **SSH tunnel required**: No direct public access
- **No auto-scaling**: Manual job submission
- **Limited monitoring**: Basic SLURM metrics only
- **Account restrictions**: Subject to allocation limits

## Best Use Cases

- **Research and development**: Academic projects
- **Long-running experiments**: Multi-day runs
- **GPU-intensive workloads**: ML model training/testing
- **Batch processing**: Non-interactive workloads

## Not Suitable For

- **Production services**: Unreliable and manual
- **Public-facing applications**: No direct access
- **High-availability**: No redundancy or failover
- **Enterprise use**: No SLAs or support
- **Real-time services**: Queue delays

## Comparison with AWS

| Feature | Zaratan | AWS |
|---------|---------|-----|
| Cost | Free (for UMD) | Pay-per-use |
| Setup | Complex (SLURM) | Simple (EC2) |
| Availability | Queue-dependent | Immediate |
| Monitoring | Basic (SLURM) | Advanced (CloudWatch) |
| Auto-scaling | No | Yes |
| Public Access | SSH tunnel required | Direct |
| Support | Community | Enterprise |
| Reliability | Shared resources | Dedicated |
| Persistence | Limited | Full (EBS) |
