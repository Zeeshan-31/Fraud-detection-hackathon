import pandas as pd
import numpy as np
import joblib
import os
import streamlit as st
from sklearn.impute import SimpleImputer

# Define the features expected by the model
MODEL_FEATURES = [
    'contract_amount', 'bidder_count', 'duration_days',
    'single_bidder_flag', 'low_competition_score', 'zero_bidders_flag',
    'bidder_to_value_ratio', 'amount_zscore', 'price_per_day_zscore',
    'short_duration_flag', 'weekend_publication_flag', 'year_end_rush_flag',
    'q4_flag', 'limited_tender_flag', 'offline_payment_flag',
    'lump_sum_flag', 'dept_tender_frequency', 'dept_single_bidder_rate',
    'red_flag_count', 'competition_health_score'
]

def standardize_columns(df):
    """
    Rename columns to standard names used by the model.
    Handles common synonyms.
    """
    df = df.copy()
    
    # Map of Standard Name -> List of Synonyms
    # Case insensitive matching will be used
    column_map = {
        'contract_id': ['tender_id', 'id', 'ref_no', 'contract_no', 'tender_no'],
        'contract_amount': ['amount', 'value', 'tender_value', 'estimated_cost', 'price', 'total_amount', 'tender_value_amount'],
        'bidder_count': ['bidders_count', 'bidders', 'no_of_bidders', 'tender_numberoftenderers', 'participation_count'],
        'dept_name': ['department', 'buyer', 'buyer_name', 'organization', 'agency', 'procuring_entity'],
        'pub_date': ['date', 'publish_date', 'tender_date', 'tender_datepublished', 'announcement_date', 'start_date'],
        'proc_method': ['method', 'procurement_method', 'tender_procurementmethod', 'type_of_bidding'],
        'contract_type': ['type', 'tender_type', 'tender_contracttype', 'category'],
        'payment_mode': ['payment', 'mode', 'payment_type'],
        'duration_days': ['duration', 'period', 'days', 'tender_period_durationindays']
    }
    
    # Create a lower-case map of existing columns
    existing_cols_lower = {col.lower(): col for col in df.columns}
    
    renamed_cols = {}
    
    for standard, synonyms in column_map.items():
        # If standard name already exists, skip
        if standard in df.columns:
            continue
            
        # Check synonyms
        for syn in synonyms:
            if syn.lower() in existing_cols_lower:
                original_name = existing_cols_lower[syn.lower()]
                renamed_cols[original_name] = standard
                break # Found a match, move to next standard column
    
    if renamed_cols:
        df = df.rename(columns=renamed_cols)
        
    return df

def validate_data_sufficiency(df):
    """
    Check if the data has enough information for meaningful analysis.
    
    Returns:
        is_valid (bool): Can we proceed?
        message (str): Warning or Error message
        status (str): 'success', 'warning', 'error'
    """
    # Standardize first to check for standard columns
    df_std = standardize_columns(df)
    
    missing_critical = []
    missing_important = []
    
    # Critical: We really can't do much without these
    if 'contract_amount' not in df_std.columns: missing_critical.append("Amount/Value")
    
    # Important: Analysis is weak without these
    if 'pub_date' not in df_std.columns: missing_important.append("Date")
    if 'bidder_count' not in df_std.columns: missing_important.append("Bidder Count")
    if 'dept_name' not in df_std.columns: missing_important.append("Department Name")
    
    if missing_critical:
        return False, f"❌ Critical columns missing: {', '.join(missing_critical)}. Analysis cannot proceed.", "error"
        
    if missing_important:
        return True, f"⚠️ Missing columns: {', '.join(missing_important)}. Analysis will be less accurate (defaults used).", "warning"
        
    return True, "✅ Data looks good!", "success"

def engineer_features_for_model(df):
    """
    Engineer features required for the ML model from raw input data.
    Handles missing columns by creating defaults.
    """
    # First, standardize column names
    df = standardize_columns(df)
    
    df = df.copy()
    
    # --- 1. Basic Column Standardization ---
    # Ensure required base columns exist
    if 'contract_amount' not in df.columns: df['contract_amount'] = 0
    if 'bidder_count' not in df.columns: df['bidder_count'] = 0
    if 'dept_name' not in df.columns: df['dept_name'] = 'Unknown'
    if 'proc_method' not in df.columns: df['proc_method'] = 'Unknown'
    if 'contract_type' not in df.columns: df['contract_type'] = 'Unknown'
    if 'payment_mode' not in df.columns: df['payment_mode'] = 'Unknown'
    if 'duration_days' not in df.columns: df['duration_days'] = 30 # Default assumption
    
    # --- 1.5 Force Numeric Types (Fix for "unsupported operand type" error) ---
    # Convert columns to numeric, coercing errors (like "N/A", "$100") to NaN then 0
    df['contract_amount'] = pd.to_numeric(df['contract_amount'], errors='coerce').fillna(0)
    df['bidder_count'] = pd.to_numeric(df['bidder_count'], errors='coerce').fillna(0)
    df['duration_days'] = pd.to_numeric(df['duration_days'], errors='coerce').fillna(30)
    
    # Handle missing pub_date (Common error source)
    if 'pub_date' not in df.columns:
        # Try to find a date column
        date_cols = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
        if date_cols:
            df['pub_date'] = df[date_cols[0]]
        else:
            df['pub_date'] = pd.NaT # Will result in NaT after to_datetime

    # --- 2. Feature Engineering ---
    
    # Competition
    df['single_bidder_flag'] = (df['bidder_count'] == 1).astype(int)
    df['low_competition_score'] = (df['bidder_count'] < 3).astype(int)
    df['zero_bidders_flag'] = (df['bidder_count'].isna() | (df['bidder_count'] == 0)).astype(int)
    
    # Bidder to Value Ratio
    # Avoid division by zero
    amount_q75 = df['contract_amount'].quantile(0.75)
    if amount_q75 == 0 or pd.isna(amount_q75): amount_q75 = 1
    
    df['bidder_to_value_ratio'] = df['bidder_count'] / (df['contract_amount'] / amount_q75)
    df['bidder_to_value_ratio'] = df['bidder_to_value_ratio'].fillna(0)
    
    # Pricing Anomalies (Z-Scores)
    # If dataset is too small (like sample), z-scores might be meaningless (NaN or 0)
    if len(df) > 1:
        df['amount_zscore'] = df.groupby('dept_name')['contract_amount'].transform(
            lambda x: np.abs((x - x.mean()) / (x.std() + 1e-8))
        ).fillna(0)
    else:
        df['amount_zscore'] = 0
        
    df['price_per_day'] = df['contract_amount'] / (df['duration_days'] + 1)
    
    if len(df) > 1:
        df['price_per_day_zscore'] = df.groupby('dept_name')['price_per_day'].transform(
            lambda x: np.abs((x - x.mean()) / (x.std() + 1e-8))
        ).fillna(0)
    else:
        df['price_per_day_zscore'] = 0

    # Timeline
    df['pub_date'] = pd.to_datetime(df['pub_date'], errors='coerce')
    df['short_duration_flag'] = (df['duration_days'] < 7).astype(int)
    
    df['weekend_publication_flag'] = df['pub_date'].apply(
        lambda x: 1 if pd.notna(x) and x.dayofweek >= 5 else 0
    )
    
    df['year_end_rush_flag'] = df['pub_date'].apply(
        lambda x: 1 if pd.notna(x) and x.month == 3 and x.day >= 15 else 0
    )
    
    df['pub_month'] = df['pub_date'].dt.month
    df['q4_flag'] = df['pub_month'].apply(lambda x: 1 if x in [1, 2, 3] else 0) # Jan-Mar is Q4 in India
    
    # Procurement Method
    df['limited_tender_flag'] = (df['proc_method'].astype(str).str.contains('Limited', case=False, na=False)).astype(int)
    df['offline_payment_flag'] = (df['payment_mode'] == 'Offline').astype(int)
    df['lump_sum_flag'] = (df['contract_type'].astype(str).str.contains('Lump', case=False, na=False)).astype(int)
    
    # Department Stats
    # For small samples, these stats are just based on the sample itself
    dept_counts = df['dept_name'].value_counts()
    df['dept_tender_frequency'] = df['dept_name'].map(dept_counts).fillna(0)
    
    # Single bidder rate per dept
    dept_single_rate = df.groupby('dept_name')['single_bidder_flag'].mean()
    df['dept_single_bidder_rate'] = df['dept_name'].map(dept_single_rate).fillna(0)
    
    # Red Flags Count (Simplified)
    flag_cols = [c for c in df.columns if c.endswith('_flag')]
    df['red_flag_count'] = df[flag_cols].sum(axis=1)
    
    # Competition Health Score
    df['competition_health_score'] = (
        (100 - (df['single_bidder_flag'] * 50)) +
        (df['bidder_count'] * 5) +
        ((1 - df['limited_tender_flag']) * 15) -
        (df['offline_payment_flag'] * 10)
    ).clip(0, 100)
    
    return df

def run_ml_prediction(df):
    """
    Run the pre-trained Isolation Forest model on the dataframe.
    
    Args:
        df: Input dataframe
        
    Returns:
        DataFrame with 'ml_risk_score', 'ml_anomaly_label', 'ml_anomaly_score' added
    """
    model_path = "models/active/isolation_forest_v1.pkl"
    
    if not os.path.exists(model_path):
        st.warning("⚠️ ML Model not found. Please train the model first.")
        return df, False
        
    try:
        # Load model artifacts
        artifacts = joblib.load(model_path)
        model = artifacts['model']
        scaler = artifacts['scaler']
        imputer = artifacts['imputer']
        
        # Engineer features
        df_featured = engineer_features_for_model(df)
        
        # Select features
        X = df_featured[MODEL_FEATURES].copy()
        
        # Impute and Scale
        # Note: We use the SAVED imputer/scaler to ensure consistency with training data
        # However, if the new data has different columns or order, we need to be careful.
        # We ensured X has exactly MODEL_FEATURES in correct order.
        
        X_imputed = imputer.transform(X)
        X_scaled = scaler.transform(X_imputed)
        
        # Predict
        anomaly_labels = model.predict(X_scaled)
        anomaly_scores = model.decision_function(X_scaled)
        
        # Add to original dataframe
        df['ml_anomaly_label'] = anomaly_labels
        df['ml_anomaly_score'] = anomaly_scores
        df['ml_risk_score'] = -anomaly_scores # Higher = More Anomalous
        
        return df, True
        
    except Exception as e:
        st.error(f"Error running ML prediction: {str(e)}")
        return df, False
