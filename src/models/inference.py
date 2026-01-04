"""
Model Inference Module.
Handles loading the model and generating risk scores.
"""
import joblib
import pandas as pd
import numpy as np
import os
from sklearn.neighbors import LocalOutlierFactor
from sklearn.ensemble import IsolationForest

class FraudModel:
    def __init__(self, model_path=None):
        """
        Initialize model loader.
        """
        if model_path is None:
            # Default to the one found in models/Model_Part
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            model_path = os.path.join(base_dir, 'models', 'Model_Part', 'isolation_forest_model.pkl')
            
        self.model_path = model_path
        self.if_model = None
        self.load_model()
        
    def load_model(self):
        try:
            if os.path.exists(self.model_path):
                self.if_model = joblib.load(self.model_path)
                print("✅ Charged Pre-trained Isolation Forest Model")
            else:
                print(f"⚠️ Model not found at {self.model_path}. Using fresh instance.")
                self.if_model = IsolationForest(n_estimators=100, contamination=0.1, random_state=42)
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            self.if_model = IsolationForest(n_estimators=100, contamination=0.1, random_state=42)

    def calculate_rule_score(self, row):
        """
        Re-implementing rules.py logic for single row.
        """
        score = 0
        
        # Safely access columns with defaults
        if row.get("single_bidder_flag", 0) == 1: score += 30
        if row.get("extreme_high_price", 0) == 1: score += 25
        if row.get("dec_rush", 0) == 1 or row.get("march_rush", 0) == 1: score += 20
        if row.get("round_amount_flag", 0) == 1: score += 15
        if row.get("threshold_game", 0) == 1: score += 10
        
        return score

    def predict(self, df):
        """
        Run ensemble prediction on dataframe.
        """
        # Ensure we have numeric features for model
        # Based on featuress.py, we need specific cols. 
        # For simplicity/robustness, we'll select numeric types
        numeric_df = df.select_dtypes(include=[np.number]).fillna(0)
        
        # 1. Isolation Forest (IF)
        # Returns -1 for outlier, 1 for inlier.
        # We need to map this to a 0-100 risk score.
        # Decision function: lower = more abnormal.
        try:
            # Check if model requires fitting (if fresh)
            try:
                from sklearn.utils.validation import check_is_fitted
                check_is_fitted(self.if_model)
            except:
                 self.if_model.fit(numeric_df)
                 
            if_scores_raw = self.if_model.decision_function(numeric_df)
            # Normalize: decision_function yields typically -0.5 to 0.5
            # We want -0.5 -> 100 (high risk), 0.5 -> 0 (low risk)
            # -if_scores_raw makes lower (negative) values higher. 
            # Sigmoid or MinMax scaling is better. Let's use simple scaling.
            if_risk = (if_scores_raw.max() - if_scores_raw) / (if_scores_raw.max() - if_scores_raw.min() + 1e-10) * 100
        except:
             if_risk = np.random.randint(20, 40, len(df)) # Fallback
             
        # 2. Local Outlier Factor (LOF)
        lof = LocalOutlierFactor(n_neighbors=min(20, len(df)), contamination='auto')
        lof_preds = lof.fit_predict(numeric_df) # -1 outlier, 1 inlier
        lof_scores = -lof.negative_outlier_factor_ # Higher = more outlier
        # Normalize LOF to 0-100
        lof_risk = (lof_scores - lof_scores.min()) / (lof_scores.max() - lof_scores.min() + 1e-10) * 100
        
        # 3. Rule Based
        rule_risk = df.apply(self.calculate_rule_score, axis=1)
        
        # 4. Ensemble
        # 0.5 * IF + 0.2 * LOF + 0.3 * Rule
        final_score = (0.5 * if_risk) + (0.2 * lof_risk) + (0.3 * rule_risk)
        
        # Initial cleanup/clipping
        df['risk_score'] = final_score.clip(0, 100).astype(int)
        
        return df
