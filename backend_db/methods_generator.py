"""
Methods Section Auto-Generator
Extracts pipeline steps and parameters to generate detailed methods descriptions
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json

class MethodsGenerator:
    """
    Automatic methods section generator for scientific reports
    
    Requirements: 5.4
    """
    
    def __init__(self):
        """Initialize methods generator"""
        self.software_versions = {
            "python": "3.11",
            "pandas": "2.1.3",
            "scikit-learn": "1.3.2",
            "numpy": "1.24.3",
            "scipy": "1.11.4",
            "pytorch": "2.1.2",
            "autogluon": "1.0.0",
            "mlflow": "2.9.2",
            "biopython": "1.83",
            "networkx": "3.2.1",
            "plotly": "5.18.0"
        }
    
    def generate_methods(
        self,
        pipeline_id: Optional[str] = None,
        model_id: Optional[str] = None,
        pipeline_data: Optional[Dict[str, Any]] = None,
        model_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate methods section from pipeline and model information
        
        Args:
            pipeline_id: ID of the pipeline to describe
            model_id: ID of the trained model
            pipeline_data: Pipeline configuration data (if not loading from DB)
            model_data: Model training data (if not loading from DB)
            
        Returns:
            Formatted methods section as HTML string
        """
        methods_html = "<div class='methods-section'>\n"
        
        # Data Processing section
        if pipeline_data or pipeline_id:
            methods_html += self._generate_data_processing_section(pipeline_data, pipeline_id)
        
        # Statistical Analysis section
        methods_html += self._generate_statistical_analysis_section()
        
        # Machine Learning section
        if model_data or model_id:
            methods_html += self._generate_ml_section(model_data, model_id)
        
        # Software and Tools section
        methods_html += self._generate_software_section()
        
        methods_html += "</div>"
        
        return methods_html
    
    def _generate_data_processing_section(
        self,
        pipeline_data: Optional[Dict[str, Any]],
        pipeline_id: Optional[str]
    ) -> str:
        """Generate data processing methods description"""
        section = "<h3>Data Processing</h3>\n"
        
        if pipeline_data:
            nodes = pipeline_data.get('nodes', [])
            
            # Describe data upload
            upload_nodes = [n for n in nodes if n.get('type') == 'upload']
            if upload_nodes:
                section += "<p>Data were uploaded and processed using the OmniScope AI platform. "
                section += "Quality control checks were performed to ensure data integrity, "
                section += "including validation of file formats, detection of missing values, "
                section += "and assessment of data distributions.</p>\n"
            
            # Describe preprocessing steps
            preprocess_nodes = [n for n in nodes if n.get('type') in ['normalize', 'filter', 'transform']]
            if preprocess_nodes:
                section += "<p>Data preprocessing included the following steps: "
                steps = []
                for node in preprocess_nodes:
                    node_type = node.get('type', 'unknown')
                    if node_type == 'normalize':
                        steps.append("normalization using z-score standardization")
                    elif node_type == 'filter':
                        steps.append("filtering to remove low-quality features")
                    elif node_type == 'transform':
                        steps.append("log transformation to stabilize variance")
                section += ", ".join(steps) + ".</p>\n"
            
            # Describe feature selection
            feature_nodes = [n for n in nodes if n.get('type') == 'feature_selection']
            if feature_nodes:
                section += "<p>Feature selection was performed to identify the most informative variables. "
                section += "Features with low variance or high correlation were removed to reduce dimensionality "
                section += "and improve model performance.</p>\n"
        else:
            section += "<p>Data processing pipeline details were not available for this analysis.</p>\n"
        
        return section
    
    def _generate_statistical_analysis_section(self) -> str:
        """Generate statistical analysis methods description"""
        section = "<h3>Statistical Analysis</h3>\n"
        
        section += "<p>Statistical analyses were performed using Python (version {}) ".format(
            self.software_versions['python']
        )
        section += "with the SciPy (version {}) and pandas (version {}) libraries. ".format(
            self.software_versions['scipy'],
            self.software_versions['pandas']
        )
        section += "Descriptive statistics including mean, median, standard deviation, and interquartile range "
        section += "were calculated for all continuous variables. "
        section += "Categorical variables were summarized using frequency counts and percentages.</p>\n"
        
        section += "<p>For hypothesis testing, appropriate statistical tests were selected based on data "
        section += "distribution and sample size. Continuous variables were tested for normality using the "
        section += "Shapiro-Wilk test. Parametric tests (t-tests, ANOVA) were used for normally distributed data, "
        section += "while non-parametric alternatives (Mann-Whitney U, Kruskal-Wallis) were applied to "
        section += "non-normal distributions.</p>\n"
        
        section += "<p>Multiple testing correction was applied using the Benjamini-Hochberg false discovery rate "
        section += "(FDR) method to control for Type I errors. Statistical significance was defined as "
        section += "FDR-adjusted p-value < 0.05.</p>\n"
        
        return section
    
    def _generate_ml_section(
        self,
        model_data: Optional[Dict[str, Any]],
        model_id: Optional[str]
    ) -> str:
        """Generate machine learning methods description"""
        section = "<h3>Machine Learning Analysis</h3>\n"
        
        if model_data:
            model_type = model_data.get('type', 'unknown')
            
            # Describe model selection
            section += "<p>Machine learning models were developed using "
            
            if model_type == 'automl':
                section += "automated machine learning (AutoML) with AutoGluon (version {}). ".format(
                    self.software_versions['autogluon']
                )
                section += "AutoML automatically evaluated multiple algorithm types including "
                section += "random forests, gradient boosting machines, neural networks, and support vector machines. "
                section += "The best-performing model was selected based on cross-validation performance.</p>\n"
            
            elif model_type == 'deep_learning':
                section += "deep learning with PyTorch (version {}). ".format(
                    self.software_versions['pytorch']
                )
                architecture = model_data.get('architecture', 'neural network')
                section += f"A {architecture} architecture was implemented with "
                section += "appropriate activation functions and regularization techniques.</p>\n"
            
            elif model_type == 'ensemble':
                section += "ensemble learning methods combining multiple base models. "
                section += "Predictions from individual models were aggregated using voting or stacking "
                section += "to improve overall performance and robustness.</p>\n"
            
            else:
                section += "scikit-learn (version {}) library.</p>\n".format(
                    self.software_versions['scikit-learn']
                )
            
            # Describe training procedure
            section += "<p>Model training was performed using k-fold cross-validation (k=5) to ensure "
            section += "robust performance estimates and prevent overfitting. "
            
            training_config = model_data.get('training_config', {})
            if training_config:
                if 'validation_split' in training_config:
                    val_split = training_config['validation_split']
                    section += f"Data were split into training ({int((1-val_split)*100)}%) and "
                    section += f"validation ({int(val_split*100)}%) sets. "
                
                if 'epochs' in training_config:
                    epochs = training_config['epochs']
                    section += f"Training was conducted for {epochs} epochs "
                
                if 'batch_size' in training_config:
                    batch_size = training_config['batch_size']
                    section += f"with a batch size of {batch_size}. "
            
            section += "Early stopping was implemented to prevent overfitting, "
            section += "with training halted if validation performance did not improve for consecutive epochs.</p>\n"
            
            # Describe hyperparameter optimization
            section += "<p>Hyperparameter optimization was performed using grid search or Bayesian optimization "
            section += "to identify optimal model configurations. "
            section += "Hyperparameters including learning rate, regularization strength, and model complexity "
            section += "were systematically tuned to maximize predictive performance.</p>\n"
            
            # Describe evaluation metrics
            metrics = model_data.get('metrics', {})
            if metrics:
                section += "<p>Model performance was evaluated using multiple metrics including "
                metric_names = []
                if 'accuracy' in metrics:
                    metric_names.append("accuracy")
                if 'auc' in metrics or 'roc_auc' in metrics:
                    metric_names.append("area under the receiver operating characteristic curve (AUC-ROC)")
                if 'f1_score' in metrics:
                    metric_names.append("F1 score")
                if 'precision' in metrics:
                    metric_names.append("precision")
                if 'recall' in metrics:
                    metric_names.append("recall")
                
                if metric_names:
                    section += ", ".join(metric_names) + ". "
                
                section += "Performance metrics were calculated on the held-out test set to provide "
                section += "unbiased estimates of model generalization.</p>\n"
        else:
            section += "<p>Machine learning model details were not available for this analysis.</p>\n"
        
        return section
    
    def _generate_software_section(self) -> str:
        """Generate software and tools section with version citations"""
        section = "<h3>Software and Tools</h3>\n"
        
        section += "<p>All analyses were conducted using Python version {} ".format(
            self.software_versions['python']
        )
        section += "with the following key libraries and their respective versions:</p>\n"
        
        section += "<ul>\n"
        section += "<li>NumPy {} for numerical computing</li>\n".format(
            self.software_versions['numpy']
        )
        section += "<li>pandas {} for data manipulation and analysis</li>\n".format(
            self.software_versions['pandas']
        )
        section += "<li>scikit-learn {} for machine learning algorithms</li>\n".format(
            self.software_versions['scikit-learn']
        )
        section += "<li>SciPy {} for scientific computing and statistics</li>\n".format(
            self.software_versions['scipy']
        )
        section += "<li>PyTorch {} for deep learning</li>\n".format(
            self.software_versions['pytorch']
        )
        section += "<li>AutoGluon {} for automated machine learning</li>\n".format(
            self.software_versions['autogluon']
        )
        section += "<li>MLflow {} for experiment tracking and model management</li>\n".format(
            self.software_versions['mlflow']
        )
        section += "<li>BioPython {} for biological data analysis</li>\n".format(
            self.software_versions['biopython']
        )
        section += "<li>NetworkX {} for network analysis</li>\n".format(
            self.software_versions['networkx']
        )
        section += "<li>Plotly {} for interactive visualizations</li>\n".format(
            self.software_versions['plotly']
        )
        section += "</ul>\n"
        
        section += "<p>All computational analyses were performed on the OmniScope AI platform, "
        section += "which provides an integrated environment for multi-omics data analysis. "
        section += "Code and analysis workflows are available upon request to ensure reproducibility.</p>\n"
        
        return section
    
    def add_custom_method(self, title: str, description: str) -> str:
        """
        Add a custom methods subsection
        
        Args:
            title: Subsection title
            description: Method description
            
        Returns:
            Formatted HTML section
        """
        section = f"<h3>{title}</h3>\n"
        section += f"<p>{description}</p>\n"
        return section
    
    def update_software_version(self, software: str, version: str):
        """Update software version information"""
        self.software_versions[software] = version
    
    def get_software_citations(self) -> List[Dict[str, Any]]:
        """
        Get citation information for software tools
        
        Returns:
            List of citation dictionaries
        """
        citations = [
            {
                "citation_id": "python",
                "authors": ["Van Rossum, G.", "Drake, F. L."],
                "year": 2009,
                "title": "Python 3 Reference Manual",
                "publisher": "CreateSpace",
                "citation_type": "book"
            },
            {
                "citation_id": "numpy",
                "authors": ["Harris, C. R.", "et al."],
                "year": 2020,
                "title": "Array programming with NumPy",
                "journal": "Nature",
                "volume": "585",
                "pages": "357-362",
                "doi": "10.1038/s41586-020-2649-2",
                "citation_type": "article"
            },
            {
                "citation_id": "pandas",
                "authors": ["McKinney, W."],
                "year": 2010,
                "title": "Data structures for statistical computing in Python",
                "journal": "Proceedings of the 9th Python in Science Conference",
                "pages": "56-61",
                "citation_type": "article"
            },
            {
                "citation_id": "scikit-learn",
                "authors": ["Pedregosa, F.", "et al."],
                "year": 2011,
                "title": "Scikit-learn: Machine Learning in Python",
                "journal": "Journal of Machine Learning Research",
                "volume": "12",
                "pages": "2825-2830",
                "citation_type": "article"
            },
            {
                "citation_id": "pytorch",
                "authors": ["Paszke, A.", "et al."],
                "year": 2019,
                "title": "PyTorch: An Imperative Style, High-Performance Deep Learning Library",
                "journal": "Advances in Neural Information Processing Systems",
                "volume": "32",
                "citation_type": "article"
            }
        ]
        return citations
