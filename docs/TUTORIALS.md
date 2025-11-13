# OmniScope AI - Tutorials

## Quick Start Tutorials

### Tutorial 1: Your First Analysis (15 minutes)

**Goal**: Upload data, train a model, and generate a report

**Prerequisites**: 
- OmniScope AI account
- Sample dataset: [cancer_data.csv](examples/cancer_data.csv)

**Steps**:

1. **Upload Data**
   ```
   1. Click "Data Harbor" in sidebar
   2. Click "Upload File"
   3. Select cancer_data.csv
   4. Wait for analysis report
   5. Review data quality metrics
   ```

2. **Create Pipeline**
   ```
   1. Click "The Weaver" in sidebar
   2. Click "New Pipeline"
   3. Drag "Data Import" node
   4. Connect to "Preprocessing" node
   5. Add "Model Training" node
   6. Connect nodes
   7. Click "Save Pipeline"
   ```

3. **Train Model**
   ```
   1. Click on "Model Training" node
   2. Select algorithm: Random Forest
   3. Choose target: disease_status
   4. Click "Train Model"
   5. Monitor progress (2-3 minutes)
   ```

4. **View Results**
   ```
   1. Navigate to "The Insight Engine"
   2. View model accuracy: ~92%
   3. Examine top biomarkers
   4. Click on TP53 for explanation
   ```

5. **Generate Report**
   ```
   1. Click "Generate Report"
   2. Select template: Scientific Report
   3. Choose format: PDF
   4. Click "Generate"
   5. Download report (30 seconds)
   ```

**Expected Outcome**: 
- Trained classification model with 90%+ accuracy
- PDF report with methods, results, and visualizations
- List of top 10 biomarkers

---

### Tutorial 2: Real-time Collaboration (20 minutes)

**Goal**: Collaborate with a teammate on pipeline development

**Prerequisites**:
- Two OmniScope AI accounts
- Shared dataset

**Part A: Create and Share Workspace**

1. **User A: Create Workspace**
   ```
   1. Click "Collaboration" in sidebar
   2. Click "New Workspace"
   3. Name: "Team Cancer Analysis"
   4. Click "Create"
   ```

2. **User A: Invite Teammate**
   ```
   1. Click workspace settings (gear icon)
   2. Click "Invite Members"
   3. Enter User B's email
   4. Select role: Editor
   5. Click "Send Invitation"
   ```

3. **User B: Accept Invitation**
   ```
   1. Check email for invitation
   2. Click "Accept Invitation"
   3. Workspace opens automatically
   ```

**Part B: Collaborative Editing**

4. **User A: Start Pipeline**
   ```
   1. Add "Data Import" node
   2. Configure with shared dataset
   3. User B sees node appear in real-time
   ```

5. **User B: Add Preprocessing**
   ```
   1. Add "Normalization" node
   2. Connect to Data Import
   3. User A sees connection appear
   4. Both users see each other's cursors
   ```

6. **Both Users: Build Together**
   ```
   User A:
   - Adds feature selection node
   - Configures parameters
   
   User B:
   - Adds model training node
   - Selects algorithm
   
   Real-time sync: All changes visible instantly
   ```

7. **Test Collaboration Features**
   ```
   - Move cursor → See teammate's cursor
   - Type in chat → Instant messaging
   - Make changes → Auto-saved
   - Disconnect → Changes queued
   - Reconnect → Changes synced
   ```

**Expected Outcome**:
- Functional collaborative workspace
- Pipeline built by two users simultaneously
- Understanding of real-time sync features

---

### Tutorial 3: Advanced ML with AutoML (30 minutes)

**Goal**: Use AutoML to find the best model automatically

**Prerequisites**:
- Dataset with 500+ samples
- Clear target variable

**Steps**:

1. **Prepare Data**
   ```
   1. Upload dataset
   2. Review data quality report
   3. Handle missing values:
      - Numeric: Median imputation
      - Categorical: Mode imputation
   4. Check class balance
   5. If imbalanced, note for later
   ```

2. **Configure AutoML**
   ```
   1. Navigate to ML Framework → AutoML
   2. Select dataset
   3. Choose target column
   4. Select features (or use all)
   5. Set task type: Classification
   6. Configure advanced settings:
      - Time limit: 3600 seconds (1 hour)
      - Quality: Best Quality
      - Metric: AUC-ROC
      - Cross-validation: 5-fold
   ```

3. **Start Training**
   ```
   1. Click "Start AutoML"
   2. System tests multiple algorithms:
      - Random Forest
      - Gradient Boosting
      - Neural Networks
      - Support Vector Machines
      - Ensemble methods
   3. Monitor progress dashboard
   4. See real-time leaderboard
   ```

4. **Analyze Results**
   ```
   After 1 hour:
   1. View final leaderboard
   2. Best model: Gradient Boosting (AUC: 0.96)
   3. Compare with other models
   4. Review hyperparameters
   5. Check cross-validation scores
   ```

5. **Explain Model**
   ```
   1. Select best model
   2. Click "Explain Model"
   3. Choose SHAP method
   4. View feature importance:
      - TP53: 0.45 (most important)
      - BRCA1: 0.32
      - Age: 0.15
   5. Examine individual predictions
   6. Generate explanation report
   ```

6. **Deploy Model**
   ```
   1. Click "Deploy Model"
   2. Generate API endpoint
   3. Test with sample data
   4. Integrate into application
   ```

**Expected Outcome**:
- Best-performing model identified automatically
- Model accuracy > 90%
- Feature importance rankings
- Deployable model with API endpoint

---

### Tutorial 4: 3D Protein Visualization (25 minutes)

**Goal**: Visualize and analyze protein structures in 3D

**Prerequisites**:
- PDB ID or protein structure file
- WebGL-enabled browser

**Part A: Basic Visualization**

1. **Load Protein Structure**
   ```
   1. Navigate to Visualization → Protein Viewer
   2. Enter PDB ID: 1ABC (or your protein)
   3. Click "Load Structure"
   4. Wait for structure to load (5-10 seconds)
   ```

2. **Explore Structure**
   ```
   Basic Controls:
   - Left drag: Rotate
   - Right drag: Zoom
   - Middle drag: Pan
   - Double-click: Center
   
   Try:
   - Rotate 360° to see all sides
   - Zoom in on active site
   - Pan to different regions
   ```

3. **Change Representation**
   ```
   1. Click "Representation" dropdown
   2. Try different styles:
      - Cartoon: See secondary structure
      - Ball & Stick: See atoms
      - Surface: See molecular surface
      - Ribbon: See backbone
   3. Compare representations
   ```

**Part B: Advanced Analysis**

4. **Color by Property**
   ```
   1. Click "Color Scheme" dropdown
   2. Try different schemes:
      - By Chain: Multi-chain proteins
      - By Element: Standard CPK colors
      - By Secondary Structure: Helix/sheet/loop
      - By B-factor: Flexibility
   3. Identify flexible regions (high B-factor)
   ```

5. **Measure Distances**
   ```
   1. Click "Measure" tool
   2. Click two atoms
   3. View distance in Angstroms
   4. Measure active site dimensions
   5. Identify binding pocket size
   ```

6. **Highlight Residues**
   ```
   1. Click "Select" tool
   2. Select residues: 100-150
   3. Click "Highlight"
   4. Change color to red
   5. Label important residues
   ```

**Part C: Export and Share**

7. **Create Publication Figure**
   ```
   1. Set optimal view angle
   2. Choose representation: Cartoon
   3. Color by secondary structure
   4. Add labels for key residues
   5. Click "Export"
   6. Format: PNG
   7. Resolution: 300 DPI
   8. Download image
   ```

8. **Create Interactive Viewer**
   ```
   1. Click "Export" → "Interactive HTML"
   2. Include controls: Yes
   3. Download HTML file
   4. Open in browser
   5. Share with colleagues
   ```

**Expected Outcome**:
- Understanding of protein 3D structure
- High-quality publication figure
- Interactive viewer for presentations

---

### Tutorial 5: Literature Mining Workflow (35 minutes)

**Goal**: Find relevant papers, extract knowledge, and generate insights

**Prerequisites**:
- Research topic or gene of interest
- OmniScope AI account

**Part A: Paper Discovery**

1. **Search for Papers**
   ```
   1. Navigate to Literature Mining
   2. Enter query: "TP53 mutations cancer therapy"
   3. Set filters:
      - Years: 2020-2024
      - Journals: High-impact only
      - Article type: Research articles
   4. Click "Search"
   5. Review 50+ results
   ```

2. **Rank by Relevance**
   ```
   1. Sort by: Relevance score
   2. Review top 10 papers
   3. Check citation counts
   4. Read AI-generated summaries
   5. Select 5 most relevant papers
   ```

3. **Read Summaries**
   ```
   For each paper:
   1. Click "View Summary"
   2. Read 3-5 sentence summary
   3. Review key findings
   4. Check methodology
   5. Note important results
   ```

**Part B: Knowledge Extraction**

4. **Extract Relationships**
   ```
   1. Select 5 papers
   2. Click "Extract Relationships"
   3. Wait for processing (1-2 minutes)
   4. View extracted relationships:
      - TP53 → regulates → p21
      - TP53 → interacts_with → MDM2
      - TP53 → associated_with → cancer
   5. Review confidence scores
   ```

5. **Build Knowledge Graph**
   ```
   1. Click "View Knowledge Graph"
   2. Explore graph visualization:
      - Nodes: Genes, diseases, drugs
      - Edges: Relationships
      - Colors: Entity types
   3. Click nodes for details
   4. Trace pathways
   5. Identify key hubs
   ```

6. **Find Novel Connections**
   ```
   1. Look for unexpected connections
   2. Check evidence for each relationship
   3. Identify research gaps
   4. Generate hypotheses
   ```

**Part C: Question Answering**

7. **Ask Specific Questions**
   ```
   Questions to try:
   1. "What is the role of TP53 in cancer?"
   2. "How does TP53 interact with MDM2?"
   3. "What drugs target TP53 pathway?"
   4. "What are TP53 mutation hotspots?"
   ```

8. **Review Answers**
   ```
   For each answer:
   1. Read AI-generated response
   2. Check confidence score
   3. Review supporting papers
   4. Verify with original text
   5. Export answer with citations
   ```

**Part D: Stay Updated**

9. **Set Up Alerts**
   ```
   1. Click "Create Alert"
   2. Topic: "TP53 cancer therapy"
   3. Frequency: Weekly
   4. Email: your@email.com
   5. Click "Subscribe"
   ```

10. **Receive Updates**
    ```
    Weekly email includes:
    - New papers matching topic
    - AI-generated summaries
    - Key findings
    - Links to full papers
    ```

**Expected Outcome**:
- Comprehensive literature review
- Knowledge graph of relationships
- Answers to specific questions
- Automated alerts for new research

---

### Tutorial 6: Generating Publication Reports (40 minutes)

**Goal**: Create a publication-ready scientific report

**Prerequisites**:
- Completed analysis with results
- Trained model
- Visualizations

**Part A: Report Configuration**

1. **Select Template**
   ```
   1. Navigate to Reports → Generate
   2. Choose template: Scientific Report
   3. Review template sections:
      - Title and Abstract
      - Introduction
      - Methods
      - Results
      - Discussion
      - References
   ```

2. **Configure Metadata**
   ```
   1. Title: "Multi-Omics Analysis of Breast Cancer Biomarkers"
   2. Authors: Add your name and affiliations
   3. Keywords: cancer, biomarkers, machine learning
   4. Abstract: Auto-generated (can edit)
   ```

3. **Select Data Sources**
   ```
   1. Model: Select trained model
   2. Dataset: Select analyzed dataset
   3. Visualizations: Select figures
   4. Statistical tests: Select analyses
   ```

**Part B: Content Customization**

4. **Edit Introduction**
   ```
   1. Review auto-generated introduction
   2. Add background context
   3. State research objectives
   4. Describe significance
   5. Preview changes
   ```

5. **Review Methods Section**
   ```
   Auto-generated content includes:
   - Data collection methods
   - Preprocessing steps
   - Statistical analyses
   - Machine learning algorithms
   - Software versions
   - Parameter settings
   
   Verify accuracy and completeness
   ```

6. **Customize Results**
   ```
   1. Select key findings to highlight
   2. Choose figures to include:
      - Model performance metrics
      - Feature importance plot
      - Survival curves
      - Network visualizations
   3. Add figure captions
   4. Include statistical tables
   ```

7. **Add Discussion Points**
   ```
   1. Interpret key findings
   2. Compare with literature
   3. Discuss limitations
   4. Suggest future work
   5. State conclusions
   ```

**Part C: Citations and References**

8. **Manage Citations**
   ```
   1. Review auto-added citations
   2. Add additional references:
      - Search PubMed
      - Click "Add to Bibliography"
   3. Choose citation style: Nature
   4. Verify formatting
   ```

9. **Format References**
   ```
   Citation styles available:
   - Nature: [1], [2], [3]
   - Science: (1, 2, 3)
   - APA: (Author, Year)
   - MLA: (Author Page)
   
   Select: Nature
   References auto-formatted
   ```

**Part D: Generation and Export**

10. **Generate Report**
    ```
    1. Review all sections
    2. Click "Generate Report"
    3. Select format: PDF
    4. Wait 20-30 seconds
    5. Preview generated report
    ```

11. **Review and Refine**
    ```
    Check:
    - Formatting consistency
    - Figure quality
    - Table alignment
    - Citation accuracy
    - Page breaks
    
    Make adjustments if needed
    ```

12. **Export Multiple Formats**
    ```
    Generate in multiple formats:
    1. PDF: For submission
    2. Word: For editing
    3. LaTeX: For journal templates
    
    Download all versions
    ```

**Expected Outcome**:
- Publication-ready scientific report
- Properly formatted citations
- High-quality figures and tables
- Multiple export formats

---

### Tutorial 7: Distributed Processing for Large Datasets (30 minutes)

**Goal**: Process a 50GB dataset using distributed computing

**Prerequisites**:
- Large dataset (>10GB)
- Access to processing cluster

**Part A: Cluster Setup**

1. **Check Cluster Status**
   ```
   1. Navigate to Processing → Cluster
   2. View current status:
      - Workers: 4 active
      - CPU: 32 cores available
      - Memory: 128 GB available
   3. Check queue: 0 jobs waiting
   ```

2. **Scale Cluster (if needed)**
   ```
   1. Click "Scale Cluster"
   2. Target workers: 8
   3. Worker specs:
      - CPU: 8 cores
      - Memory: 16 GB
   4. Click "Scale Up"
   5. Wait 2 minutes for new workers
   ```

**Part B: Job Submission**

3. **Prepare Job**
   ```
   1. Click "Submit Job"
   2. Job name: "Large Dataset Normalization"
   3. Select dataset: large_genomics_data.csv (50GB)
   4. Operation: Normalize
   5. Method: Z-score
   ```

4. **Configure Resources**
   ```
   1. Workers: 8
   2. Memory per worker: 8 GB
   3. Partition size: Auto
   4. Priority: High
   5. Timeout: 1 hour
   ```

5. **Submit and Monitor**
   ```
   1. Click "Submit Job"
   2. Job queued immediately
   3. Starts within 30 seconds
   4. Monitor dashboard:
      - Progress: 0% → 100%
      - Tasks: 0/100 → 100/100
      - Time remaining: 45 min → 0 min
   ```

**Part C: Monitoring and Management**

6. **View Real-time Progress**
   ```
   Dashboard shows:
   - Overall progress bar
   - Task completion rate
   - Worker utilization
   - Memory usage
   - Network I/O
   - Estimated completion
   ```

7. **Handle Issues**
   ```
   If worker fails:
   1. System detects failure
   2. Task automatically reassigned
   3. No data loss
   4. Processing continues
   
   If job stalls:
   1. Check worker logs
   2. Identify bottleneck
   3. Adjust parameters
   4. Restart if needed
   ```

**Part D: Results Retrieval**

8. **Download Results**
   ```
   1. Job completes in 42 minutes
   2. Notification received
   3. Click "Download Results"
   4. Choose format:
      - Parquet: Fast, compressed
      - CSV: Compatible
      - HDF5: Scientific
   5. Download (5 minutes for 50GB)
   ```

9. **Verify Quality**
   ```
   1. Check processing logs
   2. Review quality metrics
   3. Verify data integrity
   4. Compare with expected results
   5. Validate sample records
   ```

**Expected Outcome**:
- Successfully processed 50GB dataset
- Processing time: ~40 minutes (vs. hours on single machine)
- High-quality normalized data
- Understanding of distributed processing

---

## Advanced Tutorials

### Tutorial 8: Custom Plugin Development

See [Plugin Development Guide](PLUGIN_DEVELOPMENT_GUIDE.md)

### Tutorial 9: API Integration

See [API Integration Guide](API_INTEGRATION_GUIDE.md)

### Tutorial 10: Security and Compliance

See [Security Best Practices](SECURITY_GUIDE.md)

---

## Video Tutorials

All tutorials available as video walkthroughs:
- YouTube: https://youtube.com/omniscope
- Duration: 10-30 minutes each
- Includes live demonstrations
- Downloadable example data

---

## Practice Datasets

Download practice datasets:
- `cancer_data.csv` - 500 samples, 50 features
- `large_genomics.csv` - 10,000 samples, 20,000 features
- `proteomics_data.csv` - 200 samples, 5,000 proteins
- `time_series_data.csv` - Longitudinal data

Available at: https://data.omniscope.ai/tutorials

---

## Next Steps

After completing tutorials:
1. Try with your own data
2. Explore advanced features
3. Join community forum
4. Share your workflows
5. Contribute to documentation

## Getting Help

- **Tutorial Issues**: tutorials@omniscope.ai
- **Community Forum**: https://community.omniscope.ai
- **Live Chat**: Available during tutorials
- **Office Hours**: Tuesdays 2-4 PM EST
