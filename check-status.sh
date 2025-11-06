#!/bin/bash

echo "🔍 OmniScope AI Status Check"
echo "================================"

# Check frontend
echo "🌐 Frontend (Next.js):"
if curl -s http://localhost:3000 > /dev/null; then
    echo "   ✅ Running on http://localhost:3000"
else
    echo "   ❌ Not responding"
fi

# Check backend
echo "🔧 Backend (FastAPI):"
if curl -s http://localhost:8001/health > /dev/null; then
    echo "   ✅ Running on http://localhost:8001"
    echo "   📚 API Docs: http://localhost:8001/docs"
else
    echo "   ❌ Not responding"
fi

# Check module status
echo "📊 Module Status:"
curl -s http://localhost:8001/api/modules/status | python3 -m json.tool 2>/dev/null | grep -E '"status"|"description"' | head -8

echo ""
echo "🚀 Ready for live testing!"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8001"
echo "   API Docs: http://localhost:8001/docs"