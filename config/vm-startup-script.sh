#!/bin/bash
# VM Startup Script - Runs automatically when VM starts

echo "Starting VM setup for OSM extraction..."

# Update system
apt update && apt upgrade -y

# Install system dependencies
apt install -y python3-pip python3-venv wget git curl htop

# Format and mount data disk
mkfs.ext4 -m 0 -E lazy_itable_init=0,lazy_journal_init=0,discard /dev/sdb
mkdir -p /mnt/osm-data
mount -o discard,defaults /dev/sdb /mnt/osm-data
chmod a+w /mnt/osm-data

# Add to fstab for auto-mount
echo '/dev/sdb /mnt/osm-data ext4 defaults 0 0' >> /etc/fstab

# Create project directory
mkdir -p /mnt/osm-data/turkey-osm-extractor
cd /mnt/osm-data/turkey-osm-extractor

echo "VM setup complete!"