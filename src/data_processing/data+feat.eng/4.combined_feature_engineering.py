import pandas as pd
import numpy as np
from contract_award_features import engineer_contract_award_features
from payment_fraud_features import engineer_payment_fraud_features


def engineer_all_features(contracts_df, vendors_df, payments_df, market_prices_df=None, verbose=True):
    """
    Combines both contract award and payment fraud feature engineering modules.
    
    This function orchestrates the feature engineering pipeline:
    1. First applies contract award fraud features
    2. Then applies payment fraud features
    3. Returns enhanced dataframes with all features
    
    Args:
        contracts_df: DataFrame with contract information
        vendors_df: DataFrame with vendor information
        payments_df: DataFrame with payment records
        market_prices_df: Optional DataFrame with market reference prices
        verbose: Whether to print progress information
        
    Returns:
        tuple: (enhanced_contracts_df, enhanced_payments_df)
            - enhanced_contracts_df: Contracts dataframe with both award and payment features
            - enhanced_payments_df: Payments dataframe with payment features
    """
    
    if verbose:
        print("=" * 80)
        print("COMBINED FEATURE ENGINEERING PIPELINE")
        print("=" * 80)
        print(f"\nInput Data Summary:")
        print(f"  Contracts: {len(contracts_df)}")
        print(f"  Vendors: {len(vendors_df)}")
        print(f"  Payments: {len(payments_df)}")
        if market_prices_df is not None:
            print(f"  Market Prices: {len(market_prices_df)}")
    
    # ========================================================================
    # STEP 1: CONTRACT AWARD FEATURES
    # ========================================================================
    if verbose:
        print("\n" + "=" * 80)
        print("STEP 1: ENGINEERING CONTRACT AWARD FEATURES")
        print("=" * 80)
    
    contracts_enhanced = engineer_contract_award_features(
        contracts_df.copy(),
        vendors_df.copy(),
        market_prices_df.copy() if market_prices_df is not None else None,
        verbose=verbose
    )
    
    # ========================================================================
    # STEP 2: PAYMENT FRAUD FEATURES
    # ========================================================================
    if verbose:
        print("\n" + "=" * 80)
        print("STEP 2: ENGINEERING PAYMENT FRAUD FEATURES")
        print("=" * 80)
    
    contracts_final, payments_enhanced = engineer_payment_fraud_features(
        contracts_enhanced.copy(),
        payments_df.copy()
    )
    
    # ========================================================================
    # STEP 3: FINAL SUMMARY
    # ========================================================================
    if verbose:
        print("\n" + "=" * 80)
        print("FEATURE ENGINEERING COMPLETE - FINAL SUMMARY")
        print("=" * 80)
        
        original_cols = len(contracts_df.columns)
        final_cols = len(contracts_final.columns)
        added_cols = final_cols - original_cols
        
        print(f"\nContract Features:")
        print(f"  Original columns: {original_cols}")
        print(f"  Final columns: {final_cols}")
        print(f"  New features added: {added_cols}")
        
        print(f"\nPayment Features:")
        original_payment_cols = len(payments_df.columns)
        final_payment_cols = len(payments_enhanced.columns)
        added_payment_cols = final_payment_cols - original_payment_cols
        print(f"  Original columns: {original_payment_cols}")
        print(f"  Final columns: {final_payment_cols}")
        print(f"  New features added: {added_payment_cols}")
        
        # Show combined risk scores if available
        if 'contract_award_risk_score' in contracts_final.columns and 'payment_risk_score' in contracts_final.columns:
            print(f"\nCombined Risk Analysis:")
            print(f"  Average Contract Award Risk: {contracts_final['contract_award_risk_score'].mean():.2f}")
            print(f"  Average Payment Risk: {contracts_final['payment_risk_score'].mean():.2f}")
            
            # Create overall risk score
            contracts_final['overall_risk_score'] = (
                contracts_final['contract_award_risk_score'] * 0.5 + 
                contracts_final['payment_risk_score'] * 0.5
            )
            
            contracts_final['overall_risk_level'] = pd.cut(
                contracts_final['overall_risk_score'],
                bins=[0, 20, 40, 60, 100],
                labels=['Low', 'Medium', 'High', 'Critical']
            )
            
            print(f"  Average Overall Risk: {contracts_final['overall_risk_score'].mean():.2f}")
            print(f"\n  Overall Risk Distribution:")
            print(contracts_final['overall_risk_level'].value_counts().to_string())
    
    return contracts_final, payments_enhanced


def get_all_feature_names(contracts_df):
    """
    Returns a list of all feature names that can be used for ML modeling.
    
    Args:
        contracts_df: Enhanced contracts dataframe
        
    Returns:
        dict: Dictionary with feature categories and their feature names
    """
    
    feature_categories = {
        'contract_award_features': [
            # Pricing features
            'price_deviation_pct', 'price_deviation_from_median_pct', 'price_zscore',
            'extreme_high_price', 'extreme_low_price', 'suspicious_pricing',
            'near_threshold', 'is_round_number', 'benford_deviation',
            'market_price_deviation_pct', 'above_market_price',
            
            # Competition features
            'num_bids', 'single_source_flag', 'non_competitive_procedure',
            'low_competition', 'competition_score', 'high_value_single_bid',
            'high_value_non_competitive',
            
            # Timing features
            'weekend_award', 'month_end_award', 'fy_end_award',
            'short_advertisement', 'very_short_advertisement', 'long_advertisement',
            'rapid_award', 'delayed_award',
            
            # Vendor features
            'vendor_age_years', 'small_employee_count', 'very_small_vendor',
            'new_vendor', 'new_vendor_large_contract',
            'vendor_total_contracts', 'vendor_total_value',
            'vendor_category_market_share', 'high_vendor_concentration',
            'dominant_vendor', 'vendor_win_rate', 'suspiciously_high_win_rate',
            'shell_company_address',
            
            # Officer features
            'officer_single_source_rate', 'suspicious_officer_pattern',
            
            # Composite scores
            'pricing_risk', 'competition_risk', 'timing_risk', 'vendor_risk',
            'officer_risk', 'contract_award_risk_score', 'risk_level'
        ],
        
        'payment_features': [
            # Payment speed
            'days_to_first_payment', 'rapid_payment_flag', 'delayed_payment_flag',
            
            # Payment patterns
            'num_payments', 'avg_payment_interval_days', 'irregular_payment_frequency',
            
            # Duplicate detection
            'has_duplicate_payments',
            
            # Round numbers
            'num_round_payments', 'excessive_round_payments',
            
            # Timing
            'has_weekend_payments',
            
            # Amount mismatches
            'total_paid', 'payment_variance_pct', 'overpayment_flag', 'underpayment_flag',
            
            # Advance payments
            'large_advance_no_guarantee',
            
            # Composite scores
            'payment_risk_score', 'payment_risk_level'
        ],
        
        'combined_features': [
            'overall_risk_score', 'overall_risk_level'
        ]
    }
    
    # Filter to only include features that exist in the dataframe
    available_features = {}
    for category, features in feature_categories.items():
        available = [f for f in features if f in contracts_df.columns]
        if available:
            available_features[category] = available
    
    return available_features


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("COMBINED FEATURE ENGINEERING MODULE")
    print("=" * 80)
    
    print("""
To use this module with your data:

# Load your data
contracts_df = pd.read_csv('india_contracts.csv')
vendors_df = pd.read_csv('india_vendors.csv')
payments_df = pd.read_csv('india_payments.csv')
market_prices_df = pd.read_csv('india_market_prices.csv')  # Optional

# Engineer all features (both award and payment)
contracts_enhanced, payments_enhanced = engineer_all_features(
    contracts_df,
    vendors_df,
    payments_df,
    market_prices_df,  # Optional
    verbose=True
)

# Get available feature names
feature_dict = get_all_feature_names(contracts_enhanced)

# Select features for ML model
all_features = (
    feature_dict.get('contract_award_features', []) +
    feature_dict.get('payment_features', []) +
    feature_dict.get('combined_features', [])
)

# Prepare data for modeling
X = contracts_enhanced[all_features].fillna(0)
y = contracts_enhanced['is_fraud']  # Your labels

# Train model
from sklearn.ensemble import RandomForestClassifier
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

# Save enhanced data
contracts_enhanced.to_csv('contracts_with_all_features.csv', index=False)
payments_enhanced.to_csv('payments_enhanced.csv', index=False)
""")

