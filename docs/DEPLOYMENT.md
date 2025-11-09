# Cloud Deployment Guide

## Google Cloud Platform (GCP) Deployment

### Prerequisites
- Google Cloud account with billing enabled
- gcloud CLI installed
- Project with necessary APIs enabled

### Step 1: Setup VM Instance

```bash
# Create a VM instance
gcloud compute instances create osm-extractor \
  --zone=us-central1-a \
  --machine-type=e2-standard-4 \
  --boot-disk-size=50GB \
  --create-disk=size=250GB,type=pd-ssd \
  --image-family=ubuntu-2004-lts \
  --image-project=ubuntu-os-cloud

# SSH to the VM
gcloud compute ssh osm-extractor --zone=us-central1-a
```

### Step 2: Mount Data Disk

```bash
# Format and mount the data disk
sudo mkfs.ext4 /dev/sdb
sudo mkdir -p /mnt/osm-data
sudo mount /dev/sdb /mnt/osm-data
sudo chmod a+w /mnt/osm-data

# Make mount permanent
echo '/dev/sdb /mnt/osm-data ext4 defaults 0 0' | sudo tee -a /etc/fstab
```

### Step 3: Setup Environment

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3 and pip
sudo apt install python3-pip python3-venv -y

# Clone or upload your project
cd /mnt/osm-data
# Option 1: Clone from GitHub
git clone https://github.com/yourusername/OSM-Data-Extractor.git
cd OSM-Data-Extractor

# Option 2: Upload from local machine
# From your local machine:
gcloud compute scp --recurse OSM-Data-Extractor osm-extractor:/mnt/osm-data/ --zone=us-central1-a
```

### Step 4: Install Dependencies

```bash
cd /mnt/osm-data/OSM-Data-Extractor

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 5: Run Extraction

```bash
# Run in background with nohup
nohup python run_pipeline.py > extraction.log 2>&1 &

# Monitor progress
tail -f extraction.log

# Check running processes
ps aux | grep python
```

### Cost Estimation

| Resource | Specification | Cost/Day | Cost/Month |
|----------|---------------|----------|------------|
| VM Instance | e2-standard-4 | ~$3.22 | ~$96.60 |
| SSD Storage | 250GB | ~$1.42 | ~$42.50 |
| **Total** | | **~$4.64** | **~$139.10** |

*Fits within GCP free trial $300 credit*

### Monitoring

```bash
# Check disk space
df -h

# Check memory usage
free -h

# View logs
tail -f /mnt/osm-data/OSM-Data-Extractor/logs/*.log

# Stop the process
pkill -f run_pipeline.py
```

### Cleanup

```bash
# Delete the VM instance
gcloud compute instances delete osm-extractor --zone=us-central1-a

# Delete the disk (if not auto-deleted)
gcloud compute disks delete osm-extractor-data --zone=us-central1-a
```

## AWS Deployment

*Coming soon!*

## Azure Deployment

*Coming soon!*

## Local Development Tips

For local testing on smaller datasets:

```python
# In config.py, reduce the regions list:
REGIONS = [
    'İstanbul',  # Test with just one region
]
```

This significantly reduces extraction time and resource usage.
