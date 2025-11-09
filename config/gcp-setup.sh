#!/bin/bash
# GCP Setup Script - Run this in Cloud Shell

echo "Setting up GCP project for OSM extraction..."

# Set your project ID
PROJECT_ID="test5-475801"
ZONE="us-central1-a"
VM_NAME="turkey-osm-extractor"

# Set the project
gcloud config set project $PROJECT_ID

# Enable necessary APIs
echo "Enabling APIs..."
gcloud services enable compute.googleapis.com
gcloud services enable logging.googleapis.com
gcloud services enable monitoring.googleapis.com

# Create the VM with data disk
echo "Creating VM..."
gcloud compute instances create $VM_NAME \
    --zone=$ZONE \
    --machine-type=e2-standard-4 \
    --boot-disk-size=50GB \
    --boot-disk-type=pd-ssd \
    --image-family=ubuntu-2004-lts \
    --image-project=ubuntu-os-cloud \
    --tags=http-server,https-server \
    --scopes=cloud-platform

# Create and attach data disk
echo "Creating data disk..."
gcloud compute disks create osm-data-disk \
    --size=200GB \
    --type=pd-ssd \
    --zone=$ZONE

gcloud compute instances attach-disk $VM_NAME \
    --disk=osm-data-disk \
    --zone=$ZONE

echo "VM setup complete! You can now SSH into the VM and run the extraction."
echo "Run: gcloud compute ssh --zone=$ZONE $VM_NAME"