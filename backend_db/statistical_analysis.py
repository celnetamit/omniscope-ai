"""
Statistical Analysis Service for OmniScope AI
Provides advanced statistical methods including survival analysis, time-series, multi-omics integration, and Bayesian inference
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json
import io
import base64

# Survival Analysis
from lifelines import KaplanMeierFitter, CoxPHFitter
from lifelines.statistics import logrank_test

# Time-Series Analysis
from statsmodels.tsa.arima.model import ARIMA
from prophet import Prophet

# Multi-Omics Integration
from sklearn.decomposition import PCA, FactorAnalysis
from sklearn.cross_decomposition import PLSCanonical

# Bayesian Inference
import pymc as pm
import arviz as az

# Multiple Testing Correction
from statsmodels.stats.multitest import multipletests

# Power Analysis
from statsmodels.stats.power import TTestIndPower, FTestAnovaPower

# Visualization
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns


class SurvivalAnalysisService:
    """Service for survival analysis using lifelines"""
    
    @staticmethod
    def kaplan_meier_analysis(
        data: pd.DataFrame,
        time_column: str,
        event_column: str,
        group_column: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Perform Kaplan-Meier survival analysis
        
        Args:
            data: DataFrame with survival data
            time_column: Column name for time to event
            event_column: Column name for event indicator (1=event, 0=censored)
            group_column: Optional column for group comparison
            
        Returns:
            Dictionary with survival curves, statistics, and plot
        """
        results = {
            "method": "kaplan_meier",
            "time_column": time_column,
            "event_column": event_column,
            "timestamp": datetime.now().isoformat()
        }
        
        if group_column:
            # Perform grouped analysis
            groups = data[group_column].unique()
            results["groups"] = {}
            
            kmf = KaplanMeierFitter()
            
            # Create plot
            fig, ax = plt.subplots(figsize=(10, 6))
            
            for group in groups:
                group_data = data[data[group_column] == group]
                kmf.fit(
                    durations=group_data[time_column],
                    event_observed=group_data[event_column],
                    label=str(group)
                )
                
                # Store survival function
                results["groups"][str(group)] = {
                    "survival_function": kmf.survival_function_.to_dict(),
                    "median_survival": float(kmf.median_survival_time_) if not pd.isna(kmf.median_survival_time_) else None,
                    "confidence_interval": kmf.confidence_interval_.to_dict()
                }
                
                # Plot
                kmf.plot_survival_function(ax=ax)
            
            # Perform log-rank test for group comparison
            if len(groups) == 2:
                group1_data = data[data[group_column] == groups[0]]
                group2_data = data[data[group_column] == groups[1]]
                
                logrank_result = logrank_test(
                    durations_A=group1_data[time_column],
                    durations_B=group2_data[time_column],
                    event_observed_A=group1_data[event_column],
                    event_observed_B=group2_data[event_column]
                )
                
                results["logrank_test"] = {
                    "test_statistic": float(logrank_result.test_statistic),
                    "p_value": float(logrank_result.p_value),
                    "significant": logrank_result.p_value < 0.05
                }
            
            ax.set_xlabel("Time")
            ax.set_ylabel("Survival Probability")
            ax.set_title(f"Kaplan-Meier Survival Curves by {group_column}")
            ax.legend()
            
        else:
            # Single group analysis
            kmf = KaplanMeierFitter()
            kmf.fit(
                durations=data[time_column],
                event_observed=data[event_column]
            )
            
            results["survival_function"] = kmf.survival_function_.to_dict()
            results["median_survival"] = float(kmf.median_survival_time_) if not pd.isna(kmf.median_survival_time_) else None
            results["confidence_interval"] = kmf.confidence_interval_.to_dict()
            
            # Create plot
            fig, ax = plt.subplots(figsize=(10, 6))
            kmf.plot_survival_function(ax=ax)
            ax.set_xlabel("Time")
            ax.set_ylabel("Survival Probability")
            ax.set_title("Kaplan-Meier Survival Curve")
        
        # Convert plot to base64
        buf = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        plot_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        
        results["plot"] = f"data:image/png;base64,{plot_base64}"
        
        return results
    
    @staticmethod
    def cox_proportional_hazards(
        data: pd.DataFrame,
        time_column: str,
        event_column: str,
        covariates: List[str]
    ) -> Dict[str, Any]:
        """
        Perform Cox Proportional Hazards regression
        
        Args:
            data: DataFrame with survival data
            time_column: Column name for time to event
            event_column: Column name for event indicator
            covariates: List of covariate column names
            
        Returns:
            Dictionary with model results, hazard ratios, and statistics
        """
        cph = CoxPHFitter()
        
        # Prepare data
        model_data = data[[time_column, event_column] + covariates].copy()
        
        # Fit model
        cph.fit(model_data, duration_col=time_column, event_col=event_column)
        
        # Extract results
        results = {
            "method": "cox_proportional_hazards",
            "time_column": time_column,
            "event_column": event_column,
            "covariates": covariates,
            "timestamp": datetime.now().isoformat(),
            "concordance_index": float(cph.concordance_index_),
            "log_likelihood": float(cph.log_likelihood_),
            "aic": float(cph.AIC_),
            "coefficients": {},
            "hazard_ratios": {},
            "p_values": {},
            "confidence_intervals": {}
        }
        
        # Extract coefficient information
        summary = cph.summary
        for covariate in covariates:
            if covariate in summary.index:
                results["coefficients"][covariate] = float(summary.loc[covariate, "coef"])
                results["hazard_ratios"][covariate] = float(summary.loc[covariate, "exp(coef)"])
                results["p_values"][covariate] = float(summary.loc[covariate, "p"])
                results["confidence_intervals"][covariate] = {
                    "lower": float(summary.loc[covariate, "exp(coef) lower 95%"]),
                    "upper": float(summary.loc[covariate, "exp(coef) upper 95%"])
                }
        
        # Create plot
        fig, ax = plt.subplots(figsize=(10, 6))
        cph.plot(ax=ax)
        ax.set_title("Cox Proportional Hazards - Hazard Ratios")
        
        # Convert plot to base64
        buf = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        plot_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        
        results["plot"] = f"data:image/png;base64,{plot_base64}"
        
        return results
    
    @staticmethod
    def logrank_test_analysis(
        data: pd.DataFrame,
        time_column: str,
        event_column: str,
        group_column: str
    ) -> Dict[str, Any]:
        """
        Perform log-rank test for comparing survival curves between groups
        
        Args:
            data: DataFrame with survival data
            time_column: Column name for time to event
            event_column: Column name for event indicator
            group_column: Column name for group assignment
            
        Returns:
            Dictionary with test statistics and p-value
        """
        groups = data[group_column].unique()
        
        if len(groups) != 2:
            raise ValueError("Log-rank test requires exactly 2 groups")
        
        group1_data = data[data[group_column] == groups[0]]
        group2_data = data[data[group_column] == groups[1]]
        
        result = logrank_test(
            durations_A=group1_data[time_column],
            durations_B=group2_data[time_column],
            event_observed_A=group1_data[event_column],
            event_observed_B=group2_data[event_column]
        )
        
        return {
            "method": "logrank_test",
            "group1": str(groups[0]),
            "group2": str(groups[1]),
            "test_statistic": float(result.test_statistic),
            "p_value": float(result.p_value),
            "significant": result.p_value < 0.05,
            "timestamp": datetime.now().isoformat()
        }


class MultipleTestingCorrectionService:
    """Service for multiple testing correction methods"""
    
    @staticmethod
    def correct_pvalues(
        pvalues: List[float],
        method: str = "fdr_bh",
        alpha: float = 0.05
    ) -> Dict[str, Any]:
        """
        Apply multiple testing correction to p-values
        
        Args:
            pvalues: List of p-values
            method: Correction method ('bonferroni', 'fdr_bh', 'fdr_by')
            alpha: Significance level
            
        Returns:
            Dictionary with corrected p-values and rejection decisions
        """
        pvalues_array = np.array(pvalues)
        
        # Apply correction
        reject, pvals_corrected, alphacSidak, alphacBonf = multipletests(
            pvalues_array,
            alpha=alpha,
            method=method
        )
        
        return {
            "method": method,
            "alpha": alpha,
            "n_tests": len(pvalues),
            "original_pvalues": pvalues,
            "corrected_pvalues": pvals_corrected.tolist(),
            "rejected": reject.tolist(),
            "n_significant": int(reject.sum()),
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def permutation_test(
        group1: np.ndarray,
        group2: np.ndarray,
        n_permutations: int = 10000,
        statistic: str = "mean_diff"
    ) -> Dict[str, Any]:
        """
        Perform permutation-based hypothesis test
        
        Args:
            group1: Data for group 1
            group2: Data for group 2
            n_permutations: Number of permutations
            statistic: Test statistic ('mean_diff', 'median_diff')
            
        Returns:
            Dictionary with test results and p-value
        """
        # Calculate observed statistic
        if statistic == "mean_diff":
            observed_stat = np.mean(group1) - np.mean(group2)
        elif statistic == "median_diff":
            observed_stat = np.median(group1) - np.median(group2)
        else:
            raise ValueError(f"Unknown statistic: {statistic}")
        
        # Combine data
        combined = np.concatenate([group1, group2])
        n1 = len(group1)
        
        # Perform permutations
        perm_stats = []
        for _ in range(n_permutations):
            np.random.shuffle(combined)
            perm_group1 = combined[:n1]
            perm_group2 = combined[n1:]
            
            if statistic == "mean_diff":
                perm_stat = np.mean(perm_group1) - np.mean(perm_group2)
            else:
                perm_stat = np.median(perm_group1) - np.median(perm_group2)
            
            perm_stats.append(perm_stat)
        
        perm_stats = np.array(perm_stats)
        
        # Calculate p-value (two-tailed)
        p_value = np.mean(np.abs(perm_stats) >= np.abs(observed_stat))
        
        return {
            "method": "permutation_test",
            "statistic": statistic,
            "n_permutations": n_permutations,
            "observed_statistic": float(observed_stat),
            "p_value": float(p_value),
            "significant": p_value < 0.05,
            "timestamp": datetime.now().isoformat()
        }


class PowerAnalysisService:
    """Service for power analysis and sample size calculations"""
    
    @staticmethod
    def ttest_power_analysis(
        effect_size: float,
        alpha: float = 0.05,
        power: Optional[float] = None,
        n_samples: Optional[int] = None,
        alternative: str = "two-sided"
    ) -> Dict[str, Any]:
        """
        Perform power analysis for t-test
        
        Args:
            effect_size: Cohen's d effect size
            alpha: Significance level
            power: Desired statistical power (if calculating sample size)
            n_samples: Sample size per group (if calculating power)
            alternative: 'two-sided', 'larger', or 'smaller'
            
        Returns:
            Dictionary with power analysis results
        """
        analysis = TTestIndPower()
        
        if power is not None and n_samples is None:
            # Calculate required sample size
            n_samples = analysis.solve_power(
                effect_size=effect_size,
                alpha=alpha,
                power=power,
                alternative=alternative
            )
            calculated = "sample_size"
            result_value = int(np.ceil(n_samples))
        elif n_samples is not None and power is None:
            # Calculate achieved power
            power = analysis.solve_power(
                effect_size=effect_size,
                alpha=alpha,
                nobs1=n_samples,
                alternative=alternative
            )
            calculated = "power"
            result_value = float(power)
        else:
            raise ValueError("Specify either power or n_samples, not both")
        
        return {
            "test": "t_test",
            "effect_size": effect_size,
            "alpha": alpha,
            "alternative": alternative,
            "calculated": calculated,
            "result": result_value,
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def anova_power_analysis(
        effect_size: float,
        n_groups: int,
        alpha: float = 0.05,
        power: Optional[float] = None,
        n_samples: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Perform power analysis for ANOVA
        
        Args:
            effect_size: Cohen's f effect size
            n_groups: Number of groups
            alpha: Significance level
            power: Desired statistical power (if calculating sample size)
            n_samples: Sample size per group (if calculating power)
            
        Returns:
            Dictionary with power analysis results
        """
        analysis = FTestAnovaPower()
        
        if power is not None and n_samples is None:
            # Calculate required sample size
            n_samples = analysis.solve_power(
                effect_size=effect_size,
                alpha=alpha,
                power=power,
                k_groups=n_groups
            )
            calculated = "sample_size"
            result_value = int(np.ceil(n_samples))
        elif n_samples is not None and power is None:
            # Calculate achieved power
            power = analysis.solve_power(
                effect_size=effect_size,
                alpha=alpha,
                nobs=n_samples * n_groups,
                k_groups=n_groups
            )
            calculated = "power"
            result_value = float(power)
        else:
            raise ValueError("Specify either power or n_samples, not both")
        
        return {
            "test": "anova",
            "effect_size": effect_size,
            "n_groups": n_groups,
            "alpha": alpha,
            "calculated": calculated,
            "result": result_value,
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def calculate_effect_size(
        group1: np.ndarray,
        group2: np.ndarray,
        effect_type: str = "cohen_d"
    ) -> Dict[str, Any]:
        """
        Calculate effect size from data
        
        Args:
            group1: Data for group 1
            group2: Data for group 2
            effect_type: Type of effect size ('cohen_d', 'hedges_g')
            
        Returns:
            Dictionary with effect size
        """
        mean1, mean2 = np.mean(group1), np.mean(group2)
        std1, std2 = np.std(group1, ddof=1), np.std(group2, ddof=1)
        n1, n2 = len(group1), len(group2)
        
        # Pooled standard deviation
        pooled_std = np.sqrt(((n1 - 1) * std1**2 + (n2 - 1) * std2**2) / (n1 + n2 - 2))
        
        # Cohen's d
        cohen_d = (mean1 - mean2) / pooled_std
        
        if effect_type == "hedges_g":
            # Hedges' g correction for small samples
            correction = 1 - (3 / (4 * (n1 + n2) - 9))
            effect_size = cohen_d * correction
        else:
            effect_size = cohen_d
        
        # Interpret effect size
        abs_effect = abs(effect_size)
        if abs_effect < 0.2:
            interpretation = "negligible"
        elif abs_effect < 0.5:
            interpretation = "small"
        elif abs_effect < 0.8:
            interpretation = "medium"
        else:
            interpretation = "large"
        
        return {
            "effect_type": effect_type,
            "effect_size": float(effect_size),
            "interpretation": interpretation,
            "group1_mean": float(mean1),
            "group2_mean": float(mean2),
            "group1_std": float(std1),
            "group2_std": float(std2),
            "timestamp": datetime.now().isoformat()
        }



class TimeSeriesAnalysisService:
    """Service for time-series analysis"""
    
    @staticmethod
    def arima_analysis(
        data: pd.Series,
        order: Tuple[int, int, int] = (1, 1, 1),
        forecast_steps: int = 10
    ) -> Dict[str, Any]:
        """
        Perform ARIMA time-series analysis
        
        Args:
            data: Time series data
            order: ARIMA order (p, d, q)
            forecast_steps: Number of steps to forecast
            
        Returns:
            Dictionary with model results and forecast
        """
        # Fit ARIMA model
        model = ARIMA(data, order=order)
        fitted_model = model.fit()
        
        # Make forecast
        forecast = fitted_model.forecast(steps=forecast_steps)
        forecast_ci = fitted_model.get_forecast(steps=forecast_steps).conf_int()
        
        # Create plot
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot historical data
        ax.plot(data.index, data.values, label='Historical', color='blue')
        
        # Plot forecast
        forecast_index = pd.date_range(
            start=data.index[-1],
            periods=forecast_steps + 1,
            freq=pd.infer_freq(data.index)
        )[1:]
        
        ax.plot(forecast_index, forecast, label='Forecast', color='red', linestyle='--')
        ax.fill_between(
            forecast_index,
            forecast_ci.iloc[:, 0],
            forecast_ci.iloc[:, 1],
            alpha=0.3,
            color='red'
        )
        
        ax.set_xlabel('Time')
        ax.set_ylabel('Value')
        ax.set_title(f'ARIMA{order} Time Series Forecast')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Convert plot to base64
        buf = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        plot_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        
        return {
            "method": "arima",
            "order": order,
            "aic": float(fitted_model.aic),
            "bic": float(fitted_model.bic),
            "forecast": forecast.tolist(),
            "forecast_confidence_interval": {
                "lower": forecast_ci.iloc[:, 0].tolist(),
                "upper": forecast_ci.iloc[:, 1].tolist()
            },
            "model_summary": str(fitted_model.summary()),
            "plot": f"data:image/png;base64,{plot_base64}",
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def prophet_analysis(
        data: pd.DataFrame,
        forecast_periods: int = 30,
        seasonality_mode: str = 'additive',
        yearly_seasonality: bool = True,
        weekly_seasonality: bool = True,
        daily_seasonality: bool = False
    ) -> Dict[str, Any]:
        """
        Perform Prophet time-series forecasting
        
        Args:
            data: DataFrame with 'ds' (date) and 'y' (value) columns
            forecast_periods: Number of periods to forecast
            seasonality_mode: 'additive' or 'multiplicative'
            yearly_seasonality: Include yearly seasonality
            weekly_seasonality: Include weekly seasonality
            daily_seasonality: Include daily seasonality
            
        Returns:
            Dictionary with forecast and components
        """
        # Initialize Prophet model
        model = Prophet(
            seasonality_mode=seasonality_mode,
            yearly_seasonality=yearly_seasonality,
            weekly_seasonality=weekly_seasonality,
            daily_seasonality=daily_seasonality
        )
        
        # Fit model
        model.fit(data)
        
        # Create future dataframe
        future = model.make_future_dataframe(periods=forecast_periods)
        
        # Make forecast
        forecast = model.predict(future)
        
        # Create plots
        fig1 = model.plot(forecast)
        fig1.suptitle('Prophet Forecast')
        
        # Convert forecast plot to base64
        buf1 = io.BytesIO()
        fig1.tight_layout()
        fig1.savefig(buf1, format='png', dpi=100, bbox_inches='tight')
        buf1.seek(0)
        plot1_base64 = base64.b64encode(buf1.read()).decode('utf-8')
        plt.close(fig1)
        
        # Create components plot
        fig2 = model.plot_components(forecast)
        fig2.suptitle('Forecast Components')
        
        # Convert components plot to base64
        buf2 = io.BytesIO()
        fig2.tight_layout()
        fig2.savefig(buf2, format='png', dpi=100, bbox_inches='tight')
        buf2.seek(0)
        plot2_base64 = base64.b64encode(buf2.read()).decode('utf-8')
        plt.close(fig2)
        
        # Extract forecast for future periods only
        future_forecast = forecast.tail(forecast_periods)
        
        return {
            "method": "prophet",
            "seasonality_mode": seasonality_mode,
            "forecast_periods": forecast_periods,
            "forecast": {
                "dates": future_forecast['ds'].dt.strftime('%Y-%m-%d').tolist(),
                "yhat": future_forecast['yhat'].tolist(),
                "yhat_lower": future_forecast['yhat_lower'].tolist(),
                "yhat_upper": future_forecast['yhat_upper'].tolist()
            },
            "plot_forecast": f"data:image/png;base64,{plot1_base64}",
            "plot_components": f"data:image/png;base64,{plot2_base64}",
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def lstm_forecast(
        data: np.ndarray,
        lookback: int = 10,
        forecast_steps: int = 10,
        epochs: int = 50,
        batch_size: int = 32
    ) -> Dict[str, Any]:
        """
        Perform LSTM-based time-series forecasting
        
        Args:
            data: Time series data as numpy array
            lookback: Number of past time steps to use
            forecast_steps: Number of steps to forecast
            epochs: Training epochs
            batch_size: Batch size for training
            
        Returns:
            Dictionary with forecast and model performance
        """
        try:
            import torch
            import torch.nn as nn
            from torch.utils.data import DataLoader, TensorDataset
        except ImportError:
            return {
                "error": "PyTorch not available for LSTM forecasting",
                "method": "lstm",
                "timestamp": datetime.now().isoformat()
            }
        
        # Normalize data
        data_mean = np.mean(data)
        data_std = np.std(data)
        data_normalized = (data - data_mean) / data_std
        
        # Create sequences
        X, y = [], []
        for i in range(len(data_normalized) - lookback):
            X.append(data_normalized[i:i+lookback])
            y.append(data_normalized[i+lookback])
        
        X = np.array(X)
        y = np.array(y)
        
        # Split into train and test
        train_size = int(0.8 * len(X))
        X_train, X_test = X[:train_size], X[train_size:]
        y_train, y_test = y[:train_size], y[train_size:]
        
        # Convert to PyTorch tensors
        X_train_tensor = torch.FloatTensor(X_train).unsqueeze(-1)
        y_train_tensor = torch.FloatTensor(y_train).unsqueeze(-1)
        X_test_tensor = torch.FloatTensor(X_test).unsqueeze(-1)
        y_test_tensor = torch.FloatTensor(y_test).unsqueeze(-1)
        
        # Define LSTM model
        class LSTMModel(nn.Module):
            def __init__(self, input_size=1, hidden_size=50, num_layers=2):
                super(LSTMModel, self).__init__()
                self.hidden_size = hidden_size
                self.num_layers = num_layers
                self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
                self.fc = nn.Linear(hidden_size, 1)
            
            def forward(self, x):
                h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size)
                c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size)
                out, _ = self.lstm(x, (h0, c0))
                out = self.fc(out[:, -1, :])
                return out
        
        # Initialize model
        model = LSTMModel()
        criterion = nn.MSELoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
        
        # Train model
        train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        
        model.train()
        for epoch in range(epochs):
            for batch_X, batch_y in train_loader:
                optimizer.zero_grad()
                outputs = model(batch_X)
                loss = criterion(outputs, batch_y)
                loss.backward()
                optimizer.step()
        
        # Evaluate on test set
        model.eval()
        with torch.no_grad():
            test_predictions = model(X_test_tensor).numpy()
        
        # Calculate test MSE
        test_mse = np.mean((test_predictions - y_test.reshape(-1, 1))**2)
        
        # Make future forecast
        last_sequence = data_normalized[-lookback:]
        forecast_normalized = []
        
        model.eval()
        with torch.no_grad():
            for _ in range(forecast_steps):
                input_seq = torch.FloatTensor(last_sequence).unsqueeze(0).unsqueeze(-1)
                pred = model(input_seq).item()
                forecast_normalized.append(pred)
                last_sequence = np.append(last_sequence[1:], pred)
        
        # Denormalize forecast
        forecast = np.array(forecast_normalized) * data_std + data_mean
        
        # Create plot
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot historical data
        ax.plot(range(len(data)), data, label='Historical', color='blue')
        
        # Plot forecast
        forecast_index = range(len(data), len(data) + forecast_steps)
        ax.plot(forecast_index, forecast, label='LSTM Forecast', color='red', linestyle='--')
        
        ax.set_xlabel('Time')
        ax.set_ylabel('Value')
        ax.set_title('LSTM Time Series Forecast')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Convert plot to base64
        buf = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        plot_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        
        return {
            "method": "lstm",
            "lookback": lookback,
            "forecast_steps": forecast_steps,
            "epochs": epochs,
            "test_mse": float(test_mse),
            "forecast": forecast.tolist(),
            "plot": f"data:image/png;base64,{plot_base64}",
            "timestamp": datetime.now().isoformat()
        }



class MultiOmicsIntegrationService:
    """Service for multi-omics data integration"""
    
    @staticmethod
    def mofa_analysis(
        omics_data: Dict[str, pd.DataFrame],
        n_factors: int = 10,
        convergence_mode: str = "fast"
    ) -> Dict[str, Any]:
        """
        Perform MOFA+ (Multi-Omics Factor Analysis) integration
        
        Note: This is a simplified implementation using PCA-based approach
        For full MOFA+, use the mofapy2 package
        
        Args:
            omics_data: Dictionary of omics layer names to DataFrames
            n_factors: Number of latent factors
            convergence_mode: Convergence mode
            
        Returns:
            Dictionary with factor loadings and scores
        """
        # Combine all omics layers
        layer_names = list(omics_data.keys())
        combined_data = pd.concat([omics_data[layer] for layer in layer_names], axis=1)
        
        # Handle missing values
        combined_data = combined_data.fillna(combined_data.mean())
        
        # Standardize data
        from sklearn.preprocessing import StandardScaler
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(combined_data)
        
        # Perform factor analysis
        fa = FactorAnalysis(n_components=n_factors, random_state=42)
        factors = fa.fit_transform(scaled_data)
        
        # Get loadings for each omics layer
        loadings = fa.components_.T
        
        # Split loadings by omics layer
        layer_loadings = {}
        start_idx = 0
        for layer in layer_names:
            n_features = omics_data[layer].shape[1]
            layer_loadings[layer] = loadings[start_idx:start_idx+n_features, :]
            start_idx += n_features
        
        # Calculate variance explained
        variance_explained = np.var(factors, axis=0) / np.sum(np.var(factors, axis=0))
        
        # Create visualization
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        # Plot factor scores
        axes[0].scatter(factors[:, 0], factors[:, 1], alpha=0.6)
        axes[0].set_xlabel(f'Factor 1 ({variance_explained[0]:.1%} var)')
        axes[0].set_ylabel(f'Factor 2 ({variance_explained[1]:.1%} var)')
        axes[0].set_title('Sample Factor Scores')
        axes[0].grid(True, alpha=0.3)
        
        # Plot variance explained
        axes[1].bar(range(1, n_factors + 1), variance_explained)
        axes[1].set_xlabel('Factor')
        axes[1].set_ylabel('Variance Explained')
        axes[1].set_title('Variance Explained by Each Factor')
        axes[1].grid(True, alpha=0.3)
        
        # Convert plot to base64
        buf = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        plot_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        
        return {
            "method": "mofa",
            "n_factors": n_factors,
            "omics_layers": layer_names,
            "variance_explained": variance_explained.tolist(),
            "factor_scores": factors.tolist(),
            "layer_loadings": {
                layer: loadings.tolist() 
                for layer, loadings in layer_loadings.items()
            },
            "plot": f"data:image/png;base64,{plot_base64}",
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def diablo_analysis(
        omics_data: Dict[str, pd.DataFrame],
        outcome: np.ndarray,
        n_components: int = 2
    ) -> Dict[str, Any]:
        """
        Perform DIABLO (Data Integration Analysis for Biomarker discovery using Latent cOmponents)
        
        Note: This is a simplified implementation using PLS-based approach
        For full DIABLO, use the mixOmics R package
        
        Args:
            omics_data: Dictionary of omics layer names to DataFrames
            outcome: Outcome variable for supervised integration
            n_components: Number of components
            
        Returns:
            Dictionary with component scores and loadings
        """
        layer_names = list(omics_data.keys())
        
        # For simplicity, perform PLS on concatenated data
        combined_data = pd.concat([omics_data[layer] for layer in layer_names], axis=1)
        combined_data = combined_data.fillna(combined_data.mean())
        
        # Standardize
        from sklearn.preprocessing import StandardScaler
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(combined_data)
        
        # Perform PLS
        from sklearn.cross_decomposition import PLSRegression
        pls = PLSRegression(n_components=n_components)
        
        # Reshape outcome if needed
        if outcome.ndim == 1:
            outcome = outcome.reshape(-1, 1)
        
        pls.fit(scaled_data, outcome)
        
        # Get component scores
        scores = pls.transform(scaled_data)
        
        # Get loadings
        loadings = pls.x_loadings_
        
        # Split loadings by omics layer
        layer_loadings = {}
        start_idx = 0
        for layer in layer_names:
            n_features = omics_data[layer].shape[1]
            layer_loadings[layer] = loadings[start_idx:start_idx+n_features, :]
            start_idx += n_features
        
        # Create visualization
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        # Plot component scores colored by outcome
        scatter = axes[0].scatter(
            scores[:, 0], 
            scores[:, 1] if n_components > 1 else np.zeros_like(scores[:, 0]),
            c=outcome.ravel(),
            cmap='viridis',
            alpha=0.6
        )
        axes[0].set_xlabel('Component 1')
        axes[0].set_ylabel('Component 2' if n_components > 1 else 'Zero')
        axes[0].set_title('DIABLO Component Scores')
        axes[0].grid(True, alpha=0.3)
        plt.colorbar(scatter, ax=axes[0], label='Outcome')
        
        # Plot loadings heatmap for first component
        all_loadings = []
        layer_labels = []
        for layer in layer_names:
            all_loadings.extend(layer_loadings[layer][:, 0].tolist())
            layer_labels.extend([layer] * len(layer_loadings[layer]))
        
        # Show top 20 features
        top_indices = np.argsort(np.abs(all_loadings))[-20:]
        top_loadings = [all_loadings[i] for i in top_indices]
        top_labels = [f"{layer_labels[i]}_{i}" for i in top_indices]
        
        axes[1].barh(range(len(top_loadings)), top_loadings)
        axes[1].set_yticks(range(len(top_loadings)))
        axes[1].set_yticklabels(top_labels, fontsize=8)
        axes[1].set_xlabel('Loading')
        axes[1].set_title('Top 20 Feature Loadings (Component 1)')
        axes[1].grid(True, alpha=0.3, axis='x')
        
        # Convert plot to base64
        buf = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        plot_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        
        return {
            "method": "diablo",
            "n_components": n_components,
            "omics_layers": layer_names,
            "component_scores": scores.tolist(),
            "layer_loadings": {
                layer: loadings.tolist() 
                for layer, loadings in layer_loadings.items()
            },
            "plot": f"data:image/png;base64,{plot_base64}",
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def create_integration_visualization(
        omics_data: Dict[str, pd.DataFrame],
        method: str = "pca"
    ) -> Dict[str, Any]:
        """
        Create visualization for multi-omics integration
        
        Args:
            omics_data: Dictionary of omics layer names to DataFrames
            method: Dimensionality reduction method ('pca', 'umap')
            
        Returns:
            Dictionary with visualization
        """
        layer_names = list(omics_data.keys())
        combined_data = pd.concat([omics_data[layer] for layer in layer_names], axis=1)
        combined_data = combined_data.fillna(combined_data.mean())
        
        # Standardize
        from sklearn.preprocessing import StandardScaler
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(combined_data)
        
        # Apply dimensionality reduction
        if method == "pca":
            from sklearn.decomposition import PCA
            reducer = PCA(n_components=2)
            reduced_data = reducer.fit_transform(scaled_data)
            var_explained = reducer.explained_variance_ratio_
            xlabel = f'PC1 ({var_explained[0]:.1%} var)'
            ylabel = f'PC2 ({var_explained[1]:.1%} var)'
        elif method == "umap":
            from umap import UMAP
            reducer = UMAP(n_components=2, random_state=42)
            reduced_data = reducer.fit_transform(scaled_data)
            xlabel = 'UMAP 1'
            ylabel = 'UMAP 2'
        else:
            raise ValueError(f"Unknown method: {method}")
        
        # Create plot
        fig, ax = plt.subplots(figsize=(10, 8))
        scatter = ax.scatter(
            reduced_data[:, 0],
            reduced_data[:, 1],
            alpha=0.6,
            s=50
        )
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(f'Multi-Omics Integration ({method.upper()})')
        ax.grid(True, alpha=0.3)
        
        # Convert plot to base64
        buf = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        plot_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        
        return {
            "method": method,
            "omics_layers": layer_names,
            "reduced_data": reduced_data.tolist(),
            "plot": f"data:image/png;base64,{plot_base64}",
            "timestamp": datetime.now().isoformat()
        }



class BayesianInferenceService:
    """Service for Bayesian inference using PyMC"""
    
    @staticmethod
    def bayesian_linear_regression(
        X: np.ndarray,
        y: np.ndarray,
        n_samples: int = 2000,
        n_chains: int = 2
    ) -> Dict[str, Any]:
        """
        Perform Bayesian linear regression
        
        Args:
            X: Feature matrix
            y: Target variable
            n_samples: Number of MCMC samples
            n_chains: Number of MCMC chains
            
        Returns:
            Dictionary with posterior distributions and diagnostics
        """
        with pm.Model() as model:
            # Priors
            alpha = pm.Normal('alpha', mu=0, sigma=10)
            beta = pm.Normal('beta', mu=0, sigma=10, shape=X.shape[1])
            sigma = pm.HalfNormal('sigma', sigma=1)
            
            # Linear model
            mu = alpha + pm.math.dot(X, beta)
            
            # Likelihood
            y_obs = pm.Normal('y_obs', mu=mu, sigma=sigma, observed=y)
            
            # MCMC sampling
            trace = pm.sample(
                n_samples,
                chains=n_chains,
                return_inferencedata=True,
                progressbar=False
            )
        
        # Extract posterior summaries
        summary = az.summary(trace)
        
        # Create diagnostic plots
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # Trace plot for intercept
        az.plot_trace(trace, var_names=['alpha'], axes=axes[0, :])
        
        # Posterior plot for first coefficient
        az.plot_posterior(trace, var_names=['beta'], coords={'beta_dim_0': 0}, ax=axes[1, 0])
        
        # Forest plot
        az.plot_forest(trace, var_names=['beta'], ax=axes[1, 1])
        
        plt.tight_layout()
        
        # Convert plot to base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        plot_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        
        # Extract posterior means
        posterior_means = {
            'alpha': float(trace.posterior['alpha'].mean().values),
            'beta': trace.posterior['beta'].mean(dim=['chain', 'draw']).values.tolist(),
            'sigma': float(trace.posterior['sigma'].mean().values)
        }
        
        # Calculate R-hat for convergence diagnostics
        rhat = az.rhat(trace)
        
        return {
            "method": "bayesian_linear_regression",
            "n_samples": n_samples,
            "n_chains": n_chains,
            "posterior_means": posterior_means,
            "summary": summary.to_dict(),
            "rhat": {var: float(rhat[var].values) for var in rhat.data_vars},
            "plot": f"data:image/png;base64,{plot_base64}",
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def bayesian_t_test(
        group1: np.ndarray,
        group2: np.ndarray,
        n_samples: int = 2000
    ) -> Dict[str, Any]:
        """
        Perform Bayesian t-test
        
        Args:
            group1: Data for group 1
            group2: Data for group 2
            n_samples: Number of MCMC samples
            
        Returns:
            Dictionary with posterior distribution of effect size
        """
        with pm.Model() as model:
            # Priors for group means
            mu1 = pm.Normal('mu1', mu=0, sigma=10)
            mu2 = pm.Normal('mu2', mu=0, sigma=10)
            
            # Priors for group standard deviations
            sigma1 = pm.HalfNormal('sigma1', sigma=10)
            sigma2 = pm.HalfNormal('sigma2', sigma=10)
            
            # Likelihoods
            y1 = pm.Normal('y1', mu=mu1, sigma=sigma1, observed=group1)
            y2 = pm.Normal('y2', mu=mu2, sigma=sigma2, observed=group2)
            
            # Effect size (Cohen's d)
            pooled_std = pm.math.sqrt((sigma1**2 + sigma2**2) / 2)
            effect_size = pm.Deterministic('effect_size', (mu1 - mu2) / pooled_std)
            
            # MCMC sampling
            trace = pm.sample(
                n_samples,
                return_inferencedata=True,
                progressbar=False
            )
        
        # Extract posterior for effect size
        effect_size_posterior = trace.posterior['effect_size'].values.flatten()
        
        # Calculate probability that effect size > 0
        prob_positive = np.mean(effect_size_posterior > 0)
        
        # Calculate credible interval
        hdi = az.hdi(trace, var_names=['effect_size'], hdi_prob=0.95)
        
        # Create plot
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        # Posterior distribution of effect size
        axes[0].hist(effect_size_posterior, bins=50, density=True, alpha=0.7, edgecolor='black')
        axes[0].axvline(0, color='red', linestyle='--', label='No effect')
        axes[0].axvline(np.mean(effect_size_posterior), color='green', linestyle='-', label='Mean')
        axes[0].set_xlabel('Effect Size (Cohen\'s d)')
        axes[0].set_ylabel('Density')
        axes[0].set_title('Posterior Distribution of Effect Size')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # Trace plot
        az.plot_trace(trace, var_names=['effect_size'], axes=axes[1:])
        
        plt.tight_layout()
        
        # Convert plot to base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        plot_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        
        return {
            "method": "bayesian_t_test",
            "n_samples": n_samples,
            "effect_size_mean": float(np.mean(effect_size_posterior)),
            "effect_size_std": float(np.std(effect_size_posterior)),
            "credible_interval_95": {
                "lower": float(hdi['effect_size'].values[0]),
                "upper": float(hdi['effect_size'].values[1])
            },
            "prob_positive_effect": float(prob_positive),
            "plot": f"data:image/png;base64,{plot_base64}",
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def variational_inference(
        X: np.ndarray,
        y: np.ndarray,
        n_iterations: int = 50000
    ) -> Dict[str, Any]:
        """
        Perform variational inference for Bayesian linear regression
        
        Args:
            X: Feature matrix
            y: Target variable
            n_iterations: Number of optimization iterations
            
        Returns:
            Dictionary with approximate posterior
        """
        with pm.Model() as model:
            # Priors
            alpha = pm.Normal('alpha', mu=0, sigma=10)
            beta = pm.Normal('beta', mu=0, sigma=10, shape=X.shape[1])
            sigma = pm.HalfNormal('sigma', sigma=1)
            
            # Linear model
            mu = alpha + pm.math.dot(X, beta)
            
            # Likelihood
            y_obs = pm.Normal('y_obs', mu=mu, sigma=sigma, observed=y)
            
            # Variational inference
            approx = pm.fit(
                n=n_iterations,
                method='advi',
                progressbar=False
            )
        
        # Sample from approximate posterior
        trace = approx.sample(2000)
        
        # Extract means
        posterior_means = {
            'alpha': float(np.mean(trace['alpha'])),
            'beta': np.mean(trace['beta'], axis=0).tolist(),
            'sigma': float(np.mean(trace['sigma']))
        }
        
        # Create plot
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        # ELBO convergence
        axes[0].plot(approx.hist)
        axes[0].set_xlabel('Iteration')
        axes[0].set_ylabel('ELBO')
        axes[0].set_title('Variational Inference Convergence')
        axes[0].grid(True, alpha=0.3)
        
        # Posterior distributions
        axes[1].hist(trace['alpha'], bins=50, alpha=0.7, label='Intercept', density=True)
        axes[1].set_xlabel('Value')
        axes[1].set_ylabel('Density')
        axes[1].set_title('Approximate Posterior - Intercept')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Convert plot to base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        plot_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        
        return {
            "method": "variational_inference",
            "n_iterations": n_iterations,
            "posterior_means": posterior_means,
            "final_elbo": float(approx.hist[-1]),
            "plot": f"data:image/png;base64,{plot_base64}",
            "timestamp": datetime.now().isoformat()
        }
