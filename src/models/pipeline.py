"""
Data Pipeline for Fraud Detection Model.
Handles column alignment and feature engineering.
"""
import pandas as pd
import numpy as np
import sys
import os

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_processing.feature_engineering import engineer_fraud_features

class FraudDetectionPipeline:
    def __init__(self):
        self.column_mapping = {
            'tender value': 'contract_amount',
            'estimated cost': 'contract_amount',
            'amount': 'contract_amount',
            'department name': 'dept_name',
            'department': 'dept_name',
            'organisation': 'dept_name',
            'buyer_name': 'dept_name',
            'tender id': 'contract_id',
            'tender_id': 'contract_id',
            'id': 'contract_id',
            'date': 'pub_date',
            'published date': 'pub_date',
            'bidders': 'bidder_count',
            'bidders_count': 'bidder_count',
            'no of bidders': 'bidder_count'
            # Add more mappings as needed
        }
        
    def align_columns(self, df):
        """
        Align variable user column names to standard internal names.
        """
        # Lowercase columns for matching
        df.columns = [c.strip() for c in df.columns]
        
        # Create a copy to avoid SettingWithCopy warnings
        df_aligned = df.copy()
        
        # Renaissance mapping
        renames = {}
        for col in df_aligned.columns:
            clean_col = col.lower().replace('_', ' ')
            if clean_col in self.column_mapping:
                renames[col] = self.column_mapping[clean_col]
            else:
                # Try partial match (e.g. "Total Amount" -> "contract_amount")
                for key, val in self.column_mapping.items():
                    if key in clean_col:
                        renames[col] = val
                        break
                        
        if renames:
            df_aligned = df_aligned.rename(columns=renames)
            
        # Ensure required columns exist (fill with defaults if missing)
        required_cols = {
            'contract_id': 'UNKNOWN',
            'dept_name': 'Unknown Dept',
            'contract_amount': 0,
            'bidder_count': 1, # Be careful with default risk
            'pub_date': pd.Timestamp.now()
        }
        
        for col, default in required_cols.items():
            if col not in df_aligned.columns:
                df_aligned[col] = default
                
        return df_aligned

    def prepare_features(self, df):
        """
        Run the full feature engineering pipeline.
        """
        # 1. Align columns
        df_aligned = self.align_columns(df)
        
        # 2. Engineer features (calls existing logic)
        try:
            df_features = engineer_fraud_features(df_aligned)
            
            # 3. Impute missing values for model compatibility
            # Fill NaNs in feature columns that might be produced
            df_features = df_features.fillna(0)
            
            return df_features
        except Exception as e:
            print(f"Feature engineering failed: {e}")
            # Fallback: return aligned (might fail model but prevents crash)
            return df_aligned
