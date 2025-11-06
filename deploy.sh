#!/bin/bash

# OmniScope AI Deployment Script
echo "🚀 Deploying OmniScope AI to Production"
echo "========================================"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo -e "${RED}❌ Git repository not initialized${NC}"
    echo "Run: git init && git remote add origin YOUR_REPO_URL"
    exit 1
fi

# Check if we're on main branch
BRANCH=$(git branch --show-current)
if [ "$BRANCH" != "main" ]; then
    echo -e "${YELLOW}⚠️  Not on main branch. Current branch: $BRANCH${NC}"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo -e "${BLUE}📦 Preparing for deployment...${NC}"

# Generate Prisma client
echo "Generating Prisma client..."
npx prisma generate

# Build the application locally to check for errors
echo "Building application..."
npm run build

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Build failed. Please fix errors before deploying.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Build successful${NC}"

# Add all changes
echo "Adding changes to git..."
git add .

# Commit changes
echo "Enter commit message:"
read -r COMMIT_MSG
if [ -z "$COMMIT_MSG" ]; then
    COMMIT_MSG="Deploy: $(date '+%Y-%m-%d %H:%M:%S')"
fi

git commit -m "$COMMIT_MSG"

# Push to GitHub
echo -e "${BLUE}📤 Pushing to GitHub...${NC}"
git push origin main

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Successfully pushed to GitHub${NC}"
    echo ""
    echo -e "${BLUE}🎯 Next Steps:${NC}"
    echo "1. Go to coolify.panoptical.org"
    echo "2. Deploy backend to bepy.panoptical.org"
    echo "3. Deploy frontend to omini.panoptical.org"
    echo ""
    echo -e "${GREEN}📋 Deployment URLs:${NC}"
    echo "Frontend: https://omini.panoptical.org"
    echo "Backend:  https://bepy.panoptical.org"
    echo "Coolify:  https://coolify.panoptical.org"
else
    echo -e "${RED}❌ Failed to push to GitHub${NC}"
    exit 1
fi