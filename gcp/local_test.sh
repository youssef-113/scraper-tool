#!/bin/bash
# Test locally before deploying to GCP

echo "🧪 Testing Gemini Scraper Agent locally..."

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Check environment
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ .env file not found!${NC}"
    echo "Create .env with:"
    echo "  GOOGLE_API_KEY=your_key"
    echo "  GROQ_API_KEY=your_key (optional)"
    echo ""
    echo "Example:"
    echo "  cp .env.example .env"
    echo "  # Edit .env with your keys"
    exit 1
fi

# Load environment
export $(cat .env | grep -v '^#' | xargs)

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found. Install from: https://docker.com${NC}"
    exit 1
fi

# Build Docker image
echo -e "${BLUE}Building Docker image...${NC}"
docker build -t gemini-scraper-agent:local .

# Run container
echo -e "${BLUE}Starting container on port 8080...${NC}"
docker run -p 8080:8080 \
    -e GOOGLE_API_KEY=${GOOGLE_API_KEY} \
    -e GROQ_API_KEY=${GROQ_API_KEY:-} \
    -e OPENAI_API_KEY=${OPENAI_API_KEY:-} \
    --rm \
    gemini-scraper-agent:local &

# Wait for container to start
sleep 5

# Health check
echo ""
echo -e "${BLUE}Testing health endpoint...${NC}"
if curl -f http://localhost:8080/_stcore/health &> /dev/null; then
    echo -e "${GREEN}✅ Health check passed${NC}"
else
    echo -e "${RED}⚠️ Health check failed (container may still be starting)${NC}"
fi

echo ""
echo "======================================================================"
echo -e "${GREEN}✅ LOCAL TEST RUNNING${NC}"
echo "======================================================================"
echo ""
echo "🌐 Open in browser: http://localhost:8080"
echo ""
echo "Press Ctrl+C to stop the container"
echo "======================================================================"

# Wait for container
wait
