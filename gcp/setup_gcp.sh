#!/bin/bash
# Initial GCP Project Setup
# Run this ONCE before deployment

echo "🔧 Setting up GCP project for Gemini Scraper Agent..."

# Variables
PROJECT_ID="${PROJECT_ID:-gemini-scraper-agent}"
BILLING_ACCOUNT_ID="${BILLING_ACCOUNT_ID:-}"  # Pass as env var or edit below

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI not found. Install from: https://cloud.google.com/sdk${NC}"
    exit 1
fi

# Check if user is logged in
if ! gcloud auth list --filter="status:ACTIVE" | grep -q "@"; then
    echo "� Authenticating with Google Cloud..."
    gcloud auth login
fi

# Create project if it doesn't exist
echo -e "${BLUE}[1/5]${NC} Creating GCP project..."
if gcloud projects describe ${PROJECT_ID} &> /dev/null; then
    echo -e "${YELLOW}Project ${PROJECT_ID} already exists${NC}"
else
    gcloud projects create ${PROJECT_ID} \
        --name="Gemini Scraper Agent" \
        --set-as-default
    echo -e "${GREEN}✅ Project created: ${PROJECT_ID}${NC}"
fi

# Set project as default
gcloud config set project ${PROJECT_ID}

# Link billing account
echo -e "${BLUE}[2/5]${NC} Linking billing account..."
if [ -z "$BILLING_ACCOUNT_ID" ]; then
    echo "Available billing accounts:"
    gcloud beta billing accounts list
    echo ""
    read -p "Enter your Billing Account ID: " BILLING_ACCOUNT_ID
fi

gcloud beta billing projects link ${PROJECT_ID} \
    --billing-account=${BILLING_ACCOUNT_ID} || echo "Billing may already be linked"

echo -e "${GREEN}✅ Billing configured${NC}"

# Set default region and zone
echo -e "${BLUE}[3/5]${NC} Setting default region..."
gcloud config set compute/region us-central1
gcloud config set compute/zone us-central1-a
gcloud config set run/region us-central1

echo -e "${GREEN}✅ Region configured: us-central1${NC}"

# Enable required APIs
echo -e "${BLUE}[4/5]${NC} Enabling required APIs..."
gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    containerregistry.googleapis.com \
    secretmanager.googleapis.com \
    aiplatform.googleapis.com \
    storage.googleapis.com \
    artifactregistry.googleapis.com

echo -e "${GREEN}✅ APIs enabled${NC}"

# Create Artifact Registry repository
echo -e "${BLUE}[5/5]${NC} Creating Artifact Registry..."
gcloud artifacts repositories create gemini-scraper-repo \
    --repository-format=docker \
    --location=us-central1 \
    --description="Docker repository for Gemini Scraper Agent" 2>/dev/null || true

echo -e "${GREEN}✅ Artifact Registry created${NC}"

# Summary
echo ""
echo "======================================================================"
echo -e "${GREEN}✅ GCP PROJECT SETUP COMPLETE!${NC}"
echo "======================================================================"
echo ""
echo "Project ID: ${PROJECT_ID}"
echo "Region: us-central1"
echo ""
echo "Next steps:"
echo "  1. Add your API keys:"
echo "     export GOOGLE_API_KEY=your_key"
echo "     export GROQ_API_KEY=your_key (optional)"
echo ""
echo "  2. Run deployment:"
echo "     cd gcp && ./deploy.sh"
echo ""
echo "  Or test locally first:"
echo "     ./gcp/local_test.sh"
echo "======================================================================"
