# OmniScope AI - Frontend Testing Guide

## 🧪 Complete Testing Scenarios

### 1. Data Harbor Module Testing

#### Test Files Available:
- `mock_data/genomics_expression.csv` - Gene expression data (15 genes, 6 samples)
- `mock_data/proteomics_data.csv` - Protein abundance data (15 proteins, 8 patients)  
- `mock_data/metabolomics_data.csv` - Metabolite concentrations (15 metabolites, 6 samples)
- `mock_data/clinical_data_with_missing.csv` - Clinical data with missing values (15 patients)

#### Testing Steps:
1. **Navigate to Data Harbor tab**
2. **Upload genomics_expression.csv**
   - Expected: Clean data, no missing values, 15 rows × 9 columns
   - Should show data types and basic statistics
3. **Upload clinical_data_with_missing.csv**
   - Expected: Missing value warnings and recommendations
   - Should suggest imputation methods
4. **Upload proteomics_data.csv**
   - Expected: Larger dataset analysis with patient demographics

### 2. The Weaver Module Testing

#### Pipeline Creation Scenarios:

**Scenario A: Basic Genomics Pipeline**
```json
{
  "name": "Basic RNA-seq Analysis",
  "project_id": "genomics_project",
  "pipeline_json": {
    "nodes": [
      {"id": "upload1", "type": "UploadGenomicsData", "position": {"x": 100, "y": 100}},
      {"id": "norm1", "type": "NormalizeRNASeq", "position": {"x": 300, "y": 100}},
      {"id": "qc1", "type": "QCProteomics", "position": {"x": 500, "y": 100}}
    ],
    "edges": [
      {"id": "e1", "source": "upload1", "target": "norm1"},
      {"id": "e2", "source": "norm1", "target": "qc1"}
    ]
  }
}
```

**Scenario B: Multi-omics Integration**
```json
{
  "name": "Multi-omics MOFA+ Integration",
  "project_id": "multiomics_project", 
  "pipeline_json": {
    "nodes": [
      {"id": "upload1", "type": "UploadGenomicsData", "position": {"x": 100, "y": 100}},
      {"id": "upload2", "type": "UploadProteomicsData", "position": {"x": 100, "y": 200}},
      {"id": "norm1", "type": "NormalizeRNASeq", "position": {"x": 300, "y": 100}},
      {"id": "integrate1", "type": "IntegrateMOFAPlus", "position": {"x": 500, "y": 150}}
    ],
    "edges": [
      {"id": "e1", "source": "upload1", "target": "norm1"},
      {"id": "e2", "source": "norm1", "target": "integrate1"},
      {"id": "e3", "source": "upload2", "target": "integrate1"}
    ]
  }
}
```

#### Testing Steps:
1. **Create pipelines using the scenarios above**
2. **Test AI suggestions** - Should suggest next logical steps
3. **Save and load pipelines** - Verify persistence
4. **List pipelines by project** - Check filtering

### 3. The Crucible Module Testing

#### Training Job Scenarios:

**Scenario A: Cancer Classification Model**
```json
{
  "pipeline_id": "your_saved_pipeline_id",
  "data_ids": ["your_uploaded_file_id"]
}
```

#### Testing Steps:
1. **Start training job** with uploaded data
2. **Monitor real-time progress** - Watch epochs and metrics
3. **Check status updates** - Verify explanatory text changes
4. **Retrieve final results** - Get model performance metrics

### 4. The Insight Engine Testing

#### Testing Steps:
1. **Use completed training job ID** from Crucible testing
2. **List biomarkers** - Should show 15 cancer-related biomarkers
3. **Get explanations** for top biomarkers:
   - P04637 (p53) - Guardian of the genome
   - P00533 (EGFR) - Growth factor receptor
   - P01106 (MYC) - Oncogene transcription factor
4. **Test natural language queries**:
   - "What are the top 5 biomarkers?"
   - "Explain the role of p53 in cancer"
   - "Which biomarkers are related to DNA repair?"

## 🎯 Expected Results

### Data Harbor Results:
- **genomics_expression.csv**: 15 rows, 9 columns, no missing data
- **clinical_data_with_missing.csv**: Missing value warnings, imputation suggestions
- **proteomics_data.csv**: Protein abundance analysis with patient demographics

### The Weaver Results:
- **AI Suggestions**: NormalizeRNASeq → IntegrateMOFAPlus → TrainXGBoostModel
- **Pipeline Validation**: Cycle detection, orphaned nodes warnings
- **Project Organization**: Pipelines grouped by project_id

### The Crucible Results:
- **Training Progress**: 10 epochs, accuracy 0.50 → 0.95, loss 1.0 → 0.2
- **Status Updates**: "Learning basic patterns" → "Refining boundaries" → "Converging"
- **Final Metrics**: Accuracy 0.92, AUC 0.95, Precision 0.91, Recall 0.93

### The Insight Engine Results:
- **15 Biomarkers**: p53, MYC, EGFR, TP53, BRCA1, BRCA2, etc.
- **Importance Scores**: 0.99 (p53) down to 0.70 (Lactate)
- **External Links**: UniProt, NCBI, Ensembl, HMDB databases
- **Socratic Questions**: Educational prompts for deeper learning

## 🚀 Quick Test Commands

### Upload Test Data:
```bash
# Upload genomics data
curl -X POST -F "file=@mock_data/genomics_expression.csv" http://localhost:8001/api/data/upload

# Upload clinical data with missing values  
curl -X POST -F "file=@mock_data/clinical_data_with_missing.csv" http://localhost:8001/api/data/upload
```

### Create Test Pipeline:
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"name": "Test Pipeline", "project_id": "test_project", "pipeline_json": {"nodes": [{"id": "node1", "type": "UploadGenomicsData", "position": {"x": 100, "y": 100}}], "edges": []}}' \
  http://localhost:8001/api/pipelines/save
```

### Start Training Job:
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"pipeline_id": "your_pipeline_id", "data_ids": ["your_file_id"]}' \
  http://localhost:8001/api/models/train
```

## 📊 Frontend UI Testing Checklist

- [ ] Module status cards show "active" with green checkmarks
- [ ] File upload shows progress and completion status
- [ ] Pipeline editor allows drag-and-drop node creation
- [ ] Training progress bars update in real-time
- [ ] Biomarker table displays with sorting and filtering
- [ ] Error states show helpful messages
- [ ] Loading states provide user feedback
- [ ] Responsive design works on different screen sizes

Happy testing! 🧪✨