# 🚀 OmniScope AI - Deployment Guide

## 📋 **Deployment Overview**

- **Frontend Domain**: https://omics.panoptical.org
- **Backend Domain**: https://bepy.panoptical.org
- **Deployment Platform**: Coolify (coolify.panoptical.org)
- **Repository**: GitHub

## 🔧 **Prerequisites**

1. **GitHub Account** with repository access
2. **Coolify Access** at coolify.panoptical.org
3. **Domain Configuration** for omics.panoptical.org and bepy.panoptical.org

## 📦 **Step-by-Step Deployment**

### **Step 1: Prepare GitHub Repository**

1. **Create GitHub Repository**:
   ```bash
   # Initialize git repository
   git init
   git add .
   git commit -m "Initial commit: OmniScope AI platform"
   
   # Add GitHub remote
   git remote add origin 
   git branch -M main
   git push -u origin main
   ```

2. **Set Repository Secrets** (for GitHub Actions):
   - Go to your repository → Settings → Secrets and variables → Actions
   - Add any required secrets (GitHub token is automatic)

### **Step 2: Deploy Backend (bepy.panoptical.org)**

1. **Login to Coolify**: https://coolify.panoptical.org

2. **Create New Application**:
   - Click "New Application"
   - Choose "GitHub Repository"
   - Select your repository: `celnetamit/omniscope-ai`
   - Branch: `main`https://github.com/celnetamit/omniscope-ai.git

3. **Configure Backend Application**:
   ```json
   Name: omniscope-backend
   Port: 8001
   Dockerfile: Dockerfile.backend
   Domain: bepy.panoptical.org
   ```

4. **Environment Variables**:
   ```
   PYTHONPATH=/app
   ```

5. **Volume Mounts**:
   ```
   Host Path: /data/omniscope/db
   Container Path: /app/db
   ```

6. **Deploy Backend**: Click "Deploy"

### **Step 3: Deploy Frontend (omics.panoptical.org)**

1. **Create Second Application** in Coolify:
   - Same repository: `celnetamit/omniscope-ai`
   - Branch: `main`

2. **Configure Frontend Application**:
   ```json
   Name: omniscope-frontend
   Port: 3000
   Dockerfile: Dockerfile
   Domain: omics.panoptical.org
   ```

3. **Environment Variables**:
   ```
   NODE_ENV=production
   NEXTAUTH_URL=https://omics.panoptical.org
   NEXT_PUBLIC_API_URL=https://bepy.panoptical.org
   DATABASE_URL=file:./db/production.db
   NEXTAUTH_SECRET=your-secure-secret-key-here
   ```

4. **Volume Mounts**:
   ```
   Host Path: /data/omniscope/db
   Container Path: /app/db
   ```

5. **Deploy Frontend**: Click "Deploy"

### **Step 4: Configure SSL & Domains**

1. **SSL Certificates**: Coolify should auto-generate Let's Encrypt certificates
2. **DNS Configuration**: Ensure domains point to your Coolify server
3. **Health Checks**: Both applications have built-in health endpoints

## 🔍 **Verification Steps**

### **Check Backend Deployment**:
```bash
# Health check
curl https://bepy.panoptical.org/health

# API documentation
curl https://bepy.panoptical.org/docs
```

### **Check Frontend Deployment**:
```bash
# Health check
curl https://omics.panoptical.org/api/health

# Main application
curl https://omics.panoptical.org
```

### **Test Integration**:
1. Visit https://omics.panoptical.org
2. Check that all modules load correctly
3. Test file upload functionality
4. Verify backend API calls work

## 🛠️ **Troubleshooting**

### **Common Issues**:

1. **Build Failures**:
   - Check Dockerfile syntax
   - Verify all dependencies are listed
   - Check build logs in Coolify

2. **Environment Variables**:
   - Ensure all required env vars are set
   - Check NEXT_PUBLIC_API_URL points to correct backend
   - Verify NEXTAUTH_URL matches frontend domain

3. **Database Issues**:
   - Ensure volume mounts are configured
   - Check database file permissions
   - Verify Prisma client generation

4. **CORS Issues**:
   - Backend allows frontend domain
   - Check API proxy configuration
   - Verify SSL certificates

### **Logs Access**:
- **Coolify Logs**: Available in the Coolify dashboard
- **Application Logs**: Check container logs for errors
- **Health Endpoints**: Monitor /health endpoints

## 🔄 **Continuous Deployment**

### **Automatic Deployments**:
1. **GitHub Actions** configured for CI/CD
2. **Push to main branch** triggers deployment
3. **Docker images** built and pushed automatically
4. **Coolify** can be configured to auto-deploy on image updates

### **Manual Deployment**:
```bash
# Push changes to trigger deployment
git add .
git commit -m "Update: description of changes"
git push origin main
```

## 📊 **Monitoring**

### **Health Endpoints**:
- **Frontend**: https://omics.panoptical.org/api/health
- **Backend**: https://bepy.panoptical.org/health

### **Application Monitoring**:
- **Coolify Dashboard**: Real-time metrics and logs
- **Uptime Monitoring**: Set up external monitoring
- **Error Tracking**: Monitor application logs

## 🔐 **Security Considerations**

### **Environment Variables**:
- Use strong, unique NEXTAUTH_SECRET
- Keep API keys secure
- Use environment-specific configurations

### **SSL/TLS**:
- Ensure HTTPS is enforced
- Verify certificate validity
- Use secure headers

### **Database**:
- Regular backups of volume data
- Secure file permissions
- Monitor for unauthorized access

## 🎯 **Production Checklist**

- [ ] GitHub repository created and pushed
- [ ] Backend deployed at bepy.panoptical.org
- [ ] Frontend deployed at omics.panoptical.org
- [ ] SSL certificates configured
- [ ] Environment variables set correctly
- [ ] Health checks passing
- [ ] Database volumes mounted
- [ ] CORS configured properly
- [ ] Monitoring set up
- [ ] Backup strategy implemented

## 🚀 **Go Live!**

Once all steps are completed:

1. **Test All Functionality**:
   - File uploads work
   - Pipeline creation functions
   - Model training operates
   - Biomarker analysis displays

2. **Performance Check**:
   - Page load times acceptable
   - API response times good
   - No console errors

3. **User Acceptance**:
   - All modules accessible
   - Mobile responsive
   - Help system functional

**Your OmniScope AI platform is now live at:**
- **🌐 Frontend**: https://omics.panoptical.org
- **🔧 Backend**: https://bepy.panoptical.org

Ready for production use! 🎉