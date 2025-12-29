"""
Clean and remove redundant columns from contracts_with_all_features.csv
"""

import pandas as pd
import numpy as np

print("Loading data...")
df = pd.read_csv('contracts_with_all_features.csv')
print(f"Original shape: {df.shape}")

# ============================================================================
# IDENTIFY REDUNDANT COLUMNS TO REMOVE
# ============================================================================

columns_to_remove = []

# 1. Duplicate vendor names (keep vendor_name_y as it's from merged vendors table)
columns_to_remove.append('vendor_name_x')

# 2. Redundant price deviation columns (keep price_deviation_pct and price_zscore)
columns_to_remove.extend([
    'price_deviation_from_mean',  # Can derive from price_deviation_pct
    'price_deviation_from_median_pct',  # Similar to price_deviation_pct
])

# 3. Intermediate calculation columns (statistics used to compute features)
columns_to_remove.extend([
    'category_avg_price',  # Intermediate stat
    'category_std_price',  # Intermediate stat
    'category_median_price',  # Intermediate stat
    'category_total_value',  # Intermediate aggregation
    'vendor_category_value',  # Intermediate aggregation
    'vendor_age_days',  # Use vendor_age_years instead
])

# 4. Redundant date breakdown columns (keep derived flags instead)
columns_to_remove.extend([
    'award_day_of_week',  # Use weekend_award flag
    'award_day_of_month',  # Use month_end_award flag
    'award_month',  # Use fy_end_award flag
])

# 5. Redundant flag columns (keep more specific ones)
columns_to_remove.extend([
    'extreme_high_price',  # Covered by suspicious_pricing
    'extreme_low_price',  # Covered by suspicious_pricing
    'very_small_vendor',  # Use small_employee_count
    'very_short_advertisement',  # Use short_advertisement
])

# 6. Redundant risk score columns (keep composite scores)
columns_to_remove.extend([
    'pricing_risk',  # Individual risk - we have contract_award_risk_score
    'competition_risk',  # Individual risk
    'timing_risk',  # Individual risk
    'vendor_risk',  # Individual risk
    'officer_risk',  # Individual risk
    'risk_level',  # Can derive from contract_award_risk_score
    'payment_risk_level',  # Can derive from payment_risk_score
])

# 7. Duplicate market price column
columns_to_remove.append('avg_price_inr')  # Duplicate of category_avg_price

# 8. Payment intermediate columns
columns_to_remove.extend([
    'first_payment_date',  # Intermediate - we have days_to_first_payment
    'first_payment_amount',  # Intermediate - not needed for ML
    'num_round_payments',  # Intermediate - we have excessive_round_payments flag
])

# 9. Intermediate officer calculation columns
columns_to_remove.extend([
    'officer_single_source_count',  # Intermediate - we have officer_single_source_rate
    'officer_total_value',  # Not needed for fraud detection
])

# 10. Other intermediate/less useful columns
columns_to_remove.extend([
    'days_per_lakh',  # Intermediate calculation
    'threshold_type',  # Categorical - use near_threshold flag instead
    'amount_first_digit',  # Intermediate for Benford's law
    'ministry_type',  # Derived from ministry
    'vendors_at_address',  # Intermediate - use shell_company_address flag
])

# Remove columns that don't exist (to avoid errors)
columns_to_remove = [col for col in columns_to_remove if col in df.columns]

print(f"\nRemoving {len(columns_to_remove)} redundant columns:")
for col in columns_to_remove:
    print(f"  - {col}")

# Create cleaned dataframe
df_cleaned = df.drop(columns=columns_to_remove)

print(f"\nCleaned shape: {df_cleaned.shape}")
print(f"Columns removed: {len(columns_to_remove)}")
print(f"Columns remaining: {len(df_cleaned.columns)}")

# ============================================================================
# SAVE CLEANED DATASET
# ============================================================================

output_file = 'contracts_cleaned.csv'
df_cleaned.to_csv(output_file, index=False)
print(f"\nCleaned dataset saved to: {output_file}")

# ============================================================================
# SUMMARY OF REMAINING COLUMNS BY CATEGORY
# ============================================================================

print("\n" + "=" * 80)
print("REMAINING COLUMNS BY CATEGORY")
print("=" * 80)

categories = {
    'Core Contract Info': [
        'contract_id', 'tender_number', 'publication_date', 'award_date',
        'vendor_id', 'vendor_name_y', 'amount_inr', 'ministry', 'category',
        'procedure_type', 'num_bids', 'advertisement_days', 
        'contract_duration_days', 'completion_date', 'officer_id',
        'payment_terms', 'performance_guarantee_pct', 'is_fraud', 'fraud_reason'
    ],
    'Vendor Info': [
        'registration_date', 'address', 'city', 'state', 'pincode',
        'business_type', 'employees', 'gst_number', 'blacklisted'
    ],
    'Pricing Features': [
        'price_deviation_pct', 'price_zscore', 'suspicious_pricing',
        'market_price_deviation_pct', 'above_market_price', 'near_threshold',
        'is_round_number', 'benford_deviation'
    ],
    'Competition Features': [
        'single_source_flag', 'non_competitive_procedure', 'low_competition',
        'competition_score', 'high_value_single_bid', 'high_value_non_competitive'
    ],
    'Timing Features': [
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
    'Officer Features': [
        'officer_total_approvals', 'officer_single_source_rate',
        'suspicious_officer_pattern'
    ],
    'Contract Characteristics': [
        'unrealistic_short_duration', 'excessive_duration',
        'high_value_no_guarantee', 'high_risk_low_guarantee'
    ],
    'Payment Features': [
        'days_to_first_payment', 'rapid_payment_flag', 'delayed_payment_flag',
        'num_payments', 'avg_payment_interval_days', 'irregular_payment_frequency',
        'has_duplicate_payments', 'excessive_round_payments', 'has_weekend_payments',
        'total_paid', 'payment_variance_pct', 'overpayment_flag', 'underpayment_flag',
        'large_advance_no_guarantee'
    ],
    'Risk Scores': [
        'contract_award_risk_score', 'payment_risk_score',
        'overall_risk_score', 'overall_risk_level'
    ]
}

print()
for category, cols in categories.items():
    existing_cols = [c for c in cols if c in df_cleaned.columns]
    if existing_cols:
        print(f"\n{category} ({len(existing_cols)} columns):")
        print(f"  {', '.join(existing_cols)}")

print("\n" + "=" * 80)
print("CLEANING COMPLETE!")
print("=" * 80)
print(f"\nUse 'contracts_cleaned.csv' for your EDA and ML modeling.")
print(f"It contains {len(df_cleaned.columns)} columns (down from {len(df.columns)}).")

