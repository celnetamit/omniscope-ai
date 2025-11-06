# 🧪 Frontend Testing Checklist

## ✅ Ready-to-Use Test Data

### 📊 File IDs (from quick_test.sh):
- **Genomics Data**: `c27b62bf-26bd-4939-8d57-3bd2ef34ba53`
- **Clinical Data**: `d1d891a5-937e-42c1-9f01-7733b18a7f61`
- **Pipeline ID**: `634a9cf3-04a5-4c88-a448-a0cbe9f85670`
- **Training Job**: `a469f275-3b36-4dd2-8b4e-5ff4cdc9a49e`

## 🎯 Frontend Testing Steps

### 1. Dashboard Overview
- [ ] Navigate to http://localhost:3000
- [ ] Verify all 4 module status cards show "active" with green checkmarks
- [ ] Check module descriptions are displayed correctly

### 2. Data Harbor Tab Testing
- [ ] Click on "Data Harbor" tab
- [ ] Upload `mock_data/genomics_expression.csv`
- [ ] Upload `mock_data/clinical_data_with_missing.csv`
- [ ] Upload `mock_data/proteomics_data.csv`
- [ ] Upload `mock_data/metabolomics_data.csv`
- [ ] Verify file upload progress and completion messages
- [ ] Check analysis reports show correct statistics

### 3. The Weaver Tab Testing
- [ ] Click on "The Weaver" tab
- [ ] Verify existing pipeline is listed: "Frontend Test Pipeline"
- [ ] Test "Create New Pipeline" button functionality
- [ ] Copy pipeline configs from `mock_data/sample_pipeline_configs.json`
- [ ] Test AI suggestions for different pipeline configurations

### 4. The Crucible Tab Testing
- [ ] Click on "The Crucible" tab
- [ ] Verify training job `a469f275-3b36-4dd2-8b4e-5ff4cdc9a49e` is listed
- [ ] Check training progress shows 10/10 epochs completed
- [ ] Verify metrics show: Accuracy ~0.95, Loss ~0.2
- [ ] Test "Start New Training Job" with existing pipeline and data IDs

### 5. Insight Engine Tab Testing
- [ ] Click on "Insight Engine" tab
- [ ] Use training job ID: `a469f275-3b36-4dd2-8b4e-5ff4cdc9a49e`
- [ ] Click "Analyze Biomarkers" - should show 15 biomarkers
- [ ] Verify biomarkers include: MYC, TP53, KRAS, EGFR, BRCA1, BRCA2
- [ ] Test "Ask Questions" with sample queries:
  - "What are the top 5 biomarkers?"
  - "Explain the role of p53"
  - "Which genes are related to cancer?"

## 🔍 Detailed Test Scenarios

### File Upload Tests:
1. **Genomics Expression Data** (15 genes × 9 columns)
   - Expected: Clean data, no missing values
   - Should show gene expression levels across samples

2. **Clinical Data with Missing Values** (15 patients × 9 columns)
   - Expected: Missing value warnings
   - Should suggest imputation methods (KNN, median, mode)

3. **Proteomics Data** (15 proteins × 11 columns)
   - Expected: Protein abundance analysis
   - Should show patient demographics integration

4. **Metabolomics Data** (15 metabolites × 8 columns)
   - Expected: Metabolite pathway analysis
   - Should categorize by biochemical pathways

### Pipeline Creation Tests:
Use these JSON configs from `sample_pipeline_configs.json`:

1. **Basic Genomics Pipeline**
   - 3 nodes: Upload → Normalize → QC
   - Should suggest IntegrateMOFAPlus as next step

2. **Multi-omics Integration**
   - 7 nodes with complex workflow
   - Should validate connections and detect cycles

3. **Cancer Biomarker Discovery**
   - 8 nodes end-to-end pipeline
   - Should show complete analysis workflow

### Training Job Monitoring:
- Real-time progress updates every 2 seconds
- Accuracy progression: 0.50 → 0.95
- Loss reduction: 1.0 → 0.2
- Status explanations change with progress

### Biomarker Analysis:
- 15 biomarkers with importance scores
- External database links (UniProt, NCBI, Ensembl, HMDB)
- Socratic questions for educational engagement
- Natural language query responses

## 🚨 Error Testing

### Test Error Scenarios:
- [ ] Upload invalid file format (should show error)
- [ ] Use non-existent file ID (should show 404 error)
- [ ] Create pipeline with invalid JSON (should show validation error)
- [ ] Query non-existent training job (should show not found)

### Expected Error Handling:
- Graceful error messages
- Fallback UI states
- Retry mechanisms where appropriate
- User-friendly error descriptions

## 📱 Responsive Design Testing

### Test Different Screen Sizes:
- [ ] Desktop (1920×1080)
- [ ] Tablet (768×1024)
- [ ] Mobile (375×667)
- [ ] Verify all components are accessible
- [ ] Check tab navigation works on mobile

## 🎨 UI/UX Testing

### Visual Elements:
- [ ] Loading spinners during API calls
- [ ] Progress bars for training jobs
- [ ] Status badges with appropriate colors
- [ ] Icons match functionality
- [ ] Consistent spacing and typography

### Interactions:
- [ ] Hover effects on buttons
- [ ] Click feedback on interactive elements
- [ ] Smooth transitions between states
- [ ] Keyboard navigation support

## 🔄 Real-time Features

### Live Updates:
- [ ] Module status refreshes automatically
- [ ] Training progress updates every 2 seconds
- [ ] File analysis status polling
- [ ] Error states update appropriately

Happy testing! Use the provided IDs and data files to thoroughly test all functionality. 🚀