"""
Example script showing how to use the combined feature engineering pipeline.
"""

import pandas as pd
import numpy as np
from combined_feature_engineering import engineer_all_features, get_all_feature_names

# Load your data
print("Loading data...")
contracts_df = pd.read_csv('india_contracts.csv')
vendors_df = pd.read_csv('india_vendors.csv')
payments_df = pd.read_csv('india_payments.csv')
market_prices_df = pd.read_csv('india_market_prices.csv')  # Optional

# Engineer all features (both award and payment)
print("\nEngineering features...")
contracts_enhanced, payments_enhanced = engineer_all_features(
    contracts_df,
    vendors_df,
    payments_df,
    market_prices_df,  # Optional - can be None
    verbose=True
)

# Get available feature names organized by category
feature_dict = get_all_feature_names(contracts_enhanced)

print("\n" + "=" * 80)
print("AVAILABLE FEATURES BY CATEGORY")
print("=" * 80)
for category, features in feature_dict.items():
    print(f"\n{category.upper()}:")
    print(f"  Total: {len(features)} features")
    print(f"  Examples: {', '.join(features[:5])}...")

# Select features for ML model
all_features = []
for features in feature_dict.values():
    all_features.extend(features)

# Remove duplicates and ensure they exist
all_features = list(set(all_features))
all_features = [f for f in all_features if f in contracts_enhanced.columns]

print(f"\n\nTotal unique features available: {len(all_features)}")

# Prepare data for modeling
# Handle NaN values: fill numeric columns with 0, categorical columns with mode
X = contracts_enhanced[all_features].copy()

# Separate categorical and numeric columns
categorical_cols = X.select_dtypes(include=['category', 'object']).columns
numeric_cols = X.select_dtypes(include=[np.number]).columns

# Fill numeric columns with 0
X[numeric_cols] = X[numeric_cols].fillna(0)

# Fill categorical columns with their mode (most frequent value)
for col in categorical_cols:
    if X[col].isna().any():
        mode_value = X[col].mode()[0] if len(X[col].mode()) > 0 else 'Unknown'
        X[col] = X[col].fillna(mode_value)

print(f"\nFeature matrix shape: {X.shape}")
print(f"Features: {X.columns.tolist()[:10]}...")  # Show first 10

# If you have labels, you can train a model:
# y = contracts_enhanced['is_fraud']  # Your labels
# from sklearn.ensemble import RandomForestClassifier
# model = RandomForestClassifier(n_estimators=100, random_state=42)
# model.fit(X, y)

# Save enhanced data
print("\nSaving enhanced data...")
contracts_enhanced.to_csv('contracts_with_all_features.csv', index=False)
payments_enhanced.to_csv('payments_enhanced.csv', index=False)

print("\nDone! Enhanced data saved.")

