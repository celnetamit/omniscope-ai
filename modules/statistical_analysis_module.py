"""
Statistical Analysis Module for OmniScope AI
Provides API endpoints for advanced statistical methods
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np
import io

from backend_db.statistical_analysis import (
    SurvivalAnalysisService,
    TimeSeriesAnalysisService,
    MultiOmicsIntegrationService,
    BayesianInferenceService,
    MultipleTestingCorrectionService,
    PowerAnalysisService
)

router = APIRouter(prefix="/api/statistics", tags=["Statistical Analysis"])


# ============================================================================
# Request/Response Models
# ============================================================================

class SurvivalAnalysisRequest(BaseModel):
    """Request model for survival analysis"""
    time_column: str = Field(..., description="Column name for time to event")
    event_column: str = Field(..., description="Column name for event indicator (1=event, 0=censored)")
    group_column: Optional[str] = Field(None, description="Optional column for group comparison")
    method: str = Field("kaplan_meier", description="Analysis method: 'kaplan_meier' or 'cox'")
    covariates: Optional[List[str]] = Field(None, description="Covariates for Cox regression")


class TimeSeriesRequest(BaseModel):
    """Request model for time-series analysis"""
    method: str = Field(..., description="Method: 'arima', 'prophet', or 'lstm'")
    forecast_steps: int = Field(10, description="Number of steps to forecast")
    # ARIMA specific
    arima_order: Optional[List[int]] = Field([1, 1, 1], description="ARIMA order (p, d, q)")
    # Prophet specific
    seasonality_mode: Optional[str] = Field("additive", description="Prophet seasonality mode")
    # LSTM specific
    lookback: Optional[int] = Field(10, description="LSTM lookback window")
    epochs: Optional[int] = Field(50, description="LSTM training epochs")


class MultiOmicsRequest(BaseModel):
    """Request model for multi-omics integration"""
    method: str = Field(..., description="Method: 'mofa' or 'diablo'")
    n_factors: Optional[int] = Field(10, description="Number of factors/components")
    outcome_column: Optional[str] = Field(None, description="Outcome column for DIABLO")


class BayesianInferenceRequest(BaseModel):
    """Request model for Bayesian inference"""
    method: str = Field(..., description="Method: 'linear_regression', 't_test', or 'variational'")
    target_column: str = Field(..., description="Target variable column")
    feature_columns: Optional[List[str]] = Field(None, description="Feature columns for regression")
    group_column: Optional[str] = Field(None, description="Group column for t-test")
    n_samples: Optional[int] = Field(2000, description="Number of MCMC samples")


class MultipleTestingRequest(BaseModel):
    """Request model for multiple testing correction"""
    pvalues: List[float] = Field(..., description="List of p-values to correct")
    method: str = Field("fdr_bh", description="Correction method: 'bonferroni', 'fdr_bh', 'fdr_by'")
    alpha: float = Field(0.05, description="Significance level")


class PermutationTestRequest(BaseModel):
    """Request model for permutation test"""
    group1_column: str = Field(..., description="Column name for group 1")
    group2_column: str = Field(..., description="Column name for group 2")
    n_permutations: int = Field(10000, description="Number of permutations")
    statistic: str = Field("mean_diff", description="Test statistic: 'mean_diff' or 'median_diff'")


class PowerAnalysisRequest(BaseModel):
    """Request model for power analysis"""
    test: str = Field(..., description="Test type: 't_test' or 'anova'")
    effect_size: float = Field(..., description="Effect size (Cohen's d or f)")
    alpha: float = Field(0.05, description="Significance level")
    power: Optional[float] = Field(None, description="Desired power (if calculating sample size)")
    n_samples: Optional[int] = Field(None, description="Sample size (if calculating power)")
    n_groups: Optional[int] = Field(2, description="Number of groups for ANOVA")
    alternative: Optional[str] = Field("two-sided", description="Alternative hypothesis")


class EffectSizeRequest(BaseModel):
    """Request model for effect size calculation"""
    group1_column: str = Field(..., description="Column name for group 1")
    group2_column: str = Field(..., description="Column name for group 2")
    effect_type: str = Field("cohen_d", description="Effect type: 'cohen_d' or 'hedges_g'")


# ============================================================================
# Survival Analysis Endpoints
# ============================================================================

@router.post("/survival-analysis")
async def perform_survival_analysis(
    file: UploadFile = File(...),
    request: SurvivalAnalysisRequest = None
):
    """
    Perform survival analysis (Kaplan-Meier or Cox regression)
    
    Upload a CSV file with survival data and specify analysis parameters.
    """
    try:
        # Read uploaded file
        contents = await file.read()
        data = pd.read_csv(io.BytesIO(contents))
        
        # Validate columns
        required_cols = [request.time_column, request.event_column]
        if request.group_column:
            required_cols.append(request.group_column)
        if request.covariates:
            required_cols.extend(request.covariates)
        
        missing_cols = [col for col in required_cols if col not in data.columns]
        if missing_cols:
            raise HTTPException(
                status_code=400,
                detail=f"Missing columns: {missing_cols}"
            )
        
        # Perform analysis
        if request.method == "kaplan_meier":
            result = SurvivalAnalysisService.kaplan_meier_analysis(
                data=data,
                time_column=request.time_column,
                event_column=request.event_column,
                group_column=request.group_column
            )
        elif request.method == "cox":
            if not request.covariates:
                raise HTTPException(
                    status_code=400,
                    detail="Covariates required for Cox regression"
                )
            result = SurvivalAnalysisService.cox_proportional_hazards(
                data=data,
                time_column=request.time_column,
                event_column=request.event_column,
                covariates=request.covariates
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown method: {request.method}"
            )
        
        return {
            "status": "success",
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/logrank-test")
async def perform_logrank_test(
    file: UploadFile = File(...),
    time_column: str = "time",
    event_column: str = "event",
    group_column: str = "group"
):
    """
    Perform log-rank test for comparing survival curves between two groups
    """
    try:
        contents = await file.read()
        data = pd.read_csv(io.BytesIO(contents))
        
        result = SurvivalAnalysisService.logrank_test_analysis(
            data=data,
            time_column=time_column,
            event_column=event_column,
            group_column=group_column
        )
        
        return {
            "status": "success",
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Time-Series Analysis Endpoints
# ============================================================================

@router.post("/time-series")
async def perform_time_series_analysis(
    file: UploadFile = File(...),
    request: TimeSeriesRequest = None
):
    """
    Perform time-series analysis and forecasting
    
    Supports ARIMA, Prophet, and LSTM methods.
    """
    try:
        contents = await file.read()
        data = pd.read_csv(io.BytesIO(contents))
        
        if request.method == "arima":
            # Assume first column is time series data
            series = pd.Series(data.iloc[:, 0].values)
            result = TimeSeriesAnalysisService.arima_analysis(
                data=series,
                order=tuple(request.arima_order),
                forecast_steps=request.forecast_steps
            )
        elif request.method == "prophet":
            # Prophet requires 'ds' and 'y' columns
            if 'ds' not in data.columns or 'y' not in data.columns:
                raise HTTPException(
                    status_code=400,
                    detail="Prophet requires 'ds' (date) and 'y' (value) columns"
                )
            result = TimeSeriesAnalysisService.prophet_analysis(
                data=data,
                forecast_periods=request.forecast_steps,
                seasonality_mode=request.seasonality_mode
            )
        elif request.method == "lstm":
            # Assume first column is time series data
            series_data = data.iloc[:, 0].values
            result = TimeSeriesAnalysisService.lstm_forecast(
                data=series_data,
                lookback=request.lookback,
                forecast_steps=request.forecast_steps,
                epochs=request.epochs
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown method: {request.method}"
            )
        
        return {
            "status": "success",
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Multi-Omics Integration Endpoints
# ============================================================================

@router.post("/multi-omics-integration")
async def perform_multi_omics_integration(
    files: List[UploadFile] = File(...),
    request: MultiOmicsRequest = None
):
    """
    Perform multi-omics data integration
    
    Upload multiple CSV files (one per omics layer) for integration analysis.
    """
    try:
        # Read all omics layers
        omics_data = {}
        for i, file in enumerate(files):
            contents = await file.read()
            layer_name = file.filename.replace('.csv', '')
            omics_data[layer_name] = pd.read_csv(io.BytesIO(contents), index_col=0)
        
        if len(omics_data) < 2:
            raise HTTPException(
                status_code=400,
                detail="At least 2 omics layers required for integration"
            )
        
        # Perform integration
        if request.method == "mofa":
            result = MultiOmicsIntegrationService.mofa_analysis(
                omics_data=omics_data,
                n_factors=request.n_factors
            )
        elif request.method == "diablo":
            # For DIABLO, we need an outcome variable
            # Assume it's in the first file's first column
            first_layer = list(omics_data.values())[0]
            if request.outcome_column and request.outcome_column in first_layer.columns:
                outcome = first_layer[request.outcome_column].values
            else:
                # Use first column as outcome
                outcome = first_layer.iloc[:, 0].values
            
            result = MultiOmicsIntegrationService.diablo_analysis(
                omics_data=omics_data,
                outcome=outcome,
                n_components=request.n_factors
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown method: {request.method}"
            )
        
        return {
            "status": "success",
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Bayesian Inference Endpoints
# ============================================================================

@router.post("/bayesian-inference")
async def perform_bayesian_inference(
    file: UploadFile = File(...),
    request: BayesianInferenceRequest = None
):
    """
    Perform Bayesian inference
    
    Supports Bayesian linear regression, t-test, and variational inference.
    """
    try:
        contents = await file.read()
        data = pd.read_csv(io.BytesIO(contents))
        
        if request.method == "linear_regression":
            if not request.feature_columns:
                raise HTTPException(
                    status_code=400,
                    detail="Feature columns required for linear regression"
                )
            
            X = data[request.feature_columns].values
            y = data[request.target_column].values
            
            result = BayesianInferenceService.bayesian_linear_regression(
                X=X,
                y=y,
                n_samples=request.n_samples
            )
        elif request.method == "t_test":
            if not request.group_column:
                raise HTTPException(
                    status_code=400,
                    detail="Group column required for t-test"
                )
            
            groups = data[request.group_column].unique()
            if len(groups) != 2:
                raise HTTPException(
                    status_code=400,
                    detail="Exactly 2 groups required for t-test"
                )
            
            group1 = data[data[request.group_column] == groups[0]][request.target_column].values
            group2 = data[data[request.group_column] == groups[1]][request.target_column].values
            
            result = BayesianInferenceService.bayesian_t_test(
                group1=group1,
                group2=group2,
                n_samples=request.n_samples
            )
        elif request.method == "variational":
            if not request.feature_columns:
                raise HTTPException(
                    status_code=400,
                    detail="Feature columns required for variational inference"
                )
            
            X = data[request.feature_columns].values
            y = data[request.target_column].values
            
            result = BayesianInferenceService.variational_inference(
                X=X,
                y=y
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown method: {request.method}"
            )
        
        return {
            "status": "success",
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Multiple Testing Correction Endpoints
# ============================================================================

@router.post("/multiple-testing-correction")
async def perform_multiple_testing_correction(request: MultipleTestingRequest):
    """
    Apply multiple testing correction to p-values
    
    Supports Bonferroni, FDR (Benjamini-Hochberg), and FDR (Benjamini-Yekutieli) methods.
    """
    try:
        result = MultipleTestingCorrectionService.correct_pvalues(
            pvalues=request.pvalues,
            method=request.method,
            alpha=request.alpha
        )
        
        return {
            "status": "success",
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/permutation-test")
async def perform_permutation_test(
    file: UploadFile = File(...),
    request: PermutationTestRequest = None
):
    """
    Perform permutation-based hypothesis test
    """
    try:
        contents = await file.read()
        data = pd.read_csv(io.BytesIO(contents))
        
        group1 = data[request.group1_column].values
        group2 = data[request.group2_column].values
        
        result = MultipleTestingCorrectionService.permutation_test(
            group1=group1,
            group2=group2,
            n_permutations=request.n_permutations,
            statistic=request.statistic
        )
        
        return {
            "status": "success",
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Power Analysis Endpoints
# ============================================================================

@router.post("/power-analysis")
async def perform_power_analysis(request: PowerAnalysisRequest):
    """
    Perform power analysis and sample size calculation
    
    Calculate either required sample size (given power) or achieved power (given sample size).
    """
    try:
        if request.test == "t_test":
            result = PowerAnalysisService.ttest_power_analysis(
                effect_size=request.effect_size,
                alpha=request.alpha,
                power=request.power,
                n_samples=request.n_samples,
                alternative=request.alternative
            )
        elif request.test == "anova":
            result = PowerAnalysisService.anova_power_analysis(
                effect_size=request.effect_size,
                n_groups=request.n_groups,
                alpha=request.alpha,
                power=request.power,
                n_samples=request.n_samples
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown test: {request.test}"
            )
        
        return {
            "status": "success",
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/effect-size")
async def calculate_effect_size(
    file: UploadFile = File(...),
    request: EffectSizeRequest = None
):
    """
    Calculate effect size from data
    
    Supports Cohen's d and Hedges' g.
    """
    try:
        contents = await file.read()
        data = pd.read_csv(io.BytesIO(contents))
        
        group1 = data[request.group1_column].values
        group2 = data[request.group2_column].values
        
        result = PowerAnalysisService.calculate_effect_size(
            group1=group1,
            group2=group2,
            effect_type=request.effect_type
        )
        
        return {
            "status": "success",
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Health Check
# ============================================================================

@router.get("/health")
async def health_check():
    """Health check endpoint for statistical analysis module"""
    return {
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
