"""
Analyze which columns are usable for EDA and ML modeling
"""

import pandas as pd
import numpy as np

print("=" * 80)
print("COLUMN USABILITY ANALYSIS FOR EDA & ML")
print("=" * 80)

df = pd.read_csv('contracts_cleaned.csv')
print(f"\nTotal columns: {len(df.columns)}")
print(f"Total rows: {len(df):,}")

# ============================================================================
# 1. COLUMN CATEGORIZATION
# ============================================================================
print("\n" + "=" * 80)
print("1. COLUMN CATEGORIZATION BY TYPE")
print("=" * 80)

# Identify column types
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
bool_cols = df.select_dtypes(include=['bool']).columns.tolist()

print(f"\nNumeric columns: {len(numeric_cols)}")
print(f"Categorical columns: {len(categorical_cols)}")
print(f"Boolean columns: {len(bool_cols)}")

# ============================================================================
# 2. COLUMNS TO EXCLUDE FROM ML MODELING
# ============================================================================
print("\n" + "=" * 80)
print("2. COLUMNS TO EXCLUDE FROM ML MODELING")
print("=" * 80)

# Columns that should NOT be used as features (identifiers, targets, etc.)
exclude_from_ml = {
    'Identifiers': ['contract_id', 'tender_number', 'vendor_id', 'gst_number'],
    'Target Variable': ['is_fraud', 'fraud_reason'],
    'Dates (use derived features instead)': ['publication_date', 'award_date', 'registration_date', 'completion_date'],
    'Text/Address (too many unique values)': ['vendor_name_y', 'address', 'city', 'state', 'pincode'],
    'Derived Categorical (use numeric version)': ['overall_risk_level'],  # Use overall_risk_score instead
}

exclude_list = []
for category, cols in exclude_from_ml.items():
    existing_cols = [c for c in cols if c in df.columns]
    if existing_cols:
        exclude_list.extend(existing_cols)
        print(f"\n{category}:")
        for col in existing_cols:
            print(f"  - {col}")

print(f"\nTotal columns to exclude: {len(exclude_list)}")

# ============================================================================
# 3. USABLE FEATURE COLUMNS
# ============================================================================
print("\n" + "=" * 80)
print("3. USABLE FEATURE COLUMNS FOR ML MODELING")
print("=" * 80)

# All columns except excluded ones
usable_features = [col for col in df.columns if col not in exclude_list]
print(f"\nTotal usable feature columns: {len(usable_features)}")

# Categorize usable features
feature_categories = {
    'Core Contract Features': [
        'amount_inr', 'ministry', 'category', 'procedure_type', 'num_bids',
        'advertisement_days', 'contract_duration_days', 'officer_id',
        'payment_terms', 'performance_guarantee_pct'
    ],
    'Vendor Characteristics': [
        'business_type', 'employees', 'blacklisted'
    ],
    'Pricing Anomaly Features': [
        'price_deviation_pct', 'price_zscore', 'suspicious_pricing',
        'market_price_deviation_pct', 'above_market_price', 'near_threshold',
        'is_round_number', 'benford_deviation'
    ],
    'Competition Features': [
        'single_source_flag', 'non_competitive_procedure', 'low_competition',
        'competition_score', 'high_value_single_bid', 'high_value_non_competitive'
    ],
    'Timing Anomaly Features': [
        'weekend_award', 'month_end_award', 'fy_end_award',
        'short_advertisement', 'long_advertisement',
        'publication_to_award_days', 'rapid_award', 'delayed_award'
    ],
    'Vendor Risk Features': [
        'small_employee_count', 'vendor_age_years', 'new_vendor',
        'new_vendor_large_contract', 'vendor_total_contracts', 'vendor_total_value',
        'vendor_category_market_share', 'high_vendor_concentration', 'dominant_vendor',
        'vendor_win_rate', 'suspiciously_high_win_rate', 'shell_company_address',
        'cross_state_contract'
    ],
    'Officer Pattern Features': [
        'officer_total_approvals', 'officer_single_source_rate',
        'suspicious_officer_pattern'
    ],
    'Contract Characteristics': [
        'unrealistic_short_duration', 'excessive_duration',
        'high_value_no_guarantee', 'high_risk_low_guarantee'
    ],
    'Payment Anomaly Features': [
        'days_to_first_payment', 'rapid_payment_flag', 'delayed_payment_flag',
        'num_payments', 'avg_payment_interval_days', 'irregular_payment_frequency',
        'has_duplicate_payments', 'excessive_round_payments', 'has_weekend_payments',
        'total_paid', 'payment_variance_pct', 'overpayment_flag', 'underpayment_flag',
        'large_advance_no_guarantee'
    ],
    'Composite Risk Scores': [
        'contract_award_risk_score', 'payment_risk_score', 'overall_risk_score'
    ]
}

print("\nUsable features by category:")
total_counted = 0
for category, features in feature_categories.items():
    existing = [f for f in features if f in usable_features]
    if existing:
        total_counted += len(existing)
        print(f"\n{category} ({len(existing)} features):")
        for feat in existing:
            missing_pct = df[feat].isnull().sum() / len(df) * 100
            dtype = str(df[feat].dtype)
            status = "[OK]" if missing_pct < 5 else "[WARN]" if missing_pct < 50 else "[BAD]"
            print(f"  {status} {feat} ({dtype}, {missing_pct:.1f}% missing)")

# Check for uncategorized usable features
categorized_features = []
for features in feature_categories.values():
    categorized_features.extend([f for f in features if f in usable_features])

uncategorized = [f for f in usable_features if f not in categorized_features]
if uncategorized:
    print(f"\nUncategorized usable features ({len(uncategorized)}):")
    for feat in uncategorized:
        missing_pct = df[feat].isnull().sum() / len(df) * 100
        dtype = str(df[feat].dtype)
        print(f"  - {feat} ({dtype}, {missing_pct:.1f}% missing)")

# ============================================================================
# 4. COLUMNS FOR EDA
# ============================================================================
print("\n" + "=" * 80)
print("4. COLUMNS USABLE FOR EDA")
print("=" * 80)

print("\nFor EDA, you can use ALL columns including:")
print("  - Identifiers (for grouping/filtering)")
print("  - Dates (for time series analysis)")
print("  - Text fields (for frequency analysis)")
print("  - Target variable (for distribution analysis)")

eda_exclude = ['contract_id']  # Only exclude contract_id if it's truly unique
eda_usable = [col for col in df.columns if col not in eda_exclude]
print(f"\nTotal columns usable for EDA: {len(eda_usable)}")

# ============================================================================
# 5. RECOMMENDED FEATURE SETS
# ============================================================================
print("\n" + "=" * 80)
print("5. RECOMMENDED FEATURE SETS FOR ML")
print("=" * 80)

# High-value features (flags and risk scores)
high_value_features = [
    'single_source_flag', 'rapid_payment_flag', 'suspicious_pricing',
    'has_duplicate_payments', 'overpayment_flag', 'shell_company_address',
    'suspicious_officer_pattern', 'contract_award_risk_score',
    'payment_risk_score', 'overall_risk_score'
]

existing_high_value = [f for f in high_value_features if f in usable_features]
print(f"\nHigh-Value Binary Flags & Risk Scores ({len(existing_high_value)} features):")
print("  These are the most interpretable and important features:")
for feat in existing_high_value:
    print(f"    - {feat}")

# All numeric features (ready for ML)
numeric_features_usable = [f for f in numeric_cols if f not in exclude_list]
print(f"\nAll Numeric Features ({len(numeric_features_usable)} features):")
print("  Ready for ML algorithms without encoding:")
print(f"    Examples: {', '.join(numeric_features_usable[:10])}...")

# Categorical features that need encoding
categorical_features_usable = [f for f in categorical_cols if f not in exclude_list]
print(f"\nCategorical Features ({len(categorical_features_usable)} features):")
print("  Need encoding (one-hot, label, or target encoding):")
for feat in categorical_features_usable:
    unique_count = df[feat].nunique()
    print(f"    - {feat} ({unique_count} unique values)")

# ============================================================================
# 6. MISSING VALUE IMPACT
# ============================================================================
print("\n" + "=" * 80)
print("6. MISSING VALUE IMPACT ON USABLE FEATURES")
print("=" * 80)

usable_with_missing = []
for feat in usable_features:
    missing_count = df[feat].isnull().sum()
    if missing_count > 0:
        missing_pct = missing_count / len(df) * 100
        usable_with_missing.append((feat, missing_count, missing_pct))

if usable_with_missing:
    print(f"\nFeatures with missing values ({len(usable_with_missing)}):")
    usable_with_missing.sort(key=lambda x: x[2], reverse=True)
    for feat, count, pct in usable_with_missing:
        print(f"  - {feat}: {count:,} missing ({pct:.2f}%)")
        if pct < 5:
            print(f"    -> Action: Simple imputation (mean/median/mode)")
        elif pct < 25:
            print(f"    -> Action: Consider imputation or drop if not critical")
        else:
            print(f"    -> Action: Consider dropping or advanced imputation")
else:
    print("\n[OK] No missing values in usable features!")

# ============================================================================
# 7. SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("7. SUMMARY & RECOMMENDATIONS")
print("=" * 80)

print(f"\nTotal columns in dataset: {len(df.columns)}")
print(f"Columns excluded from ML: {len(exclude_list)}")
print(f"Usable feature columns for ML: {len(usable_features)}")
print(f"  - Numeric features: {len(numeric_features_usable)}")
print(f"  - Categorical features: {len(categorical_features_usable)}")
print(f"  - Boolean/Flag features: {len([f for f in bool_cols if f in usable_features])}")

print("\nRecommended ML Feature Set:")
print(f"  - Use all {len(numeric_features_usable)} numeric features")
print(f"  - Encode {len(categorical_features_usable)} categorical features")
print(f"  - Total: ~{len(usable_features)} features after encoding")

print("\nFor EDA:")
print(f"  - Use all {len(eda_usable)} columns for comprehensive analysis")
print(f"  - Focus on risk scores and flag features for fraud patterns")

print("\n" + "=" * 80)

