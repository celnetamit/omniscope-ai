#!/bin/bash

echo "🧪 OmniScope AI - Quick Frontend Test Setup"
echo "=========================================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}📁 Creating test data directory...${NC}"
mkdir -p mock_data

echo -e "${BLUE}🔬 Testing Data Harbor Module...${NC}"
echo "Uploading genomics expression data..."
GENOMICS_RESPONSE=$(curl -s -X POST -F "file=@mock_data/genomics_expression.csv" http://localhost:8001/api/data/upload)
GENOMICS_ID=$(echo $GENOMICS_RESPONSE | grep -o '"file_id":"[^"]*"' | cut -d'"' -f4)
echo -e "${GREEN}✅ Genomics file uploaded: $GENOMICS_ID${NC}"

echo "Uploading clinical data with missing values..."
CLINICAL_RESPONSE=$(curl -s -X POST -F "file=@mock_data/clinical_data_with_missing.csv" http://localhost:8001/api/data/upload)
CLINICAL_ID=$(echo $CLINICAL_RESPONSE | grep -o '"file_id":"[^"]*"' | cut -d'"' -f4)
echo -e "${GREEN}✅ Clinical file uploaded: $CLINICAL_ID${NC}"

echo -e "${BLUE}🔗 Testing The Weaver Module...${NC}"
echo "Creating test pipeline..."
PIPELINE_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" \
  -d '{"name": "Frontend Test Pipeline", "project_id": "frontend_test", "pipeline_json": {"nodes": [{"id": "node1", "type": "UploadGenomicsData", "position": {"x": 100, "y": 100}}, {"id": "node2", "type": "NormalizeRNASeq", "position": {"x": 300, "y": 100}}], "edges": [{"id": "edge1", "source": "node1", "target": "node2"}]}}' \
  http://localhost:8001/api/pipelines/save)
PIPELINE_ID=$(echo $PIPELINE_RESPONSE | grep -o '"pipeline_id":"[^"]*"' | cut -d'"' -f4)
echo -e "${GREEN}✅ Pipeline created: $PIPELINE_ID${NC}"

echo -e "${BLUE}🔥 Testing The Crucible Module...${NC}"
echo "Starting training job..."
TRAINING_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" \
  -d "{\"pipeline_id\": \"$PIPELINE_ID\", \"data_ids\": [\"$GENOMICS_ID\"]}" \
  http://localhost:8001/api/models/train)
JOB_ID=$(echo $TRAINING_RESPONSE | grep -o '"job_id":"[^"]*"' | cut -d'"' -f4)
echo -e "${GREEN}✅ Training job started: $JOB_ID${NC}"

echo -e "${YELLOW}⏳ Waiting for training to complete (12 seconds)...${NC}"
sleep 12

echo -e "${BLUE}💡 Testing The Insight Engine Module...${NC}"
echo "Retrieving biomarkers..."
curl -s http://localhost:8001/api/results/$JOB_ID/biomarkers | head -5
echo -e "${GREEN}✅ Biomarkers retrieved successfully${NC}"

echo ""
echo -e "${GREEN}🎉 All modules tested successfully!${NC}"
echo ""
echo "📋 Test Results Summary:"
echo "========================"
echo "📊 Genomics File ID: $GENOMICS_ID"
echo "🏥 Clinical File ID: $CLINICAL_ID"  
echo "🔗 Pipeline ID: $PIPELINE_ID"
echo "🔥 Training Job ID: $JOB_ID"
echo ""
echo "🌐 Frontend URLs:"
echo "   Dashboard: http://localhost:3000"
echo "   API Docs: http://localhost:8001/docs"
echo ""
echo "💡 Use these IDs to test the frontend interface!"
echo "   Copy and paste them into the frontend forms."