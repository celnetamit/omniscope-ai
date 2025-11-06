# 📁 Coolify Volume Mount Setup Guide

## 🎯 **Step-by-Step Instructions for Volume Configuration**

### **Step 1: Access Your Backend Application**
1. Go to **https://coolify.panoptical.org**
2. Login to your Coolify dashboard
3. Find your **omniscope-backend** application
4. Click on it to open the application details

### **Step 2: Navigate to Storage Settings**
1. In your backend application page, look for tabs at the top
2. Click on **"Storages"** or **"Volumes"** tab
   - If you don't see it, look for **"Configuration"** → **"Storages"**
   - Or check **"Settings"** → **"Storages"**

### **Step 3: Add New Volume Mount**
1. Look for a button like **"+ Add Storage"** or **"+ Add Volume"**
2. Click it to create a new volume mount

### **Step 4: Configure the Volume**
Fill in these exact values:

```
Name: backend-database
Source: /data/omniscope/backend
Destination: /app/db
Type: Bind Mount (or Volume)
```

**Detailed Fields:**
- **Name/Label**: `backend-database` (or any name you prefer)
- **Host Path/Source**: `/data/omniscope/backend`
- **Container Path/Destination**: `/app/db`
- **Mount Type**: `Bind Mount` (if available)
- **Read/Write**: `Read/Write` or `RW`

### **Step 5: Save and Deploy**
1. Click **"Save"** or **"Add"** to create the volume
2. Go back to your application main page
3. Click **"Deploy"** to redeploy with the new volume

## 🔍 **Alternative Method - If You Can't Find Storages Tab**

### **Method 2: Through Docker Compose Override**
If Coolify doesn't show a Storages tab, you can add it via Docker Compose:

1. In your backend application, look for **"Docker Compose"** or **"Advanced"**
2. Add this to your compose configuration:
```yaml
volumes:
  - /data/omniscope/backend:/app/db
```

### **Method 3: Through Environment Variables**
Some Coolify versions use environment variables:
1. Go to **"Environment Variables"** in your backend app
2. Add:
```
COOLIFY_VOLUME_0=/data/omniscope/backend:/app/db
```

## 📸 **What to Look For in Coolify Dashboard**

### **Common Tab Names:**
- "Storages"
- "Volumes" 
- "Mounts"
- "Configuration" → "Storage"
- "Settings" → "Volumes"
- "Advanced" → "Volumes"

### **Common Button Names:**
- "+ Add Storage"
- "+ Add Volume"
- "+ New Mount"
- "Configure Volumes"

## ✅ **Verification Steps**

### **After Adding Volume:**
1. **Deploy** your backend application
2. **Check logs** during deployment for:
```
📁 Created database directory: db
✅ Database tables created successfully
```

3. **Test persistence:**
   - Upload a file in your app
   - Redeploy the backend
   - Check if the file analysis is still there

### **Check if Volume is Working:**
```bash
# Test endpoint after deployment
curl https://bepy.panoptical.org/health
```

Should show:
```json
{
  "modules": {
    "data_harbor": {
      "storage": "SQLite database"
    }
  }
}
```

## 🚨 **If You Can't Find Volume Settings**

### **Option 1: Skip Volume for Now**
The database will still work, but data will be lost on restart. You can:
1. Deploy without volume first
2. Test the database functionality
3. Add volume later when you find the setting

### **Option 2: Contact Coolify Support**
1. Check Coolify documentation for your version
2. Look for "Persistent Storage" or "Volume Mounts"
3. Each Coolify version might have different UI

### **Option 3: Manual File Backup**
Without volume mount, you can manually backup:
```bash
# Download database file before updates
# Upload it back after deployment
```

## 📋 **Quick Checklist**

- [ ] Found backend application in Coolify
- [ ] Located Storages/Volumes section
- [ ] Added volume mount: `/data/omniscope/backend` → `/app/db`
- [ ] Saved volume configuration
- [ ] Deployed application
- [ ] Verified database initialization in logs
- [ ] Tested data persistence

## 🎯 **Most Important**

**Even without volume mount, your database will work!** 

The volume is only needed for **data persistence across restarts**. You can:
1. **Deploy first** to test the database functionality
2. **Add volume later** when you find the right setting
3. **Use the app normally** - it will work perfectly

The database upgrade is complete and functional! 🎉