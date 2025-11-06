#!/bin/bash

# Backend Monitoring Script for OmniScope AI
# This script helps monitor the backend health and provides debugging information

BACKEND_URL="https://bepy.panoptical.org"
FRONTEND_URL="https://omini.panoptical.org"

echo "🔍 OmniScope AI Backend Monitor"
echo "================================"
echo "Backend URL: $BACKEND_URL"
echo "Frontend URL: $FRONTEND_URL"
echo ""

# Function to check endpoint
check_endpoint() {
    local url=$1
    local name=$2
    
    echo -n "Checking $name... "
    
    if curl -s -f "$url" > /dev/null 2>&1; then
        echo "✅ OK"
        return 0
    else
        echo "❌ FAILED"
        return 1
    fi
}

# Function to get detailed response
get_response() {
    local url=$1
    local name=$2
    
    echo "📊 $name Response:"
    echo "-------------------"
    curl -s "$url" 2>/dev/null | jq . 2>/dev/null || curl -s "$url" 2>/dev/null || echo "No response"
    echo ""
}

# Check basic connectivity
echo "🌐 Connectivity Check:"
check_endpoint "$BACKEND_URL/health" "Backend Health"
check_endpoint "$BACKEND_URL/docs" "Backend API Docs"
check_endpoint "$FRONTEND_URL" "Frontend"
check_endpoint "$FRONTEND_URL/api/health" "Frontend API"
echo ""

# Get detailed health information
get_response "$BACKEND_URL/health" "Backend Health"
get_response "$BACKEND_URL/api/modules/status" "Module Status"

# Check if jq is available for JSON formatting
if ! command -v jq &> /dev/null; then
    echo "💡 Tip: Install 'jq' for better JSON formatting: sudo apt-get install jq"
fi

echo "🔄 Monitor completed at $(date)"