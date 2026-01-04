import pandas as pd
import joblib
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline



df = pd.read_csv(r"C:\Users\mishr\Downloads\data_with_features.csv")

numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns.tolist()

exclude_cols = [
    "fraud_risk_score",
    "final_risk_score",
    "rule_risk_score"
]

feature_cols = [col for col in numeric_cols if col not in exclude_cols]

print("Using features:", feature_cols)