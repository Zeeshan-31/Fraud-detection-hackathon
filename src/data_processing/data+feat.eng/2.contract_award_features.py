import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

"""
CONTRACT AWARD FRAUD - COMPREHENSIVE FEATURE ENGINEERING
Detects fraud patterns at the contract award stage
"""

def engineer_contract_award_features(contracts_df, vendors_df, market_prices_df=None, verbose=True):
    """
    Creates advanced features to detect contract award fraud
    
    Args:
        contracts_df: DataFrame with contract information
        vendors_df: DataFrame with vendor information
        market_prices_df: Optional DataFrame with market reference prices
        verbose: Whether to print progress
        
    Returns:
        Enhanced DataFrame with contract award fraud features
    """
    
    if verbose:
        print("=" * 80)
        print("CONTRACT AWARD FRAUD - FEATURE ENGINEERING")
        print("=" * 80)
        print(f"\nInput Data:")
        print(f"  Contracts: {len(contracts_df)}")
        print(f"  Vendors: {len(vendors_df)}")
    
    # Create copies
    contracts = contracts_df.copy()
    vendors = vendors_df.copy()
    
    # Ensure dates are datetime
    contracts['award_date'] = pd.to_datetime(contracts['award_date'])
    contracts['publication_date'] = pd.to_datetime(contracts['publication_date'])
    if 'completion_date' in contracts.columns:
        contracts['completion_date'] = pd.to_datetime(contracts['completion_date'])
    
    # Merge with vendor info
    contracts = contracts.merge(vendors, on='vendor_id', how='left')
    
    # ========================================================================
    # CATEGORY 1: PRICING ANOMALIES
    # ========================================================================
    if verbose:
        print("\n" + "=" * 80)
        print("CATEGORY 1: PRICING ANOMALIES")
        print("=" * 80)
    
    # Feature 1.1: Price deviation from category average
    if verbose:
        print("\n1.1 Calculating price deviations...")
    
    category_stats = contracts.groupby('category')['amount_inr'].agg(['mean', 'std', 'median']).reset_index()
    category_stats.columns = ['category', 'category_avg_price', 'category_std_price', 'category_median_price']
    contracts = contracts.merge(category_stats, on='category', how='left')
    
    # Deviation from mean
    contracts['price_deviation_from_mean'] = contracts['amount_inr'] - contracts['category_avg_price']
    contracts['price_deviation_pct'] = (
        contracts['price_deviation_from_mean'] / contracts['category_avg_price'] * 100
    )
    
    # Deviation from median (more robust to outliers)
    contracts['price_deviation_from_median_pct'] = (
        (contracts['amount_inr'] - contracts['category_median_price']) / 
        contracts['category_median_price'] * 100
    )
    
    # Z-score (statistical outlier detection)
    contracts['price_zscore'] = (
        (contracts['amount_inr'] - contracts['category_avg_price']) / 
        contracts['category_std_price'].replace(0, 1)
    )
    
    # Flag extreme pricing
    contracts['extreme_high_price'] = (contracts['price_zscore'] > 2.5).astype(int)
    contracts['extreme_low_price'] = (contracts['price_zscore'] < -2.5).astype(int)
    contracts['suspicious_pricing'] = (contracts['price_zscore'].abs() > 2).astype(int)
    
    if verbose:
        print(f"   ✓ Extreme high prices: {contracts['extreme_high_price'].sum()}")
        print(f"   ✓ Extreme low prices: {contracts['extreme_low_price'].sum()}")
        print(f"   ✓ Average price deviation: {contracts['price_deviation_pct'].mean():.2f}%")
    
    # Feature 1.2: If market prices provided, compare against them
    if market_prices_df is not None:
        if verbose:
            print("\n1.2 Comparing against market reference prices...")
        
        contracts = contracts.merge(
            market_prices_df[['category', 'avg_price_inr']], 
            on='category', 
            how='left',
            suffixes=('', '_market')
        )
        
        contracts['market_price_deviation_pct'] = (
            (contracts['amount_inr'] - contracts['avg_price_inr']) / 
            contracts['avg_price_inr'] * 100
        )
        contracts['above_market_price'] = (contracts['market_price_deviation_pct'] > 50).astype(int)
    
    # Feature 1.3: Threshold manipulation detection
    if verbose:
        print("\n1.3 Detecting threshold manipulation...")
    
    # Common oversight thresholds in India
    thresholds = [
        (1000000, 1050000, '10_lakh'),      # ₹10 Lakh
        (2500000, 2600000, '25_lakh'),      # ₹25 Lakh  
        (5000000, 5200000, '50_lakh'),      # ₹50 Lakh
        (10000000, 10500000, '1_crore'),    # ₹1 Crore
    ]
    
    contracts['near_threshold'] = 0
    contracts['threshold_type'] = 'none'
    
    for lower, upper, name in thresholds:
        mask = (contracts['amount_inr'] >= lower * 0.95) & (contracts['amount_inr'] < lower)
        contracts.loc[mask, 'near_threshold'] = 1
        contracts.loc[mask, 'threshold_type'] = f'just_below_{name}'
    
    if verbose:
        print(f"   ✓ Contracts near thresholds: {contracts['near_threshold'].sum()}")
    
    # Feature 1.4: Round number analysis (Benford's Law)
    if verbose:
        print("\n1.4 Applying Benford's Law...")
    
    # First digit distribution
    contracts['amount_first_digit'] = contracts['amount_inr'].astype(str).str[0].astype(int)
    
    # Benford's Law expected distribution
    benford_expected = {1: 0.301, 2: 0.176, 3: 0.125, 4: 0.097, 5: 0.079, 
                        6: 0.067, 7: 0.058, 8: 0.051, 9: 0.046}
    
    # Check if amount is suspiciously round
    contracts['is_round_number'] = (
        (contracts['amount_inr'] % 100000 == 0) |  # Multiple of 1 Lakh
        (contracts['amount_inr'] % 50000 == 0) |   # Multiple of 50K
        (contracts['amount_inr'] % 10000 == 0)     # Multiple of 10K
    ).astype(int)
    
    # Benford deviation score
    actual_dist = contracts['amount_first_digit'].value_counts(normalize=True)
    contracts['benford_deviation'] = contracts['amount_first_digit'].map(
        lambda d: abs(actual_dist.get(d, 0) - benford_expected.get(d, 0))
    )
    
    if verbose:
        print(f"   ✓ Round number contracts: {contracts['is_round_number'].sum()}")
    
    # ========================================================================
    # CATEGORY 2: COMPETITION ANOMALIES
    # ========================================================================
    if verbose:
        print("\n" + "=" * 80)
        print("CATEGORY 2: COMPETITION ANOMALIES")
        print("=" * 80)
    
    # Feature 2.1: Bid competition analysis
    if verbose:
        print("\n2.1 Analyzing bid competition...")
    
    # Single source flag
    contracts['single_source_flag'] = (
        (contracts['procedure_type'] == 'Single Source') | 
        (contracts['num_bids'] == 1)
    ).astype(int)
    
    # Non-competitive procedure
    contracts['non_competitive_procedure'] = (
        contracts['procedure_type'].isin(['Single Source', 'Limited Tender'])
    ).astype(int)
    
    # Low competition (< 3 bids for open tender)
    contracts['low_competition'] = (
        (contracts['procedure_type'] == 'Open Tender') & 
        (contracts['num_bids'] < 3)
    ).astype(int)
    
    # Competition score (normalized)
    contracts['competition_score'] = np.clip(contracts['num_bids'] / 10 * 100, 0, 100)
    
    if verbose:
        print(f"   ✓ Single source contracts: {contracts['single_source_flag'].sum()}")
        print(f"   ✓ Low competition: {contracts['low_competition'].sum()}")
        print(f"   ✓ Average bids per contract: {contracts['num_bids'].mean():.2f}")
    
    # Feature 2.2: Suspicious bid patterns
    if verbose:
        print("\n2.2 Detecting suspicious bid patterns...")
    
    # High-value contract with single bid
    contracts['high_value_single_bid'] = (
        (contracts['amount_inr'] > 1000000) & 
        (contracts['num_bids'] == 1)
    ).astype(int)
    
    # Non-competitive for high-value
    contracts['high_value_non_competitive'] = (
        (contracts['amount_inr'] > 5000000) & 
        (contracts['non_competitive_procedure'] == 1)
    ).astype(int)
    
    if verbose:
        print(f"   ✓ High-value single bids: {contracts['high_value_single_bid'].sum()}")
    
    # ========================================================================
    # CATEGORY 3: TIMING ANOMALIES
    # ========================================================================
    if verbose:
        print("\n" + "=" * 80)
        print("CATEGORY 3: TIMING ANOMALIES")
        print("=" * 80)
    
    # Feature 3.1: Award timing analysis
    if verbose:
        print("\n3.1 Analyzing award timing...")
    
    # Weekend/holiday awards
    contracts['award_day_of_week'] = contracts['award_date'].dt.dayofweek
    contracts['weekend_award'] = (contracts['award_day_of_week'] >= 5).astype(int)
    
    # Month-end rush (potential budget manipulation)
    contracts['award_day_of_month'] = contracts['award_date'].dt.day
    contracts['month_end_award'] = (contracts['award_day_of_month'] >= 25).astype(int)
    
    # Financial year end (March in India)
    contracts['award_month'] = contracts['award_date'].dt.month
    contracts['fy_end_award'] = (contracts['award_month'] == 3).astype(int)
    
    if verbose:
        print(f"   ✓ Weekend awards: {contracts['weekend_award'].sum()}")
        print(f"   ✓ Month-end awards: {contracts['month_end_award'].sum()}")
        print(f"   ✓ Financial year-end awards: {contracts['fy_end_award'].sum()}")
    
    # Feature 3.2: Advertisement period analysis
    if verbose:
        print("\n3.2 Analyzing advertisement periods...")
    
    # Short advertisement period
    contracts['short_advertisement'] = (contracts['advertisement_days'] < 7).astype(int)
    contracts['very_short_advertisement'] = (contracts['advertisement_days'] < 3).astype(int)
    
    # Unusually long advertisement (potential favoritism - waiting for specific vendor)
    contracts['long_advertisement'] = (contracts['advertisement_days'] > 45).astype(int)
    
    if verbose:
        print(f"   ✓ Short advertisement periods: {contracts['short_advertisement'].sum()}")
        print(f"   ✓ Very short (<3 days): {contracts['very_short_advertisement'].sum()}")
    
    # Feature 3.3: Time from publication to award
    contracts['publication_to_award_days'] = (
        contracts['award_date'] - contracts['publication_date']
    ).dt.days
    
    contracts['rapid_award'] = (contracts['publication_to_award_days'] < 10).astype(int)
    contracts['delayed_award'] = (contracts['publication_to_award_days'] > 90).astype(int)
    
    if verbose:
        print(f"   ✓ Rapid awards (<10 days): {contracts['rapid_award'].sum()}")
    
    # ========================================================================
    # CATEGORY 4: VENDOR ANOMALIES
    # ========================================================================
    if verbose:
        print("\n" + "=" * 80)
        print("CATEGORY 4: VENDOR ANOMALIES")
        print("=" * 80)
    
    # Feature 4.1: Vendor characteristics
    if verbose:
        print("\n4.1 Analyzing vendor characteristics...")
    
    # Shell company indicators
    contracts['small_employee_count'] = (contracts['employees'] <= 5).astype(int)
    contracts['very_small_vendor'] = (contracts['employees'] <= 2).astype(int)
    
    # New vendor winning large contract
    # Convert registration_date to datetime in contracts (after merge)
    contracts['registration_date'] = pd.to_datetime(contracts['registration_date'])
    contracts['vendor_age_days'] = (
        contracts['award_date'] - contracts['registration_date']
    ).dt.days
    contracts['vendor_age_years'] = contracts['vendor_age_days'] / 365.25
    
    contracts['new_vendor'] = (contracts['vendor_age_years'] < 1).astype(int)
    contracts['new_vendor_large_contract'] = (
        (contracts['new_vendor'] == 1) & 
        (contracts['amount_inr'] > 2000000)
    ).astype(int)
    
    if verbose:
        print(f"   ✓ Small vendors (<= 5 employees): {contracts['small_employee_count'].sum()}")
        print(f"   ✓ New vendors (<1 year): {contracts['new_vendor'].sum()}")
        print(f"   ✓ New vendors with large contracts: {contracts['new_vendor_large_contract'].sum()}")
    
    # Feature 4.2: Vendor concentration and patterns
    if verbose:
        print("\n4.2 Calculating vendor concentration metrics...")
    
    # How many contracts does this vendor have?
    vendor_contract_counts = contracts.groupby('vendor_id').size().reset_index(name='vendor_total_contracts')
    contracts = contracts.merge(vendor_contract_counts, on='vendor_id', how='left')
    
    # Total value won by vendor
    vendor_total_value = contracts.groupby('vendor_id')['amount_inr'].sum().reset_index()
    vendor_total_value.columns = ['vendor_id', 'vendor_total_value']
    contracts = contracts.merge(vendor_total_value, on='vendor_id', how='left')
    
    # Vendor market share in category
    category_total = contracts.groupby('category')['amount_inr'].sum().reset_index()
    category_total.columns = ['category', 'category_total_value']
    contracts = contracts.merge(category_total, on='category', how='left')
    
    vendor_category_value = contracts.groupby(['vendor_id', 'category'])['amount_inr'].sum().reset_index()
    vendor_category_value.columns = ['vendor_id', 'category', 'vendor_category_value']
    contracts = contracts.merge(vendor_category_value, on=['vendor_id', 'category'], how='left')
    
    contracts['vendor_category_market_share'] = (
        contracts['vendor_category_value'] / contracts['category_total_value'] * 100
    )
    
    # High concentration flag
    contracts['high_vendor_concentration'] = (contracts['vendor_total_contracts'] > 10).astype(int)
    contracts['dominant_vendor'] = (contracts['vendor_category_market_share'] > 30).astype(int)
    
    if verbose:
        print(f"   ✓ High concentration vendors: {contracts['high_vendor_concentration'].sum()}")
        print(f"   ✓ Dominant vendors (>30% share): {contracts['dominant_vendor'].sum()}")
    
    # Feature 4.3: Vendor win rate
    if verbose:
        print("\n4.3 Calculating vendor win rates...")
    
    # Win rate (contracts won / total contracts vendor participated in)
    # Approximate: assume participation in similar category contracts
    contracts['vendor_win_rate'] = (
        contracts['vendor_total_contracts'] / 
        contracts.groupby('category')['contract_id'].transform('count') * 100
    )
    
    contracts['suspiciously_high_win_rate'] = (contracts['vendor_win_rate'] > 50).astype(int)
    
    if verbose:
        print(f"   ✓ Vendors with >50% win rate: {contracts['suspiciously_high_win_rate'].sum()}")
    
    # ========================================================================
    # CATEGORY 5: GEOGRAPHIC ANOMALIES
    # ========================================================================
    if verbose:
        print("\n" + "=" * 80)
        print("CATEGORY 5: GEOGRAPHIC ANOMALIES")
        print("=" * 80)
    
    # Feature 5.1: Cross-state contracts
    if verbose:
        print("\n5.1 Detecting geographic anomalies...")
    
    # Vendor from different state (for state/municipal contracts)
    contracts['ministry_type'] = contracts['ministry'].apply(
        lambda x: 'state' if 'State' in x or 'Municipal' in x else 'central'
    )
    
    # This is approximate - in real data, you'd have ministry location
    contracts['cross_state_contract'] = (
        (contracts['ministry_type'] == 'state') & 
        (contracts['state'] != contracts['state'].mode()[0])  # Different from most common
    ).astype(int)
    
    # Feature 5.2: Vendor address clustering
    if verbose:
        print("\n5.2 Analyzing vendor address patterns...")
    
    # Multiple vendors at same address (shell company network)
    address_counts = contracts.groupby('address')['vendor_id'].nunique().reset_index()
    address_counts.columns = ['address', 'vendors_at_address']
    contracts = contracts.merge(address_counts, on='address', how='left')
    
    contracts['shell_company_address'] = (contracts['vendors_at_address'] > 3).astype(int)
    
    if verbose:
        shell_addresses = contracts[contracts['shell_company_address'] == 1]['address'].nunique()
        print(f"   ✓ Suspicious addresses (>3 vendors): {shell_addresses}")
    
    # ========================================================================
    # CATEGORY 6: OFFICER/APPROVER PATTERNS
    # ========================================================================
    if verbose:
        print("\n" + "=" * 80)
        print("CATEGORY 6: OFFICER/APPROVER PATTERNS")
        print("=" * 80)
    
    # Feature 6.1: Officer approval patterns
    if verbose:
        print("\n6.1 Analyzing officer approval patterns...")
    
    # How many contracts has this officer approved?
    officer_counts = contracts.groupby('officer_id').agg({
        'contract_id': 'count',
        'single_source_flag': 'sum',
        'amount_inr': 'sum'
    }).reset_index()
    officer_counts.columns = ['officer_id', 'officer_total_approvals', 
                             'officer_single_source_count', 'officer_total_value']
    contracts = contracts.merge(officer_counts, on='officer_id', how='left')
    
    # Officer's single-source rate
    contracts['officer_single_source_rate'] = (
        contracts['officer_single_source_count'] / 
        contracts['officer_total_approvals'] * 100
    )
    
    contracts['suspicious_officer_pattern'] = (
        (contracts['officer_single_source_rate'] > 50) & 
        (contracts['officer_total_approvals'] > 5)
    ).astype(int)
    
    if verbose:
        print(f"   ✓ Officers with suspicious patterns: {contracts['suspicious_officer_pattern'].sum()}")
    
    # ========================================================================
    # CATEGORY 7: CONTRACT CHARACTERISTICS
    # ========================================================================
    if verbose:
        print("\n" + "=" * 80)
        print("CATEGORY 7: CONTRACT CHARACTERISTICS")
        print("=" * 80)
    
    # Feature 7.1: Contract duration analysis
    if verbose:
        print("\n7.1 Analyzing contract durations...")
    
    # Unusually short duration for contract value
    contracts['days_per_lakh'] = contracts['contract_duration_days'] / (contracts['amount_inr'] / 100000)
    contracts['unrealistic_short_duration'] = (contracts['days_per_lakh'] < 1).astype(int)
    
    # Very long duration (potential stalling)
    contracts['excessive_duration'] = (contracts['contract_duration_days'] > 365).astype(int)
    
    if verbose:
        print(f"   ✓ Unrealistically short durations: {contracts['unrealistic_short_duration'].sum()}")
    
    # Feature 7.2: Performance guarantee analysis
    if verbose:
        print("\n7.2 Analyzing performance guarantees...")
    
    # High-value contract without guarantee
    contracts['high_value_no_guarantee'] = (
        (contracts['amount_inr'] > 5000000) & 
        (contracts['performance_guarantee_pct'] == 0)
    ).astype(int)
    
    # Low guarantee for high-risk category
    high_risk_categories = ['Construction', 'Road Development', 'Software Development']
    contracts['high_risk_low_guarantee'] = (
        (contracts['category'].isin(high_risk_categories)) & 
        (contracts['performance_guarantee_pct'] < 5) & 
        (contracts['amount_inr'] > 2000000)
    ).astype(int)
    
    if verbose:
        print(f"   ✓ High-value without guarantee: {contracts['high_value_no_guarantee'].sum()}")
    
    # ========================================================================
    # COMPOSITE RISK SCORES
    # ========================================================================
    if verbose:
        print("\n" + "=" * 80)
        print("CATEGORY 8: COMPOSITE RISK SCORES")
        print("=" * 80)
    
    # Define risk categories and their features
    risk_categories = {
        'pricing_risk': [
            'extreme_high_price', 'near_threshold', 'is_round_number'
        ],
        'competition_risk': [
            'single_source_flag', 'low_competition', 'high_value_non_competitive'
        ],
        'timing_risk': [
            'weekend_award', 'fy_end_award', 'short_advertisement', 'rapid_award'
        ],
        'vendor_risk': [
            'small_employee_count', 'new_vendor_large_contract', 
            'shell_company_address', 'suspiciously_high_win_rate'
        ],
        'officer_risk': [
            'suspicious_officer_pattern'
        ]
    }
    
    # Calculate individual risk scores
    for risk_type, features in risk_categories.items():
        available_features = [f for f in features if f in contracts.columns]
        if available_features:
            contracts[risk_type] = (
                contracts[available_features].sum(axis=1) / len(available_features) * 100
            )
    
    # Overall contract award risk score
    risk_score_features = [k for k in risk_categories.keys() if k in contracts.columns]
    contracts['contract_award_risk_score'] = (
        contracts[risk_score_features].mean(axis=1)
    )
    
    # Risk level categorization
    contracts['risk_level'] = pd.cut(
        contracts['contract_award_risk_score'],
        bins=[0, 20, 40, 60, 100],
        labels=['Low', 'Medium', 'High', 'Critical']
    )
    
    if verbose:
        print(f"\n   Risk Score Distribution:")
        print(contracts['risk_level'].value_counts().to_string())
        print(f"\n   Average risk scores by category:")
        for risk_type in risk_score_features:
            print(f"     - {risk_type}: {contracts[risk_type].mean():.2f}")
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    if verbose:
        print("\n" + "=" * 80)
        print("FEATURE ENGINEERING COMPLETE - SUMMARY")
        print("=" * 80)
        
        original_cols = len(contracts_df.columns)
        new_cols = len(contracts.columns)
        added_cols = new_cols - original_cols
        
        print(f"\nOriginal columns: {original_cols}")
        print(f"Enhanced columns: {new_cols}")
        print(f"New features added: {added_cols}")
        
        print(f"\nHigh-risk contracts (score > 60): {(contracts['contract_award_risk_score'] > 60).sum()}")
        print(f"Critical risk contracts (score > 80): {(contracts['contract_award_risk_score'] > 80).sum()}")
        
        print(f"\nKey fraud indicators detected:")
        key_indicators = [
            'extreme_high_price', 'single_source_flag', 'weekend_award',
            'shell_company_address', 'new_vendor_large_contract', 
            'high_value_no_guarantee', 'suspicious_officer_pattern'
        ]
        for indicator in key_indicators:
            if indicator in contracts.columns:
                count = contracts[indicator].sum()
                pct = count / len(contracts) * 100
                print(f"  - {indicator}: {count} ({pct:.1f}%)")
    
    return contracts


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("CONTRACT AWARD FRAUD - FEATURE ENGINEERING MODULE")
    print("=" * 80)
    
    print("""
To use this module with your data:

# Load your data
contracts_df = pd.read_csv('india_contracts.csv')
vendors_df = pd.read_csv('india_vendors.csv')
market_prices_df = pd.read_csv('india_market_prices.csv')  # Optional

# Engineer contract award features
contracts_enhanced = engineer_contract_award_features(
    contracts_df,
    vendors_df,
    market_prices_df,  # Optional
    verbose=True
)

# Save enhanced data
contracts_enhanced.to_csv('contracts_with_award_features.csv', index=False)

# Select features for ML model
award_fraud_features = [
    # Pricing features
    'price_deviation_pct', 'price_zscore', 'near_threshold', 'is_round_number',
    
    # Competition features
    'num_bids', 'single_source_flag', 'low_competition', 'competition_score',
    
    # Timing features
    'weekend_award', 'month_end_award', 'short_advertisement', 'rapid_award',
    
    # Vendor features
    'vendor_age_years', 'small_employee_count', 'vendor_total_contracts',
    'vendor_win_rate', 'shell_company_address',
    
    # Officer features
    'officer_single_source_rate', 'suspicious_officer_pattern',
    
    # Composite scores
    'pricing_risk', 'competition_risk', 'timing_risk', 'vendor_risk',
    'contract_award_risk_score'
]

X = contracts_enhanced[award_fraud_features].fillna(0)
y = contracts_enhanced['is_fraud']  # Your labels

# Train model
from sklearn.ensemble import RandomForestClassifier
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)
""")