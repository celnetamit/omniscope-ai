"""
Test script for Statistical Analysis Module
Tests all implemented statistical methods
"""

import pandas as pd
import numpy as np
from backend_db.statistical_analysis import (
    SurvivalAnalysisService,
    TimeSeriesAnalysisService,
    MultiOmicsIntegrationService,
    BayesianInferenceService,
    MultipleTestingCorrectionService,
    PowerAnalysisService
)

def test_survival_analysis():
    """Test survival analysis methods"""
    print("\n" + "="*80)
    print("Testing Survival Analysis")
    print("="*80)
    
    # Create sample survival data
    np.random.seed(42)
    n_samples = 100
    data = pd.DataFrame({
        'time': np.random.exponential(10, n_samples),
        'event': np.random.binomial(1, 0.7, n_samples),
        'group': np.random.choice(['A', 'B'], n_samples),
        'age': np.random.normal(60, 10, n_samples),
        'treatment': np.random.choice([0, 1], n_samples)
    })
    
    # Test Kaplan-Meier
    print("\n1. Testing Kaplan-Meier Analysis...")
    try:
        result = SurvivalAnalysisService.kaplan_meier_analysis(
            data=data,
            time_column='time',
            event_column='event',
            group_column='group'
        )
        print(f"   ✓ Kaplan-Meier completed")
        print(f"   - Method: {result['method']}")
        if 'logrank_test' in result:
            print(f"   - Log-rank p-value: {result['logrank_test']['p_value']:.4f}")
        print(f"   - Plot generated: {'plot' in result}")
    except Exception as e:
        print(f"   ✗ Kaplan-Meier failed: {e}")
    
    # Test Cox Regression
    print("\n2. Testing Cox Proportional Hazards...")
    try:
        result = SurvivalAnalysisService.cox_proportional_hazards(
            data=data,
            time_column='time',
            event_column='event',
            covariates=['age', 'treatment']
        )
        print(f"   ✓ Cox regression completed")
        print(f"   - Concordance index: {result['concordance_index']:.4f}")
        print(f"   - AIC: {result['aic']:.2f}")
        print(f"   - Hazard ratios: {result['hazard_ratios']}")
    except Exception as e:
        print(f"   ✗ Cox regression failed: {e}")
    
    # Test Log-rank test
    print("\n3. Testing Log-rank Test...")
    try:
        result = SurvivalAnalysisService.logrank_test_analysis(
            data=data,
            time_column='time',
            event_column='event',
            group_column='group'
        )
        print(f"   ✓ Log-rank test completed")
        print(f"   - Test statistic: {result['test_statistic']:.4f}")
        print(f"   - P-value: {result['p_value']:.4f}")
        print(f"   - Significant: {result['significant']}")
    except Exception as e:
        print(f"   ✗ Log-rank test failed: {e}")


def test_time_series_analysis():
    """Test time-series analysis methods"""
    print("\n" + "="*80)
    print("Testing Time-Series Analysis")
    print("="*80)
    
    # Create sample time series data
    np.random.seed(42)
    n_points = 100
    time_series = pd.Series(
        np.cumsum(np.random.randn(n_points)) + 50,
        index=pd.date_range('2020-01-01', periods=n_points, freq='D')
    )
    
    # Test ARIMA
    print("\n1. Testing ARIMA Analysis...")
    try:
        result = TimeSeriesAnalysisService.arima_analysis(
            data=time_series,
            order=(1, 1, 1),
            forecast_steps=10
        )
        print(f"   ✓ ARIMA completed")
        print(f"   - AIC: {result['aic']:.2f}")
        print(f"   - BIC: {result['bic']:.2f}")
        print(f"   - Forecast length: {len(result['forecast'])}")
        print(f"   - Plot generated: {'plot' in result}")
    except Exception as e:
        print(f"   ✗ ARIMA failed: {e}")
    
    # Test Prophet
    print("\n2. Testing Prophet Analysis...")
    try:
        prophet_data = pd.DataFrame({
            'ds': time_series.index,
            'y': time_series.values
        })
        result = TimeSeriesAnalysisService.prophet_analysis(
            data=prophet_data,
            forecast_periods=30
        )
        print(f"   ✓ Prophet completed")
        print(f"   - Forecast periods: {result['forecast_periods']}")
        print(f"   - Forecast length: {len(result['forecast']['dates'])}")
        print(f"   - Plots generated: 2")
    except Exception as e:
        print(f"   ✗ Prophet failed: {e}")
    
    # Test LSTM
    print("\n3. Testing LSTM Forecast...")
    try:
        result = TimeSeriesAnalysisService.lstm_forecast(
            data=time_series.values,
            lookback=10,
            forecast_steps=10,
            epochs=20
        )
        print(f"   ✓ LSTM completed")
        print(f"   - Test MSE: {result['test_mse']:.4f}")
        print(f"   - Forecast length: {len(result['forecast'])}")
        print(f"   - Plot generated: {'plot' in result}")
    except Exception as e:
        print(f"   ✗ LSTM failed: {e}")


def test_multi_omics_integration():
    """Test multi-omics integration methods"""
    print("\n" + "="*80)
    print("Testing Multi-Omics Integration")
    print("="*80)
    
    # Create sample multi-omics data
    np.random.seed(42)
    n_samples = 50
    
    omics_data = {
        'genomics': pd.DataFrame(
            np.random.randn(n_samples, 100),
            columns=[f'gene_{i}' for i in range(100)]
        ),
        'proteomics': pd.DataFrame(
            np.random.randn(n_samples, 80),
            columns=[f'protein_{i}' for i in range(80)]
        ),
        'metabolomics': pd.DataFrame(
            np.random.randn(n_samples, 60),
            columns=[f'metabolite_{i}' for i in range(60)]
        )
    }
    
    # Test MOFA
    print("\n1. Testing MOFA Analysis...")
    try:
        result = MultiOmicsIntegrationService.mofa_analysis(
            omics_data=omics_data,
            n_factors=5
        )
        print(f"   ✓ MOFA completed")
        print(f"   - Number of factors: {result['n_factors']}")
        print(f"   - Omics layers: {result['omics_layers']}")
        print(f"   - Variance explained (first 3): {result['variance_explained'][:3]}")
        print(f"   - Plot generated: {'plot' in result}")
    except Exception as e:
        print(f"   ✗ MOFA failed: {e}")
    
    # Test DIABLO
    print("\n2. Testing DIABLO Analysis...")
    try:
        outcome = np.random.randn(n_samples)
        result = MultiOmicsIntegrationService.diablo_analysis(
            omics_data=omics_data,
            outcome=outcome,
            n_components=2
        )
        print(f"   ✓ DIABLO completed")
        print(f"   - Number of components: {result['n_components']}")
        print(f"   - Omics layers: {result['omics_layers']}")
        print(f"   - Plot generated: {'plot' in result}")
    except Exception as e:
        print(f"   ✗ DIABLO failed: {e}")


def test_bayesian_inference():
    """Test Bayesian inference methods"""
    print("\n" + "="*80)
    print("Testing Bayesian Inference")
    print("="*80)
    
    # Create sample data
    np.random.seed(42)
    n_samples = 100
    X = np.random.randn(n_samples, 3)
    y = 2 + 3*X[:, 0] - 1.5*X[:, 1] + 0.5*X[:, 2] + np.random.randn(n_samples)*0.5
    
    # Test Bayesian Linear Regression
    print("\n1. Testing Bayesian Linear Regression...")
    try:
        result = BayesianInferenceService.bayesian_linear_regression(
            X=X,
            y=y,
            n_samples=1000,
            n_chains=2
        )
        print(f"   ✓ Bayesian regression completed")
        print(f"   - Posterior means: {result['posterior_means']}")
        print(f"   - R-hat values: {result['rhat']}")
        print(f"   - Plot generated: {'plot' in result}")
    except Exception as e:
        print(f"   ✗ Bayesian regression failed: {e}")
    
    # Test Bayesian t-test
    print("\n2. Testing Bayesian t-test...")
    try:
        group1 = np.random.randn(50) + 1
        group2 = np.random.randn(50)
        result = BayesianInferenceService.bayesian_t_test(
            group1=group1,
            group2=group2,
            n_samples=1000
        )
        print(f"   ✓ Bayesian t-test completed")
        print(f"   - Effect size mean: {result['effect_size_mean']:.4f}")
        print(f"   - 95% CI: [{result['credible_interval_95']['lower']:.4f}, {result['credible_interval_95']['upper']:.4f}]")
        print(f"   - Prob positive effect: {result['prob_positive_effect']:.4f}")
        print(f"   - Plot generated: {'plot' in result}")
    except Exception as e:
        print(f"   ✗ Bayesian t-test failed: {e}")
    
    # Test Variational Inference
    print("\n3. Testing Variational Inference...")
    try:
        result = BayesianInferenceService.variational_inference(
            X=X,
            y=y,
            n_iterations=10000
        )
        print(f"   ✓ Variational inference completed")
        print(f"   - Posterior means: {result['posterior_means']}")
        print(f"   - Final ELBO: {result['final_elbo']:.2f}")
        print(f"   - Plot generated: {'plot' in result}")
    except Exception as e:
        print(f"   ✗ Variational inference failed: {e}")


def test_multiple_testing_correction():
    """Test multiple testing correction methods"""
    print("\n" + "="*80)
    print("Testing Multiple Testing Correction")
    print("="*80)
    
    # Create sample p-values
    np.random.seed(42)
    pvalues = np.random.uniform(0, 1, 100).tolist()
    
    # Test different correction methods
    methods = ['bonferroni', 'fdr_bh', 'fdr_by']
    
    for method in methods:
        print(f"\n{methods.index(method) + 1}. Testing {method.upper()} correction...")
        try:
            result = MultipleTestingCorrectionService.correct_pvalues(
                pvalues=pvalues,
                method=method,
                alpha=0.05
            )
            print(f"   ✓ {method.upper()} completed")
            print(f"   - Number of tests: {result['n_tests']}")
            print(f"   - Significant tests: {result['n_significant']}")
            print(f"   - Rejection rate: {result['n_significant']/result['n_tests']:.2%}")
        except Exception as e:
            print(f"   ✗ {method.upper()} failed: {e}")
    
    # Test permutation test
    print(f"\n{len(methods) + 1}. Testing Permutation Test...")
    try:
        group1 = np.random.randn(50) + 0.5
        group2 = np.random.randn(50)
        result = MultipleTestingCorrectionService.permutation_test(
            group1=group1,
            group2=group2,
            n_permutations=1000,
            statistic='mean_diff'
        )
        print(f"   ✓ Permutation test completed")
        print(f"   - Observed statistic: {result['observed_statistic']:.4f}")
        print(f"   - P-value: {result['p_value']:.4f}")
        print(f"   - Significant: {result['significant']}")
    except Exception as e:
        print(f"   ✗ Permutation test failed: {e}")


def test_power_analysis():
    """Test power analysis methods"""
    print("\n" + "="*80)
    print("Testing Power Analysis")
    print("="*80)
    
    # Test t-test power analysis
    print("\n1. Testing t-test Power Analysis (sample size calculation)...")
    try:
        result = PowerAnalysisService.ttest_power_analysis(
            effect_size=0.5,
            alpha=0.05,
            power=0.8
        )
        print(f"   ✓ t-test power analysis completed")
        print(f"   - Effect size: {result['effect_size']}")
        print(f"   - Required sample size per group: {result['result']}")
    except Exception as e:
        print(f"   ✗ t-test power analysis failed: {e}")
    
    print("\n2. Testing t-test Power Analysis (power calculation)...")
    try:
        result = PowerAnalysisService.ttest_power_analysis(
            effect_size=0.5,
            alpha=0.05,
            n_samples=64
        )
        print(f"   ✓ t-test power analysis completed")
        print(f"   - Effect size: {result['effect_size']}")
        print(f"   - Achieved power: {result['result']:.4f}")
    except Exception as e:
        print(f"   ✗ t-test power analysis failed: {e}")
    
    # Test ANOVA power analysis
    print("\n3. Testing ANOVA Power Analysis...")
    try:
        result = PowerAnalysisService.anova_power_analysis(
            effect_size=0.3,
            n_groups=3,
            alpha=0.05,
            power=0.8
        )
        print(f"   ✓ ANOVA power analysis completed")
        print(f"   - Effect size: {result['effect_size']}")
        print(f"   - Number of groups: {result['n_groups']}")
        print(f"   - Required sample size per group: {result['result']}")
    except Exception as e:
        print(f"   ✗ ANOVA power analysis failed: {e}")
    
    # Test effect size calculation
    print("\n4. Testing Effect Size Calculation...")
    try:
        group1 = np.random.randn(50) + 0.5
        group2 = np.random.randn(50)
        result = PowerAnalysisService.calculate_effect_size(
            group1=group1,
            group2=group2,
            effect_type='cohen_d'
        )
        print(f"   ✓ Effect size calculation completed")
        print(f"   - Effect size (Cohen's d): {result['effect_size']:.4f}")
        print(f"   - Interpretation: {result['interpretation']}")
        print(f"   - Group 1 mean: {result['group1_mean']:.4f}")
        print(f"   - Group 2 mean: {result['group2_mean']:.4f}")
    except Exception as e:
        print(f"   ✗ Effect size calculation failed: {e}")


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("STATISTICAL ANALYSIS MODULE - COMPREHENSIVE TEST SUITE")
    print("="*80)
    
    try:
        test_survival_analysis()
    except Exception as e:
        print(f"\n✗ Survival analysis tests failed: {e}")
    
    try:
        test_time_series_analysis()
    except Exception as e:
        print(f"\n✗ Time-series analysis tests failed: {e}")
    
    try:
        test_multi_omics_integration()
    except Exception as e:
        print(f"\n✗ Multi-omics integration tests failed: {e}")
    
    try:
        test_bayesian_inference()
    except Exception as e:
        print(f"\n✗ Bayesian inference tests failed: {e}")
    
    try:
        test_multiple_testing_correction()
    except Exception as e:
        print(f"\n✗ Multiple testing correction tests failed: {e}")
    
    try:
        test_power_analysis()
    except Exception as e:
        print(f"\n✗ Power analysis tests failed: {e}")
    
    print("\n" + "="*80)
    print("TEST SUITE COMPLETED")
    print("="*80)
    print("\nNote: Some tests may show warnings from underlying libraries.")
    print("This is normal and does not indicate test failure.")


if __name__ == "__main__":
    main()
