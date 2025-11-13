# Statistical Analysis Module - Quick Start Guide

## Overview
The Statistical Analysis Module provides advanced statistical methods for multi-omics research, including survival analysis, time-series forecasting, multi-omics integration, Bayesian inference, multiple testing correction, and power analysis.

## Installation

### Install Required Dependencies
```bash
pip install lifelines==0.27.8 statsmodels==0.14.1 prophet==1.1.5 pymc==5.10.3 arviz==0.17.0 seaborn==0.13.0
```

### Verify Installation
```bash
python test_statistical_analysis.py
```

## API Endpoints

All endpoints are available under `/api/statistics/` prefix.

### 1. Survival Analysis

#### Kaplan-Meier Analysis
```bash
curl -X POST "http://localhost:8001/api/statistics/survival-analysis" \
  -F "file=@survival_data.csv" \
  -F 'request={"time_column":"time","event_column":"event","group_column":"treatment","method":"kaplan_meier"}'
```

**CSV Format**:
```csv
time,event,treatment
12.5,1,A
8.3,0,B
15.2,1,A
...
```

#### Cox Proportional Hazards
```bash
curl -X POST "http://localhost:8001/api/statistics/survival-analysis" \
  -F "file=@survival_data.csv" \
  -F 'request={"time_column":"time","event_column":"event","method":"cox","covariates":["age","treatment"]}'
```

### 2. Time-Series Analysis

#### ARIMA Forecasting
```bash
curl -X POST "http://localhost:8001/api/statistics/time-series" \
  -F "file=@timeseries_data.csv" \
  -F 'request={"method":"arima","forecast_steps":10,"arima_order":[1,1,1]}'
```

**CSV Format**:
```csv
value
45.2
47.8
46.3
...
```

#### Prophet Forecasting
```bash
curl -X POST "http://localhost:8001/api/statistics/time-series" \
  -F "file=@timeseries_data.csv" \
  -F 'request={"method":"prophet","forecast_steps":30,"seasonality_mode":"additive"}'
```

**CSV Format** (Prophet requires 'ds' and 'y' columns):
```csv
ds,y
2020-01-01,45.2
2020-01-02,47.8
2020-01-03,46.3
...
```

#### LSTM Forecasting
```bash
curl -X POST "http://localhost:8001/api/statistics/time-series" \
  -F "file=@timeseries_data.csv" \
  -F 'request={"method":"lstm","forecast_steps":10,"lookback":10,"epochs":50}'
```

### 3. Multi-Omics Integration

#### MOFA Analysis
```bash
curl -X POST "http://localhost:8001/api/statistics/multi-omics-integration" \
  -F "files=@genomics.csv" \
  -F "files=@proteomics.csv" \
  -F "files=@metabolomics.csv" \
  -F 'request={"method":"mofa","n_factors":10}'
```

**CSV Format** (each file is one omics layer):
```csv
sample_id,feature1,feature2,feature3,...
sample1,0.5,1.2,0.8,...
sample2,0.7,1.1,0.9,...
...
```

#### DIABLO Analysis
```bash
curl -X POST "http://localhost:8001/api/statistics/multi-omics-integration" \
  -F "files=@genomics.csv" \
  -F "files=@proteomics.csv" \
  -F 'request={"method":"diablo","n_factors":5,"outcome_column":"outcome"}'
```

### 4. Bayesian Inference

#### Bayesian Linear Regression
```bash
curl -X POST "http://localhost:8001/api/statistics/bayesian-inference" \
  -F "file=@regression_data.csv" \
  -F 'request={"method":"linear_regression","target_column":"outcome","feature_columns":["age","biomarker1","biomarker2"],"n_samples":2000}'
```

**CSV Format**:
```csv
outcome,age,biomarker1,biomarker2
5.2,45,0.8,1.2
6.1,52,0.9,1.5
...
```

#### Bayesian t-test
```bash
curl -X POST "http://localhost:8001/api/statistics/bayesian-inference" \
  -F "file=@ttest_data.csv" \
  -F 'request={"method":"t_test","target_column":"value","group_column":"group","n_samples":2000}'
```

**CSV Format**:
```csv
value,group
5.2,A
6.1,B
5.8,A
...
```

### 5. Multiple Testing Correction

#### Correct P-values
```bash
curl -X POST "http://localhost:8001/api/statistics/multiple-testing-correction" \
  -H "Content-Type: application/json" \
  -d '{"pvalues":[0.001,0.05,0.02,0.15,0.003],"method":"fdr_bh","alpha":0.05}'
```

#### Permutation Test
```bash
curl -X POST "http://localhost:8001/api/statistics/permutation-test" \
  -F "file=@comparison_data.csv" \
  -F 'request={"group1_column":"group1","group2_column":"group2","n_permutations":10000,"statistic":"mean_diff"}'
```

**CSV Format**:
```csv
group1,group2
5.2,4.8
6.1,5.2
5.8,4.9
...
```

### 6. Power Analysis

#### Calculate Required Sample Size
```bash
curl -X POST "http://localhost:8001/api/statistics/power-analysis" \
  -H "Content-Type: application/json" \
  -d '{"test":"t_test","effect_size":0.5,"alpha":0.05,"power":0.8,"alternative":"two-sided"}'
```

#### Calculate Achieved Power
```bash
curl -X POST "http://localhost:8001/api/statistics/power-analysis" \
  -H "Content-Type: application/json" \
  -d '{"test":"t_test","effect_size":0.5,"alpha":0.05,"n_samples":64,"alternative":"two-sided"}'
```

#### Calculate Effect Size
```bash
curl -X POST "http://localhost:8001/api/statistics/effect-size" \
  -F "file=@comparison_data.csv" \
  -F 'request={"group1_column":"group1","group2_column":"group2","effect_type":"cohen_d"}'
```

## Python Client Examples

### Example 1: Survival Analysis
```python
import requests
import pandas as pd

# Prepare data
data = pd.DataFrame({
    'time': [12.5, 8.3, 15.2, 10.1, 14.8],
    'event': [1, 0, 1, 1, 0],
    'treatment': ['A', 'B', 'A', 'B', 'A']
})
data.to_csv('survival_data.csv', index=False)

# Make request
files = {'file': open('survival_data.csv', 'rb')}
data = {
    'time_column': 'time',
    'event_column': 'event',
    'group_column': 'treatment',
    'method': 'kaplan_meier'
}

response = requests.post(
    'http://localhost:8001/api/statistics/survival-analysis',
    files=files,
    data={'request': str(data)}
)

result = response.json()
print(result['result']['logrank_test'])
```

### Example 2: Time-Series Forecasting
```python
import requests
import pandas as pd
import numpy as np

# Prepare data
dates = pd.date_range('2020-01-01', periods=100, freq='D')
values = np.cumsum(np.random.randn(100)) + 50

data = pd.DataFrame({'ds': dates, 'y': values})
data.to_csv('timeseries_data.csv', index=False)

# Make request
files = {'file': open('timeseries_data.csv', 'rb')}
params = {
    'method': 'prophet',
    'forecast_steps': 30,
    'seasonality_mode': 'additive'
}

response = requests.post(
    'http://localhost:8001/api/statistics/time-series',
    files=files,
    data={'request': str(params)}
)

result = response.json()
forecast = result['result']['forecast']
print(f"Forecasted values: {forecast['yhat'][:5]}")
```

### Example 3: Multi-Omics Integration
```python
import requests
import pandas as pd
import numpy as np

# Prepare multi-omics data
genomics = pd.DataFrame(np.random.randn(50, 100))
proteomics = pd.DataFrame(np.random.randn(50, 80))
metabolomics = pd.DataFrame(np.random.randn(50, 60))

genomics.to_csv('genomics.csv')
proteomics.to_csv('proteomics.csv')
metabolomics.to_csv('metabolomics.csv')

# Make request
files = [
    ('files', open('genomics.csv', 'rb')),
    ('files', open('proteomics.csv', 'rb')),
    ('files', open('metabolomics.csv', 'rb'))
]
params = {
    'method': 'mofa',
    'n_factors': 10
}

response = requests.post(
    'http://localhost:8001/api/statistics/multi-omics-integration',
    files=files,
    data={'request': str(params)}
)

result = response.json()
print(f"Variance explained: {result['result']['variance_explained']}")
```

### Example 4: Bayesian Inference
```python
import requests
import pandas as pd
import numpy as np

# Prepare data
n = 100
data = pd.DataFrame({
    'outcome': 2 + 3*np.random.randn(n) + np.random.randn(n),
    'age': np.random.normal(60, 10, n),
    'biomarker1': np.random.randn(n),
    'biomarker2': np.random.randn(n)
})
data.to_csv('regression_data.csv', index=False)

# Make request
files = {'file': open('regression_data.csv', 'rb')}
params = {
    'method': 'linear_regression',
    'target_column': 'outcome',
    'feature_columns': ['age', 'biomarker1', 'biomarker2'],
    'n_samples': 2000
}

response = requests.post(
    'http://localhost:8001/api/statistics/bayesian-inference',
    files=files,
    data={'request': str(params)}
)

result = response.json()
print(f"Posterior means: {result['result']['posterior_means']}")
```

### Example 5: Power Analysis
```python
import requests

# Calculate required sample size
params = {
    'test': 't_test',
    'effect_size': 0.5,
    'alpha': 0.05,
    'power': 0.8,
    'alternative': 'two-sided'
}

response = requests.post(
    'http://localhost:8001/api/statistics/power-analysis',
    json=params
)

result = response.json()
print(f"Required sample size per group: {result['result']['result']}")
```

## Response Format

All endpoints return JSON responses with the following structure:

```json
{
  "status": "success",
  "result": {
    "method": "method_name",
    "timestamp": "2024-01-01T00:00:00",
    "plot": "data:image/png;base64,...",
    ...
  }
}
```

### Visualization
Most methods return a `plot` field containing a base64-encoded PNG image that can be:
- Displayed in web browsers: `<img src="{plot}" />`
- Saved to file: Decode base64 and write to file
- Embedded in reports

## Error Handling

Errors return HTTP status codes with detailed messages:

```json
{
  "detail": "Error message describing what went wrong"
}
```

Common error codes:
- `400`: Invalid input (missing columns, wrong format)
- `500`: Internal server error (computation failed)

## Health Check

Check module status:
```bash
curl http://localhost:8001/api/statistics/health
```

Response:
```json
{
  "status": "healthy",
  "module": "statistical_analysis",
  "available_methods": {
    "survival_analysis": ["kaplan_meier", "cox", "logrank_test"],
    "time_series": ["arima", "prophet", "lstm"],
    "multi_omics": ["mofa", "diablo"],
    "bayesian": ["linear_regression", "t_test", "variational"],
    "multiple_testing": ["bonferroni", "fdr_bh", "fdr_by", "permutation"],
    "power_analysis": ["t_test", "anova", "effect_size"]
  }
}
```

## Best Practices

### 1. Data Preparation
- Ensure CSV files have proper headers
- Handle missing values before upload
- Use appropriate data types
- Normalize/standardize when needed

### 2. Method Selection
- **Survival Analysis**: Use Kaplan-Meier for univariate, Cox for multivariate
- **Time-Series**: ARIMA for stationary, Prophet for seasonality, LSTM for complex patterns
- **Multi-Omics**: MOFA for unsupervised, DIABLO for supervised
- **Bayesian**: Use when uncertainty quantification is important
- **Multiple Testing**: Always correct when testing multiple hypotheses
- **Power Analysis**: Plan experiments before data collection

### 3. Interpretation
- Check convergence diagnostics for Bayesian methods
- Validate model assumptions
- Consider effect sizes, not just p-values
- Use visualizations to understand results

### 4. Performance
- Start with smaller datasets for testing
- Use appropriate sample sizes for MCMC
- Consider computational time for LSTM
- Cache results when possible

## Troubleshooting

### Issue: Module not found
**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

### Issue: Convergence warnings in Bayesian methods
**Solution**: Increase number of samples or chains
```python
{"n_samples": 5000, "n_chains": 4}
```

### Issue: LSTM training too slow
**Solution**: Reduce epochs or use GPU
```python
{"epochs": 20}  # Reduce from default 50
```

### Issue: Memory error with large datasets
**Solution**: Reduce data size or use sampling
```python
data = data.sample(n=10000)  # Sample before upload
```

## Support

For issues or questions:
1. Check the implementation summary: `TASK_8_IMPLEMENTATION_SUMMARY.md`
2. Run the test suite: `python test_statistical_analysis.py`
3. Review API documentation: `http://localhost:8001/docs`

## Next Steps

1. Install dependencies
2. Start the server: `python main.py`
3. Try the examples above
4. Explore the API documentation
5. Integrate with your analysis pipeline

Happy analyzing! 🎉
