#!/bin/bash

# GitHub Repository Setup Script for OmniScope AI
# User: celnetamit
# Email: amit.rai@celnet.in

echo "🚀 Setting up GitHub Repository for OmniScope AI"
echo "================================================"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Repository details
GITHUB_USERNAME="celnetamit"
REPO_NAME="omniscope-ai"
EMAIL="amit.rai@celnet.in"

echo -e "${BLUE}📋 Repository Details:${NC}"
echo "Username: $GITHUB_USERNAME"
echo "Repository: $REPO_NAME"
echo "Email: $EMAIL"
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git is not installed. Please install Git first.${NC}"
    exit 1
fi

# Configure git user (if not already configured)
echo -e "${BLUE}⚙️ Configuring Git...${NC}"
git config --global user.name "celnetamit"
git config --global user.email "amit.rai@celnet.in"

# Initialize git repository if not already initialized
if [ ! -d ".git" ]; then
    echo -e "${BLUE}📦 Initializing Git repository...${NC}"
    git init
    echo -e "${GREEN}✅ Git repository initialized${NC}"
else
    echo -e "${YELLOW}⚠️ Git repository already exists${NC}"
fi

# Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    echo -e "${BLUE}📝 Creating .gitignore...${NC}"
    cat > .gitignore << 'EOF'
# Dependencies
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Production builds
.next/
out/
build/
dist/

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Database
*.db
*.sqlite
db/

# Logs
*.log
logs/

# Runtime data
pids/
*.pid
*.seed
*.pid.lock

# Coverage directory used by tools like istanbul
coverage/
*.lcov

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
ENV/
env/
.venv/
.pytest_cache/

# Temporary files
tmp/
temp/
*.tmp

# Development logs
dev.log
server.log
EOF
    echo -e "${GREEN}✅ .gitignore created${NC}"
fi

# Add all files to git
echo -e "${BLUE}📁 Adding files to Git...${NC}"
git add .

# Create initial commit
echo -e "${BLUE}💾 Creating initial commit...${NC}"
git commit -m "Initial commit: OmniScope AI - Multi-Omics Data Analysis Platform

Features:
- Data Harbor: File upload and analysis
- The Weaver: Pipeline management with AI suggestions
- The Crucible: Real-time model training
- Insight Engine: Biomarker discovery and analysis
- Modern Next.js frontend with TypeScript
- FastAPI backend with comprehensive APIs
- Docker deployment configuration
- Coolify deployment ready"

echo -e "${GREEN}✅ Initial commit created${NC}"

# Instructions for GitHub setup
echo ""
echo -e "${YELLOW}🔑 NEXT STEPS - Manual GitHub Setup Required:${NC}"
echo ""
echo "1. Go to https://github.com/new"
echo "2. Repository name: omniscope-ai"
echo "3. Description: OmniScope AI - Multi-Omics Data Analysis Platform"
echo "4. Set to Public (or Private if preferred)"
echo "5. DO NOT initialize with README (we already have one)"
echo "6. Click 'Create repository'"
echo ""
echo "7. After creating the repository, run these commands:"
echo ""
echo -e "${BLUE}git remote add origin https://github.com/celnetamit/omniscope-ai.git${NC}"
echo -e "${BLUE}git branch -M main${NC}"
echo -e "${BLUE}git push -u origin main${NC}"
echo ""
echo -e "${YELLOW}📝 Alternative: Use GitHub CLI (if installed):${NC}"
echo -e "${BLUE}gh repo create omniscope-ai --public --source=. --remote=origin --push${NC}"
echo ""
echo -e "${GREEN}🎯 Repository will be available at:${NC}"
echo "https://github.com/celnetamit/omniscope-ai"
echo ""
echo -e "${YELLOW}⚠️ Security Reminder:${NC}"
echo "- Never commit passwords or API keys"
echo "- Use environment variables for sensitive data"
echo "- Enable 2FA on your GitHub account"