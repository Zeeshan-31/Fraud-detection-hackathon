"""
Analyze data quality and determine usable rows for EDA and ML
"""

import pandas as pd
import numpy as np

print("=" * 80)
print("DATA QUALITY ANALYSIS")
print("=" * 80)

df = pd.read_csv('contracts_cleaned.csv')
print(f"\nTotal rows: {len(df):,}")
print(f"Total columns: {len(df.columns)}")

# ============================================================================
# 1. MISSING VALUES ANALYSIS
# ============================================================================
print("\n" + "=" * 80)
print("1. MISSING VALUES ANALYSIS")
print("=" * 80)

missing = df.isnull().sum()
missing_pct = (missing / len(df)) * 100

# Columns with any missing values
cols_with_missing = missing[missing > 0]
print(f"\nColumns with missing values: {len(cols_with_missing)}")

if len(cols_with_missing) > 0:
    print("\nTop 20 columns with most missing values:")
    top_missing = cols_with_missing.sort_values(ascending=False).head(20)
    for col, count in top_missing.items():
        pct = missing_pct[col]
        print(f"  {col}: {count:,} ({pct:.2f}%)")

# Columns with >50% missing (likely unusable)
high_missing = missing[missing > len(df) * 0.5]
print(f"\nColumns with >50% missing (likely unusable): {len(high_missing)}")
if len(high_missing) > 0:
    for col in high_missing.index:
        print(f"  - {col}: {missing_pct[col]:.2f}% missing")

# ============================================================================
# 2. TARGET VARIABLE ANALYSIS
# ============================================================================
print("\n" + "=" * 80)
print("2. TARGET VARIABLE ANALYSIS")
print("=" * 80)

if 'is_fraud' in df.columns:
    fraud_dist = df['is_fraud'].value_counts()
    print(f"\nis_fraud distribution:")
    print(fraud_dist)
    print(f"\nFraud rate: {df['is_fraud'].mean()*100:.2f}%")
    print(f"Legitimate contracts: {fraud_dist.get(0, 0):,}")
    print(f"Fraudulent contracts: {fraud_dist.get(1, 0):,}")
    
    # Rows with valid target
    rows_with_target = df['is_fraud'].notna().sum()
    print(f"\nRows with valid target variable: {rows_with_target:,} ({rows_with_target/len(df)*100:.2f}%)")
else:
    print("\n[WARN] No 'is_fraud' column found - this is unsupervised learning scenario")

# ============================================================================
# 3. KEY FEATURES COMPLETENESS
# ============================================================================
print("\n" + "=" * 80)
print("3. KEY FEATURES COMPLETENESS")
print("=" * 80)

key_features = {
    'Core Identifiers': ['contract_id', 'vendor_id'],
    'Target/Outcome': ['is_fraud'],
    'Main Amount': ['amount_inr'],
    'Risk Scores': ['contract_award_risk_score', 'payment_risk_score', 'overall_risk_score'],
    'Critical Flags': ['single_source_flag', 'rapid_payment_flag', 'suspicious_pricing'],
}

for category, features in key_features.items():
    print(f"\n{category}:")
    for feat in features:
        if feat in df.columns:
            missing_count = df[feat].isnull().sum()
            missing_pct_val = missing_count / len(df) * 100
            status = "[OK]" if missing_pct_val < 5 else "[WARN]" if missing_pct_val < 50 else "[BAD]"
            print(f"  {status} {feat}: {missing_count:,} missing ({missing_pct_val:.2f}%)")
        else:
            print(f"  [MISSING] {feat}: Column not found")

# ============================================================================
# 4. USABLE ROWS CALCULATION
# ============================================================================
print("\n" + "=" * 80)
print("4. USABLE ROWS FOR EDA & ML")
print("=" * 80)

# Define critical columns that must be present
critical_cols = ['contract_id', 'amount_inr', 'vendor_id']

# For supervised learning (if is_fraud exists)
if 'is_fraud' in df.columns:
    critical_cols.append('is_fraud')
    
    # Rows usable for supervised ML (have target + critical features)
    usable_supervised = df[critical_cols].notna().all(axis=1).sum()
    print(f"\nRows usable for SUPERVISED ML (has target + critical features):")
    print(f"  {usable_supervised:,} rows ({usable_supervised/len(df)*100:.2f}%)")
    
    # Check fraud distribution in usable rows
    if usable_supervised > 0:
        usable_df = df[df[critical_cols].notna().all(axis=1)]
        fraud_in_usable = usable_df['is_fraud'].value_counts()
        print(f"\n  Fraud distribution in usable rows:")
        print(f"    Legitimate: {fraud_in_usable.get(0, 0):,}")
        print(f"    Fraudulent: {fraud_in_usable.get(1, 0):,}")
        if len(fraud_in_usable) > 0:
            print(f"    Fraud rate: {fraud_in_usable.get(1, 0)/usable_supervised*100:.2f}%")

# For unsupervised learning / EDA (no target needed)
critical_cols_eda = ['contract_id', 'amount_inr']
usable_eda = df[critical_cols_eda].notna().all(axis=1).sum()
print(f"\nRows usable for EDA / UNSUPERVISED ML (has critical features):")
print(f"  {usable_eda:,} rows ({usable_eda/len(df)*100:.2f}%)")

# Rows with risk scores (most important features)
risk_score_cols = ['contract_award_risk_score', 'payment_risk_score', 'overall_risk_score']
existing_risk_cols = [col for col in risk_score_cols if col in df.columns]
if existing_risk_cols:
    rows_with_risk_scores = df[existing_risk_cols].notna().all(axis=1).sum()
    print(f"\nRows with ALL risk scores:")
    print(f"  {rows_with_risk_scores:,} rows ({rows_with_risk_scores/len(df)*100:.2f}%)")
    
    # Rows with at least one risk score
    rows_with_any_risk = df[existing_risk_cols].notna().any(axis=1).sum()
    print(f"\nRows with AT LEAST ONE risk score:")
    print(f"  {rows_with_any_risk:,} rows ({rows_with_any_risk/len(df)*100:.2f}%)")

# ============================================================================
# 5. RECOMMENDATIONS
# ============================================================================
print("\n" + "=" * 80)
print("5. RECOMMENDATIONS")
print("=" * 80)

print("\nFor EDA:")
print(f"  [OK] Use all {usable_eda:,} rows (have contract_id and amount_inr)")
print(f"  [OK] Focus on {rows_with_any_risk:,} rows with risk scores for fraud analysis")

if 'is_fraud' in df.columns:
    print("\nFor SUPERVISED ML:")
    print(f"  [OK] Use {usable_supervised:,} rows with complete target + critical features")
    
    if usable_supervised > 0:
        usable_df = df[df[critical_cols].notna().all(axis=1)]
        fraud_count = usable_df['is_fraud'].sum()
        legit_count = len(usable_df) - fraud_count
        
        if fraud_count > 0 and legit_count > 0:
            imbalance_ratio = max(fraud_count, legit_count) / min(fraud_count, legit_count)
            print(f"  [WARN] Class imbalance ratio: {imbalance_ratio:.2f}:1")
            if imbalance_ratio > 10:
                print(f"     -> Consider: SMOTE, class weights, or stratified sampling")
        
        print(f"  -> Minimum recommended sample: {max(100, fraud_count * 10):,} rows")

print("\nFor FEATURE ENGINEERING:")
print(f"  [OK] {len(df.columns)} total features available")
print(f"  -> Consider removing columns with >50% missing values")
print(f"  -> Use imputation for columns with <50% missing")

print("\n" + "=" * 80)

