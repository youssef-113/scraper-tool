#!/bin/bash
# Automated Screenshot Capture Guide
# Helps capture all required screenshots

echo "📸 Screenshot Capture Guide for Deployment Proof"
echo "=================================================="
echo ""

PROJECT_ID="${PROJECT_ID:-gemini-scraper-agent}"
REGION="us-central1"
SERVICE_NAME="gemini-scraper-agent"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}SCREENSHOT 1: Cloud Run Dashboard${NC}"
echo "1. Open: https://console.cloud.google.com/run?project=${PROJECT_ID}"
echo "2. Click on service: ${SERVICE_NAME}"
echo "3. Screenshot the overview page showing:"
echo "   - Service name"
echo "   - Green 'SERVING' status"
echo "   - Service URL"
echo "   - Metrics graph"
echo "4. Save as: 01_cloud_run_dashboard.png"
echo ""
read -p "Press Enter when screenshot is captured..."

echo -e "${BLUE}SCREENSHOT 2: Service Logs${NC}"
echo "1. Click on 'LOGS' tab"
echo "2. Wait for logs to populate (10-15 seconds)"
echo "3. Screenshot showing:"
echo "   - Multiple log entries"
echo "   - Timestamps"
echo "   - Gemini API calls"
echo "4. Save as: 02_service_logs.png"
echo ""
read -p "Press Enter when screenshot is captured..."

echo -e "${BLUE}SCREENSHOT 3: Vertex AI${NC}"
echo "1. Open: https://console.cloud.google.com/vertex-ai?project=${PROJECT_ID}"
echo "2. Click 'Model Garden'"
echo "3. Search for 'Gemini'"
echo "4. Screenshot showing Gemini 2.0 Flash enabled"
echo "5. Save as: 03_vertex_ai.png"
echo ""
read -p "Press Enter when screenshot is captured..."

echo -e "${BLUE}SCREENSHOT 4: Secret Manager${NC}"
echo "1. Open: https://console.cloud.google.com/security/secret-manager?project=${PROJECT_ID}"
echo "2. Screenshot showing 'google-api-key' secret"
echo "3. Save as: 04_secret_manager.png"
echo ""
read -p "Press Enter when screenshot is captured..."

echo -e "${BLUE}SCREENSHOT 5: Container Registry${NC}"
echo "1. Open: https://console.cloud.google.com/gcr/images/${PROJECT_ID}"
echo "2. Click on gemini-scraper-agent image"
echo "3. Screenshot showing image tags and versions"
echo "4. Save as: 05_container_registry.png"
echo ""
read -p "Press Enter when screenshot is captured..."

echo -e "${BLUE}SCREENSHOT 6: Cloud Build${NC}"
echo "1. Open: https://console.cloud.google.com/cloud-build/builds?project=${PROJECT_ID}"
echo "2. Screenshot showing recent successful builds"
echo "3. Save as: 06_cloud_build.png"
echo ""
read -p "Press Enter when screenshot is captured..."

echo -e "${BLUE}SCREENSHOT 7: Live Application${NC}"
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region ${REGION} --format='value(status.url)' 2>/dev/null || echo "https://your-service-url")
echo "1. Open: ${SERVICE_URL}"
echo "2. Wait for app to load"
echo "3. Screenshot showing the app running"
echo "4. Save as: 07_live_application.png"
echo ""
read -p "Press Enter when screenshot is captured..."

echo ""
echo -e "${GREEN}✅ All screenshots captured!${NC}"
echo ""
echo "Next steps:"
echo "1. Review all screenshots in deployment_screenshots/"
echo "2. Ensure they're clear and legible"
echo "3. Upload to GitHub repository"
echo "4. Add links to DEPLOYMENT_PROOF.md"
echo ""
echo -e "${YELLOW}Optional: Record a 30-second video walkthrough${NC}"
echo "See deployment_screenshots/video_script.md for guidance"
