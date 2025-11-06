# 🔧 Backend Troubleshooting Guide

## 🚨 **Backend Going Down - Common Issues & Solutions**

### **Issue 1: Memory Exhaustion (Most Common)**

**Symptoms:**
- Backend works initially, then crashes after some time
- Container restarts frequently
- Out of Memory (OOM) errors in logs

**Causes:**
- Large file uploads consuming memory
- Too many stored analysis reports
- Background tasks accumulating

**Solutions Applied:**
✅ **Memory Management**: Limited stored reports to 100 items
✅ **Cleanup Functions**: Automatic cleanup of old data
✅ **Timestamps**: Added timestamps for proper cleanup

**Monitor Memory Usage:**
```bash
# Check container memory usage in Coolify
# Go to your backend app → Metrics → Memory Usage
```

### **Issue 2: Reload Mode in Production**

**Symptoms:**
- Random crashes
- File watching errors
- Instability in containerized environment

**Solution Applied:**
✅ **Disabled Reload**: Changed `reload=True` to `reload=False` in production

### **Issue 3: Unhandled Exceptions**

**Symptoms:**
- Backend crashes on specific requests
- 500 errors causing process exit

**Solutions Applied:**
✅ **Better Error Handling**: Added try-catch blocks in background tasks
✅ **Graceful Shutdown**: Added signal handlers for clean shutdown
✅ **Error Logging**: Added print statements for debugging

## 🔍 **Monitoring & Debugging**

### **1. Use the Monitor Script**
```bash
./monitor-backend.sh
```

### **2. Check Coolify Logs**
1. Go to https://coolify.panoptical.org
2. Find your backend application
3. Click "Logs" to see real-time output
4. Look for error messages or crash indicators

### **3. Health Check Endpoints**
```bash
# Backend health
curl https://bepy.panoptical.org/health

# Module status
curl https://bepy.panoptical.org/api/modules/status

# API documentation
curl https://bepy.panoptical.org/docs
```

### **4. Common Error Patterns**

**Memory Issues:**
```
OOMKilled
Container killed due to memory limit
```

**Python Errors:**
```
ModuleNotFoundError
ImportError
SyntaxError
```

**Network Issues:**
```
Connection refused
Timeout errors
```

## 🛠️ **Quick Fixes**

### **If Backend is Down:**

1. **Restart in Coolify:**
   - Go to your backend app
   - Click "Deploy" or "Restart"

2. **Check Resource Limits:**
   - Increase memory limit if needed
   - Check CPU usage

3. **Verify Environment Variables:**
   ```
   PYTHONPATH=/app
   ```

### **If Backend Keeps Crashing:**

1. **Check Recent Changes:**
   - Any new deployments?
   - Configuration changes?

2. **Review Logs:**
   - Look for Python tracebacks
   - Check for repeated error patterns

3. **Test Locally:**
   ```bash
   # Run locally to test
   python main.py
   ```

## 🔄 **Redeploy Steps**

### **Method 1: Coolify Redeploy**
1. Go to https://coolify.panoptical.org
2. Find "omniscope-backend"
3. Click "Deploy"
4. Wait for build to complete
5. Check logs for startup messages

### **Method 2: Force Rebuild**
1. In Coolify, go to Settings
2. Enable "Force Rebuild"
3. Deploy again
4. This rebuilds the Docker image from scratch

## 📊 **Performance Optimization**

### **Memory Usage:**
- **Current Limits**: 100 reports, 50 training jobs
- **Adjust if needed**: Modify `MAX_STORED_REPORTS` and `MAX_STORED_JOBS`

### **File Upload Limits:**
- **Current**: 10MB per file
- **Location**: `modules/data_harbor.py`
- **Adjust**: Change `MAX_FILE_SIZE` constant

### **Background Task Monitoring:**
```python
# Check active background tasks
# Look for stuck or long-running tasks
```

## 🚀 **Prevention Strategies**

### **1. Regular Monitoring**
- Set up uptime monitoring
- Check memory usage trends
- Monitor error rates

### **2. Resource Management**
- Set appropriate memory limits
- Monitor disk usage
- Clean up old data regularly

### **3. Error Handling**
- All endpoints have try-catch blocks
- Background tasks handle exceptions
- Graceful degradation on errors

## 📞 **Emergency Checklist**

When backend is down:

- [ ] Check Coolify dashboard for errors
- [ ] Run monitor script: `./monitor-backend.sh`
- [ ] Check recent deployments/changes
- [ ] Review application logs
- [ ] Restart the application
- [ ] Verify health endpoints
- [ ] Test basic functionality
- [ ] Check frontend connectivity

## 🔗 **Useful Commands**

```bash
# Test backend connectivity
curl -I https://bepy.panoptical.org/health

# Check API documentation
curl https://bepy.panoptical.org/docs

# Test file upload endpoint
curl -X POST https://bepy.panoptical.org/api/data/upload

# Monitor in real-time
watch -n 5 './monitor-backend.sh'
```

## 📝 **Log Analysis**

### **Good Startup Logs:**
```
🚀 Starting OmniScope AI Core Application...
📚 API Documentation: http://localhost:8001/docs
🔍 Health Check: http://localhost:8001/health
📊 Module Status: http://localhost:8001/api/modules/status
INFO:     Started server process [1]
INFO:     Waiting for application startup.
🚀 OmniScope AI is starting up...
📊 Data Harbor Module: Ready for file uploads and analysis
🔗 The Weaver Module: Ready for pipeline management
🔥 The Crucible Module: Ready for model training
💡 The Insight Engine Module: Ready for biomarker analysis
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8001
```

### **Error Indicators:**
```
Traceback (most recent call last):
ModuleNotFoundError:
ImportError:
MemoryError:
OSError:
```

The backend should now be much more stable with these improvements!