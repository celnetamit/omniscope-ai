# 🧬 OmniScope AI - Multi-Omics Data Analysis Platform

A comprehensive, AI-powered platform for multi-omics data analysis, featuring advanced biomarker discovery, pipeline management, and machine learning capabilities.

## 🌐 **Live Demo**

- **Frontend**: https://omini.panoptical.org
- **Backend API**: https://bepy.panoptical.org
- **API Documentation**: https://bepy.panoptical.org/docs

## ✨ **Features**

### 🗂️ **Data Harbor - File Upload & Analysis**
- Drag & drop file upload interface
- Automated data quality assessment
- Real-time analysis progress tracking
- Comprehensive data reports with recommendations

### 🔗 **The Weaver - Pipeline Management**
- Visual pipeline editor with drag-and-drop nodes
- AI-powered workflow suggestions
- Multi-omics integration capabilities
- Project-based organization

### 🔥 **The Crucible - Model Training**
- Real-time machine learning model training
- Multiple ML algorithms (XGBoost, Random Forest, Neural Networks)
- Live progress monitoring with AI explanations
- Comprehensive performance metrics

### 💡 **Insight Engine - Biomarker Analysis**
- Interactive biomarker discovery and exploration
- AI-powered biological significance explanations
- Natural language query processing
- Socratic learning approach for education

## 🚀 **Technology Stack**

### **Frontend**
- **Next.js 15** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **shadcn/ui** - Modern component library
- **React Hook Form + Zod** - Form handling and validation

### **Backend**
- **FastAPI** - Modern Python web framework
- **Pydantic** - Data validation and serialization
- **Pandas** - Data analysis and manipulation
- **Uvicorn** - ASGI server

### **Database & Storage**
- **Prisma ORM** - Type-safe database access
- **SQLite** - Lightweight database (production-ready)

### **Deployment**
- **Docker** - Containerization
- **Coolify** - Self-hosted deployment platform
- **GitHub Actions** - CI/CD pipeline

## 🛠️ **Local Development**

### **Prerequisites**
- Node.js 20+
- Python 3.12+
- Git

### **Quick Start**
```bash
# Clone the repository
git clone https://github.com/celnetamit/omniscope-ai.git
cd omniscope-ai

# Install frontend dependencies
npm install

# Set up Python virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set up database
npx prisma generate
npx prisma db push

# Start development servers
npm run dev          # Frontend on http://localhost:3000
python main.py       # Backend on http://localhost:8001
```

### **Environment Variables**
Copy `.env.example` to `.env` and configure:
```bash
cp .env.example .env
```

## 🐳 **Docker Deployment**

### **Local Docker Testing**
```bash
# Build and run with Docker Compose
docker-compose up --build

# Access the application
# Frontend: http://localhost:3000
# Backend: http://localhost:8001
```

### **Production Deployment**
See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for detailed deployment instructions.

## 📊 **API Documentation**

The backend provides comprehensive API documentation:
- **Local**: http://localhost:8001/docs
- **Production**: https://bepy.panoptical.org/docs

### **Key Endpoints**
- `POST /api/data/upload` - File upload and analysis
- `GET /api/data/{file_id}/report` - Analysis reports
- `POST /api/pipelines/save` - Pipeline management
- `POST /api/models/train` - Model training
- `GET /api/results/{model_id}/biomarkers` - Biomarker discovery

## 🧪 **Testing**

### **Frontend Testing**
```bash
npm run lint        # ESLint
npm run build       # Build verification
```

### **Backend Testing**
```bash
# Run quick test script
./quick_test.sh

# Manual API testing
curl http://localhost:8001/health
```

### **Integration Testing**
Use the provided mock data in `mock_data/` directory:
- `genomics_expression.csv` - Gene expression data
- `clinical_data_with_missing.csv` - Clinical data with missing values
- `proteomics_data.csv` - Protein abundance data
- `metabolomics_data.csv` - Metabolite concentrations

## 📁 **Project Structure**

```
omniscope-ai/
├── src/                          # Frontend source code
│   ├── app/                      # Next.js App Router pages
│   ├── components/               # React components
│   │   ├── modules/              # Main application modules
│   │   ├── layout/               # Layout components
│   │   └── ui/                   # UI components (shadcn/ui)
│   └── lib/                      # Utility functions
├── modules/                      # Backend Python modules
├── prisma/                       # Database schema
├── mock_data/                    # Test datasets
├── Dockerfile                    # Frontend container
├── Dockerfile.backend            # Backend container
└── docker-compose.yml            # Local development setup
```

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 **Support**

- **Documentation**: Check the comprehensive guides in the `/docs` directory
- **Issues**: Report bugs and request features via GitHub Issues
- **Discussions**: Join community discussions in GitHub Discussions

## 🎯 **Roadmap**

- [ ] Advanced visualization tools
- [ ] Collaborative features and sharing
- [ ] Integration with external databases
- [ ] Advanced ML model support
- [ ] Real-time collaboration
- [ ] Mobile app development

## 🙏 **Acknowledgments**

- Built with modern web technologies and best practices
- Designed for the bioinformatics and research community
- Powered by AI for intelligent analysis and insights

---

**Ready to revolutionize your multi-omics research? Get started at https://omini.panoptical.org** 🚀# omniscope-ai
