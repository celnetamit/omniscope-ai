# 🗄️ Database Migration Guide - Backend Production Database

## 🎉 **What's New**

Your OmniScope AI backend now has **production-ready database persistence**!

### **Before (In-Memory Storage):**
❌ Data lost on restart  
❌ No data persistence  
❌ Limited scalability  

### **After (SQLite Database):**
✅ **Data survives restarts**  
✅ **Persistent storage**  
✅ **Production ready**  
✅ **Automatic cleanup**  
✅ **Query logging**  

## 📊 **Database Schema**

### **Tables Created:**
1. **`file_analysis_reports`** - Data Harbor file analysis results
2. **`pipelines`** - The Weaver pipeline configurations  
3. **`training_jobs`** - The Crucible model training jobs
4. **`biomarker_results`** - The Insight Engine biomarker data
5. **`query_logs`** - Natural language query analytics

### **Database Location:**
```
Backend: /app/db/backend.db (SQLite file)
Frontend: /app/db/production.db (SQLite file)
```

## 🚀 **Deployment Steps**

### **1. Redeploy Backend in Coolify**
1. Go to https://coolify.panoptical.org
2. Find your **omniscope-backend** application
3. Click **"Deploy"** to redeploy with database support
4. Wait for build completion (3-5 minutes)

### **2. Configure Volume Mounts (Important!)**
In Coolify backend settings, ensure you have:
```
Source: /data/omniscope/backend
Destination: /app/db
```
This ensures your database file persists across container restarts.

### **3. Verify Database Initialization**
Check the deployment logs for:
```
🗄️ Initializing backend database...
📁 Created database directory: db
✅ Database tables created successfully
✅ Database connection test successful
```

## 🔍 **Testing the Database**

### **Test Data Persistence:**
1. **Upload a file** in Data Harbor
2. **Create a pipeline** in The Weaver  
3. **Start model training** in The Crucible
4. **Restart the backend** (redeploy)
5. **Check if data is still there** ✅

### **Health Check:**
```bash
curl https://bepy.panoptical.org/health
```

Should show:
```json
{
  "modules": {
    "data_harbor": "operational",
    "storage": "SQLite database"
  }
}
```

## 📈 **Performance & Limits**

### **Current Configuration:**
- **File Reports**: Max 100 stored (auto-cleanup)
- **Training Jobs**: Max 50 stored (auto-cleanup)  
- **Pipelines**: Unlimited (per project)
- **Biomarkers**: Unlimited (per model)
- **Query Logs**: Unlimited (for analytics)

### **Database Size Management:**
- **Automatic cleanup** removes old data
- **SQLite** is lightweight and efficient
- **No manual maintenance** required

## 🔧 **Advanced Configuration**

### **Environment Variables:**
```bash
DATABASE_URL=sqlite:///./db/backend.db  # Default
# For PostgreSQL: postgresql://user:pass@host:port/dbname
# For MySQL: mysql://user:pass@host:port/dbname
```

### **Database Migration (Future):**
The system is designed to support:
- **PostgreSQL** for high-traffic production
- **MySQL** for enterprise deployments
- **SQLite** for development and small deployments

## 🛠️ **Troubleshooting**

### **Database Connection Issues:**
```bash
# Check if database file exists
ls -la /app/db/backend.db

# Check database permissions
chmod 664 /app/db/backend.db
```

### **Migration from In-Memory:**
- **No data loss** - old in-memory data was temporary
- **Fresh start** - all modules start with clean database
- **Demo data** - biomarkers auto-generate for testing

### **Common Errors:**
```
❌ "Database locked" - Check file permissions
❌ "No such table" - Database initialization failed
❌ "Connection refused" - Database file path issue
```

## 📊 **Data Structure Examples**

### **File Analysis Report:**
```json
{
  "id": "uuid-here",
  "filename": "data.csv", 
  "status": "complete",
  "report_data": {
    "summary": {"rows": 1000, "columns": 50},
    "findings": [...],
    "recommendations": [...]
  }
}
```

### **Pipeline Configuration:**
```json
{
  "id": "pipeline-uuid",
  "project_id": "project-123",
  "name": "My Analysis Pipeline",
  "pipeline_json": {
    "nodes": [...],
    "edges": [...]
  }
}
```

### **Training Job:**
```json
{
  "id": "job-uuid",
  "status": "completed",
  "progress": {"current_epoch": 10, "total_epochs": 10},
  "final_metrics": {"accuracy": 0.92, "auc": 0.95}
}
```

## 🎯 **Benefits Achieved**

### **Data Persistence:**
- ✅ File analysis results survive restarts
- ✅ Pipeline configurations are saved permanently  
- ✅ Training job history is maintained
- ✅ Biomarker results are stored long-term

### **Production Readiness:**
- ✅ Proper database schema with relationships
- ✅ Automatic data cleanup and management
- ✅ Query logging for analytics
- ✅ Scalable architecture

### **User Experience:**
- ✅ No data loss on system updates
- ✅ Faster loading of previous work
- ✅ Historical data access
- ✅ Improved reliability

## 🔄 **Backup & Recovery**

### **Backup Database:**
```bash
# Copy the SQLite file
cp /app/db/backend.db /backup/backend-$(date +%Y%m%d).db
```

### **Restore Database:**
```bash
# Replace with backup
cp /backup/backend-20241106.db /app/db/backend.db
```

### **Coolify Volume Backup:**
Coolify automatically handles volume persistence, but you can also:
1. Go to your backend app settings
2. Configure backup schedules
3. Download volume snapshots

Your backend is now production-ready with full database persistence! 🎉