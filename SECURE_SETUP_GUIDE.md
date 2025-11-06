# 🔐 Secure GitHub Setup Guide

## ⚠️ **Important Security Notice**

**NEVER share your passwords publicly!** This guide will help you set up the repository securely.

## 🚀 **Quick Setup Steps**

### **Step 1: Run the Setup Script**
```bash
./setup-github.sh
```

### **Step 2: Create GitHub Repository**

#### **Option A: Using GitHub Web Interface**
1. Go to https://github.com/new
2. **Repository name**: `omniscope-ai`
3. **Description**: `OmniScope AI - Multi-Omics Data Analysis Platform`
4. **Visibility**: Public (recommended) or Private
5. **DO NOT** check "Add a README file" (we already have one)
6. Click **"Create repository"**

#### **Option B: Using GitHub CLI (if installed)**
```bash
# Install GitHub CLI first if not installed
# Then run:
gh auth login
gh repo create omniscope-ai --public --source=. --remote=origin --push
```

### **Step 3: Connect Local Repository to GitHub**
After creating the repository on GitHub, run:
```bash
git remote add origin https://github.com/celnetamit/omniscope-ai.git
git branch -M main
git push -u origin main
```

### **Step 4: Verify Repository**
Your repository will be available at:
**https://github.com/celnetamit/omniscope-ai**

## 🔑 **Authentication Options**

### **Option 1: Personal Access Token (Recommended)**
1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate new token with `repo` permissions
3. Use token instead of password when prompted

### **Option 2: SSH Key (Most Secure)**
```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "amit.rai@celnet.in"

# Add to SSH agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Copy public key and add to GitHub
cat ~/.ssh/id_ed25519.pub
```

Then add the public key to GitHub Settings → SSH and GPG keys

### **Option 3: GitHub CLI**
```bash
# Install GitHub CLI and authenticate
gh auth login
```

## 🛡️ **Security Best Practices**

### **1. Enable Two-Factor Authentication**
- Go to GitHub Settings → Security
- Enable 2FA for additional security

### **2. Use Environment Variables**
- Never commit passwords or API keys
- Use `.env` files (already in `.gitignore`)
- Use GitHub Secrets for CI/CD

### **3. Review Repository Settings**
- Set appropriate visibility (Public/Private)
- Configure branch protection rules
- Enable security alerts

## 📋 **Post-Setup Checklist**

- [ ] Repository created on GitHub
- [ ] Local repository connected to GitHub
- [ ] Initial commit pushed successfully
- [ ] Repository accessible at https://github.com/celnetamit/omniscope-ai
- [ ] 2FA enabled on GitHub account
- [ ] Secure authentication method configured

## 🚀 **Next Steps After Repository Setup**

1. **Deploy to Coolify**: Follow the deployment guide
2. **Configure Domains**: Set up omini.panoptical.org and bepy.panoptical.org
3. **Test Deployment**: Verify all functionality works
4. **Monitor**: Set up monitoring and alerts

## 🆘 **Troubleshooting**

### **Authentication Issues**
```bash
# If you get authentication errors, try:
git config --global credential.helper store
```

### **Permission Denied**
- Use Personal Access Token instead of password
- Or set up SSH key authentication

### **Repository Already Exists**
```bash
# If repository name is taken, try:
# omniscope-ai-platform
# omniscope-multiomics
# celnet-omniscope
```

## 📞 **Support**

If you encounter issues:
1. Check GitHub documentation
2. Verify your credentials
3. Ensure repository name is unique
4. Contact GitHub support if needed

**Remember: Keep your credentials secure and never share them publicly!** 🔐