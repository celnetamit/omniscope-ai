# OmniScope AI - Multi-Omics Data Analysis Platform

A comprehensive platform integrating four powerful modules for multi-omics data analysis, pipeline management, model training, and insight generation.

## 🏗️ Architecture Overview

OmniScope AI consists of a Next.js frontend (TypeScript) and a Python FastAPI backend that integrates four specialized modules:

### Core Modules

1. **Data Harbor** - File upload and CSV analysis
2. **The Weaver** - Visual pipeline management with AI suggestions
3. **The Crucible** - Model training with real-time progress tracking
4. **The Insight Engine** - Biomarker analysis with Socratic tutoring

## 📁 Project Structure

```
/home/z/my-project/
├── src/app/                    # Next.js frontend
│   ├── page.tsx               # Main dashboard
│   └── api/proxy/             # API proxy to Python backend
├── modules/                   # Python FastAPI modules
│   ├── data_harbor.py         # Module 2: Data Harbor
│   ├── the_weaver.py          # Module 3: The Weaver
│   ├── the_crucible.py        # Module 4: The Crucible
│   └── the_insight_engine.py  # Module 5: The Insight Engine
├── main.py                    # Core FastAPI application
├── requirements.txt           # Python dependencies
├── server.ts                  # Next.js server with Socket.IO
└── start-omniscope.sh         # Startup script
```

## 🚀 Setup Instructions

### Prerequisites

- Node.js 18+ (for Next.js)
- Python 3.8+ (for FastAPI backend)
- npm or yarn

### Step 1: Install Frontend Dependencies

```bash
cd /home/z/my-project
npm install
```

### Step 2: Install Python Dependencies

```bash
pip3 install -r requirements.txt
```

### Step 3: Start the Platform

#### Option A: Using the Startup Script (Recommended)

```bash
./start-omniscope.sh
```

#### Option B: Manual Startup

**Terminal 1 - Start Python Backend:**
```bash
python3 main.py
```

**Terminal 2 - Start Next.js Frontend:**
```bash
npm run dev
```

### Step 4: Access the Platform

- **Frontend Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🔌 Module Integration Details

### Core Application (main.py)

The core FastAPI application serves as the central hub that:

1. **Imports all module routers** with proper prefixes
2. **Configures CORS** for cross-origin requests
3. **Provides unified endpoints** for module status and health checks
4. **Handles global exceptions** consistently
5. **Offers comprehensive API documentation**

### Module Routing Structure

```
/api/data/          → Data Harbor Module
/api/pipelines/     → The Weaver Module  
/api/models/        → The Crucible Module
/api/results/       → The Insight Engine Module
```

### Frontend Integration

The Next.js frontend connects to the Python backend through:

1. **API Proxy Route** (`/api/proxy`) - Handles cross-origin requests
2. **Real-time Dashboard** - Shows module status and interactions
3. **Tabbed Interface** - Separate sections for each module
4. **Polling Mechanisms** - Real-time updates for training jobs and file analysis

## 📊 Module Features & Endpoints

### 1. Data Harbor Module
- **Purpose**: CSV file upload and automated analysis
- **Endpoints**:
  - `POST /api/data/upload` - Upload CSV files
  - `GET /api/data/{file_id}/report` - Get analysis results
- **Features**: Missing value analysis, duplicate detection, data quality recommendations

### 2. The Weaver Module
- **Purpose**: Visual pipeline management with AI suggestions
- **Endpoints**:
  - `POST /api/pipelines/save` - Save/update pipelines
  - `GET /api/pipelines/{pipeline_id}` - Load specific pipeline
  - `GET /api/pipelines/project/{project_id}/list` - List project pipelines
  - `POST /api/pipelines/suggest` - Get AI-powered suggestions
- **Features**: Pipeline validation, AI co-pilot suggestions, visual workflow editor

### 3. The Crucible Module
- **Purpose**: Model training with real-time progress tracking
- **Endpoints**:
  - `POST /api/models/train` - Start training job
  - `GET /api/models/{job_id}/status` - Get training status
  - `GET /api/models/{job_id}/results` - Get final results
- **Features**: Background processing, real-time metrics, training explanations

### 4. The Insight Engine Module
- **Purpose**: Biomarker analysis with educational explanations
- **Endpoints**:
  - `GET /api/results/{model_id}/biomarkers` - Get biomarkers list
  - `GET /api/results/{model_id}/biomarkers/{gene_id}/explain` - Get detailed explanation
  - `POST /api/results/{model_id}/query` - Natural language queries
- **Features**: Socratic tutoring, external database links, conversational queries

## 🔄 Data Flow Between Modules

1. **Data Harbor** → Analyzes uploaded CSV files
2. **The Weaver** → Creates pipelines using analyzed data
3. **The Crucible** → Trains models based on pipelines
4. **The Insight Engine** → Analyzes model results and provides insights

## 🛠️ Development & Testing

### Running Linting
```bash
npm run lint
```

### Testing Module Integration

1. **Test Backend Health**:
   ```bash
   curl http://localhost:8000/health
   ```

2. **Test Module Status**:
   ```bash
   curl http://localhost:8000/api/modules/status
   ```

3. **Test Frontend Connection**:
   - Open http://localhost:3000
   - Check module status cards
   - Try uploading a CSV file

### API Testing

Use the built-in Swagger UI at http://localhost:8000/docs to test all endpoints interactively.

## 🔧 Configuration

### Environment Variables

- `PYTHON_BACKEND_URL`: URL of the Python backend (default: http://localhost:8000)
- `NODE_ENV`: Environment mode (development/production)

### Customization

- **Module Prefixes**: Modify in `main.py` router includes
- **CORS Settings**: Adjust origins in production
- **Storage**: Replace in-memory storage with databases for production

## 🚨 Troubleshooting

### Common Issues

1. **Port Conflicts**: Ensure ports 3000 and 8000 are available
2. **CORS Errors**: Check CORS configuration in `main.py`
3. **Module Import Errors**: Verify Python dependencies are installed
4. **Proxy Failures**: Check backend is running before frontend

### Debug Mode

Enable debug mode by setting:
```python
app = FastAPI(debug=True)
```

## 📈 Production Deployment

### Docker Setup (Recommended)

Create a `docker-compose.yml` file to containerize both services:

```yaml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - PYTHONPATH=/app
    volumes:
      - ./modules:/app/modules
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
    environment:
      - PYTHON_BACKEND_URL=http://backend:8000
```

### Database Integration

Replace in-memory storage with:
- **PostgreSQL** for pipeline storage
- **Redis** for caching and job queues
- **MinIO/S3** for file storage

## 🤝 Contributing

1. Follow the existing module structure
2. Add proper error handling and validation
3. Update API documentation
4. Test integration with existing modules

## 📄 License

This project is part of the OmniScope AI platform for multi-omics data analysis.