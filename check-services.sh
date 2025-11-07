#!/bin/bash

echo "🔍 OmniScope AI Services Status Check"
echo "======================================"

# Check Frontend (Next.js)
echo "🌐 Frontend (Next.js on port 3000):"
if curl -s http://localhost:3000 > /dev/null; then
    echo "   ✅ Frontend is running"
else
    echo "   ❌ Frontend is not responding"
fi

# Check Backend (FastAPI)
echo "🔧 Backend (FastAPI on port 8001):"
if curl -s http://localhost:8001/health > /dev/null; then
    echo "   ✅ Backend is running"
    
    # Get module status
    echo "📊 Module Status:"
    curl -s http://localhost:8001/api/modules/status | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    for module, info in data.items():
        status = info.get('status', 'unknown')
        desc = info.get('description', 'No description')
        print(f'   • {module.replace(\"_\", \" \").title()}: {status} - {desc}')
except:
    print('   ⚠️  Could not parse module status')
"
else
    echo "   ❌ Backend is not responding"
fi

echo ""
echo "🌍 Access URLs:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8001"
echo "   API Docs: http://localhost:8001/docs"
echo ""