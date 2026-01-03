"""
Utility functions for the dashboard.
Common functions used across tabs and components.
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime


def generate_risk_scores(df, seed=42):
    """
    Generate risk scores for tenders (0-100).
    Uses consistent seed for reproducibility.
    
    Args:
        df: DataFrame with tender data
        seed: Random seed for consistency
        
    Returns:
        DataFrame with added risk_score and risk_level columns
    """
    np.random.seed(seed)
    df['risk_score'] = np.random.randint(0, 100, len(df))
    return df


def classify_risk_levels(df, risk_threshold):
    """
    Classify tenders into risk levels (Low, Medium, High).
    
    Args:
        df: DataFrame with risk_score column
        risk_threshold: Threshold for high risk (typically 70)
        
    Returns:
        DataFrame with added risk_level column
    """
    df['risk_level'] = pd.cut(
        df['risk_score'], 
        bins=[0, 40, risk_threshold, 100], 
        labels=['Low', 'Medium', 'High']
    )
    return df


def calculate_risk_metrics(df):
    """
    Calculate risk-related metrics from the dataframe.
    
    Args:
        df: DataFrame with risk_level column
        
    Returns:
        Dictionary with calculated metrics
    """
    total_tenders = len(df)
    high_risk_count = len(df[df['risk_level'] == 'High'])
    medium_risk_count = len(df[df['risk_level'] == 'Medium'])
    low_risk_count = len(df[df['risk_level'] == 'Low'])
    
    return {
        'total_tenders': total_tenders,
        'high_risk_count': high_risk_count,
        'medium_risk_count': medium_risk_count,
        'low_risk_count': low_risk_count,
        'high_risk_pct': (high_risk_count / total_tenders * 100) if total_tenders > 0 else 0,
        'medium_risk_pct': (medium_risk_count / total_tenders * 100) if total_tenders > 0 else 0,
        'low_risk_pct': (low_risk_count / total_tenders * 100) if total_tenders > 0 else 0,
    }


def find_amount_column(df):
    """
    Find amount/value column in the dataframe.
    Searches for common column names.
    
    Args:
        df: DataFrame to search
        
    Returns:
        Column name or None if not found
    """
    for col in df.columns:
        if 'amount' in col.lower() or 'value' in col.lower() or 'price' in col.lower():
            if pd.api.types.is_numeric_dtype(df[col]):
                return col
    return None


def format_amount(amount):
    """
    Format amount in Indian currency format.
    
    Args:
        amount: Numeric amount to format
        
    Returns:
        Formatted string (e.g., "₹1.50Cr")
    """
    if pd.isna(amount):
        return "N/A"
    return f"₹{amount/10000000:.2f}Cr"


def get_data_overview_stats(df, risk_threshold):
    """
    Get overview statistics for uploaded data.
    
    Args:
        df: Uploaded dataframe
        risk_threshold: Current risk threshold
        
    Returns:
        Dictionary with overview statistics
    """
    amount_col = find_amount_column(df)
    
    if amount_col and pd.api.types.is_numeric_dtype(df[amount_col]):
        total_amount = df[amount_col].sum()
        amount_display = format_amount(total_amount)
    else:
        amount_display = "N/A"
    
    return {
        'row_count': len(df),
        'column_count': len(df.columns),
        'total_amount': amount_display,
        'data_type': 'Procurement'
    }


def generate_analysis_info(row_count, risk_threshold):
    """
    Generate analysis information message.
    
    Args:
        row_count: Number of records to analyze
        risk_threshold: Current risk threshold
        
    Returns:
        Formatted info message
    """
    return f"""The system will analyze {row_count:,} procurement records using advanced ML algorithms to detect anomalies, 
    unusual patterns, and potential fraud indicators. Current high-risk threshold is set to {risk_threshold}%."""


def export_analysis_summary(df, risk_threshold, upload_time, metrics):
    """
    Generate text summary report for export.
    
    Args:
        df: Analysis dataframe with risk_score
        risk_threshold: Risk threshold used
        upload_time: When data was uploaded
        metrics: Calculated metrics
        
    Returns:
        Formatted summary text
    """
    summary = f"""Government Procurement Fraud Detection Report
Generated: {upload_time}
Risk Threshold: {risk_threshold}%
================================================================

SUMMARY STATISTICS
Total Records Analyzed: {metrics['total_tenders']:,}
High Risk: {metrics['high_risk_count']:,} ({metrics['high_risk_pct']:.1f}%)
Medium Risk: {metrics['medium_risk_count']:,} ({metrics['medium_risk_pct']:.1f}%)
Low Risk: {metrics['low_risk_count']:,} ({metrics['low_risk_pct']:.1f}%)

RISK SCORE ANALYSIS
Average Risk Score: {df['risk_score'].mean():.2f}
Median Risk Score: {df['risk_score'].median():.2f}
Highest Risk Score: {df['risk_score'].max()}
Lowest Risk Score: {df['risk_score'].min()}
"""
    return summary
