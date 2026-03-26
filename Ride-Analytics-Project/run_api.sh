#!/bin/bash
# Quick start script for running FastAPI locally

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting Ride-Sharing Analytics API...${NC}"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Creating one...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${GREEN}📦 Activating virtual environment...${NC}"
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Installing API dependencies...${NC}"
    pip install -r api/requirements.txt
fi

# Check environment variables
if [ -z "$GCP_PROJECT_ID" ]; then
    echo -e "${YELLOW}⚠️  GCP_PROJECT_ID not set. Please set it:${NC}"
    echo -e "${YELLOW}   export GCP_PROJECT_ID='your-project-id'${NC}"
    echo ""
    read -p "Enter your GCP Project ID: " project_id
    export GCP_PROJECT_ID="$project_id"
fi

if [ -z "$BIGQUERY_DATASET" ]; then
    export BIGQUERY_DATASET="ridesharing_analytics"
    echo -e "${GREEN}✓ Using default dataset: ridesharing_analytics${NC}"
fi

# Check GCP authentication
if [ -z "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
    if ! gcloud auth application-default print-access-token &>/dev/null; then
        echo -e "${YELLOW}⚠️  GCP authentication not found.${NC}"
        echo -e "${YELLOW}   Run: gcloud auth application-default login${NC}"
        echo ""
        read -p "Do you want to authenticate now? (y/n): " auth_choice
        if [ "$auth_choice" = "y" ] || [ "$auth_choice" = "Y" ]; then
            gcloud auth application-default login
        else
            echo -e "${RED}❌ Authentication required. Exiting.${NC}"
            exit 1
        fi
    fi
fi

echo -e "${GREEN}✓ Environment configured${NC}"
echo -e "${GREEN}✓ GCP Project: $GCP_PROJECT_ID${NC}"
echo -e "${GREEN}✓ BigQuery Dataset: $BIGQUERY_DATASET${NC}"
echo ""
echo -e "${GREEN}🌐 Starting API server...${NC}"
echo -e "${GREEN}   API will be available at: http://localhost:8080${NC}"
echo -e "${GREEN}   API docs will be available at: http://localhost:8080/docs${NC}"
echo ""
echo -e "${YELLOW}Press CTRL+C to stop the server${NC}"
echo ""

# Run the API
uvicorn api.main:app --host 0.0.0.0 --port 8080 --reload

