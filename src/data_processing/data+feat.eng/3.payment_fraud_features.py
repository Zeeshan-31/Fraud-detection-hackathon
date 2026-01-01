import pandas as pd
import numpy as np
from datetime import datetime, timedelta

"""
PAYMENT IRREGULARITY DETECTION FEATURES
Add these to your existing procurement fraud detection system
"""

def engineer_payment_fraud_features(contracts_df, payments_df):
    """
    Creates advanced features to detect payment irregularities
    
    Args:
        contracts_df: DataFrame with contract information
        payments_df: DataFrame with payment records
        
    Returns:
        DataFrame with payment fraud features
    """
    
    print("=" * 80)
    print("ENGINEERING PAYMENT FRAUD DETECTION FEATURES")
    print("=" * 80)
    
    # Ensure dates are datetime
    contracts_df['award_date'] = pd.to_datetime(contracts_df['award_date'])
    payments_df['payment_date'] = pd.to_datetime(payments_df['payment_date'])
    
    # ========================================================================
    # FEATURE 1: PAYMENT SPEED ANALYSIS
    # ========================================================================
    print("\n1. Analyzing payment speed...")
    
    # Calculate time from contract award to first payment
    first_payments = payments_df.groupby('contract_id').agg({
        'payment_date': 'min',
        'amount_inr': 'first'
    }).reset_index()
    first_payments.columns = ['contract_id', 'first_payment_date', 'first_payment_amount']
    
    contracts_df = contracts_df.merge(first_payments, on='contract_id', how='left')
    contracts_df['days_to_first_payment'] = (
        contracts_df['first_payment_date'] - contracts_df['award_date']
    ).dt.days
    
    # Flag suspiciously fast payments (< 3 days)
    contracts_df['rapid_payment_flag'] = (contracts_df['days_to_first_payment'] < 3).astype(int)
    
    # Flag suspiciously slow payments (> 180 days)
    contracts_df['delayed_payment_flag'] = (contracts_df['days_to_first_payment'] > 180).astype(int)
    
    print(f"   - Rapid payments detected: {contracts_df['rapid_payment_flag'].sum()}")
    print(f"   - Delayed payments detected: {contracts_df['delayed_payment_flag'].sum()}")
    
    # ========================================================================
    # FEATURE 2: PAYMENT PATTERN ANALYSIS
    # ========================================================================
    print("\n2. Analyzing payment patterns...")
    
    # Count payments per contract
    payment_counts = payments_df.groupby('contract_id').size().reset_index(name='num_payments')
    contracts_df = contracts_df.merge(payment_counts, on='contract_id', how='left')
    
    # Calculate payment frequency (average days between payments)
    def calculate_payment_frequency(group):
        if len(group) < 2:
            return 0
        dates = sorted(pd.to_datetime(group['payment_date']))
        intervals = [(dates[i+1] - dates[i]).days for i in range(len(dates)-1)]
        return np.mean(intervals) if intervals else 0
    
    payment_freq = payments_df.groupby('contract_id').apply(
        calculate_payment_frequency
    ).reset_index(name='avg_payment_interval_days')
    contracts_df = contracts_df.merge(payment_freq, on='contract_id', how='left')
    
    # Flag unusual payment frequency
    contracts_df['irregular_payment_frequency'] = (
        (contracts_df['avg_payment_interval_days'] < 5) & 
        (contracts_df['num_payments'] > 2)
    ).astype(int)
    
    print(f"   - Contracts with irregular payment frequency: {contracts_df['irregular_payment_frequency'].sum()}")
    
    # ========================================================================
    # FEATURE 3: DUPLICATE PAYMENT DETECTION
    # ========================================================================
    print("\n3. Detecting duplicate payments...")
    
    # Find payments with same amount and date to same vendor
    payments_df['payment_hash'] = (
        payments_df['contract_id'].astype(str) + '_' + 
        payments_df['amount_inr'].astype(str) + '_' + 
        payments_df['payment_date'].astype(str)
    )
    
    duplicate_payments = payments_df.groupby('payment_hash').size()
    duplicate_payment_ids = duplicate_payments[duplicate_payments > 1].index
    
    payments_df['is_duplicate'] = payments_df['payment_hash'].isin(duplicate_payment_ids).astype(int)
    
    # Flag contracts with duplicate payments
    contracts_with_duplicates = payments_df[payments_df['is_duplicate'] == 1]['contract_id'].unique()
    contracts_df['has_duplicate_payments'] = contracts_df['contract_id'].isin(
        contracts_with_duplicates
    ).astype(int)
    
    print(f"   - Duplicate payments found: {payments_df['is_duplicate'].sum()}")
    print(f"   - Contracts affected: {contracts_df['has_duplicate_payments'].sum()}")
    
    # ========================================================================
    # FEATURE 4: ROUND NUMBER ANALYSIS (Benford's Law)
    # ========================================================================
    print("\n4. Applying Benford's Law analysis...")
    
    # Check if payment amounts are suspiciously round
    payments_df['is_round_number'] = (
        (payments_df['amount_inr'] % 100000 == 0) |  # Multiple of 1 Lakh
        (payments_df['amount_inr'] % 50000 == 0)     # Multiple of 50K
    ).astype(int)
    
    # Count round number payments per contract
    round_payments = payments_df.groupby('contract_id')['is_round_number'].sum().reset_index()
    round_payments.columns = ['contract_id', 'num_round_payments']
    contracts_df = contracts_df.merge(round_payments, on='contract_id', how='left')
    
    # Flag if too many round number payments
    contracts_df['excessive_round_payments'] = (
        contracts_df['num_round_payments'] >= 2
    ).astype(int)
    
    print(f"   - Contracts with excessive round payments: {contracts_df['excessive_round_payments'].sum()}")
    
    # First digit distribution (Benford's Law)
    payments_df['first_digit'] = payments_df['amount_inr'].astype(str).str[0].astype(int)
    
    # Expected Benford distribution
    benford_expected = {1: 0.301, 2: 0.176, 3: 0.125, 4: 0.097, 5: 0.079, 
                        6: 0.067, 7: 0.058, 8: 0.051, 9: 0.046}
    
    actual_distribution = payments_df['first_digit'].value_counts(normalize=True).to_dict()
    
    print(f"\n   Benford's Law Analysis:")
    print(f"   Digit | Expected | Actual | Deviation")
    print(f"   " + "-" * 45)
    for digit in range(1, 10):
        expected = benford_expected.get(digit, 0)
        actual = actual_distribution.get(digit, 0)
        deviation = abs(actual - expected)
        flag = "⚠️" if deviation > 0.05 else "✓"
        print(f"   {digit}     | {expected:.3f}    | {actual:.3f}  | {deviation:.3f} {flag}")
    
    # ========================================================================
    # FEATURE 5: PAYMENT SPLITTING DETECTION
    # ========================================================================
    print("\n5. Detecting payment splitting...")
    
    # Find multiple small payments to same vendor on same day
    vendor_contracts = contracts_df[['contract_id', 'vendor_id']].merge(
        payments_df, on='contract_id'
    )
    
    # Group by vendor and payment date
    same_day_payments = vendor_contracts.groupby(
        ['vendor_id', 'payment_date']
    ).agg({
        'contract_id': 'count',
        'amount_inr': 'sum'
    }).reset_index()
    same_day_payments.columns = ['vendor_id', 'payment_date', 'num_contracts_paid', 'total_amount']
    
    # Flag if vendor received multiple payments on same day
    suspicious_splitting = same_day_payments[
        (same_day_payments['num_contracts_paid'] >= 3) &
        (same_day_payments['total_amount'] > 900000) &
        (same_day_payments['total_amount'] < 1100000)  # Near 10 Lakh threshold
    ]
    
    print(f"   - Suspicious payment splitting patterns: {len(suspicious_splitting)}")
    
    # ========================================================================
    # FEATURE 6: PAYMENT TIMING ANOMALIES
    # ========================================================================
    print("\n6. Analyzing payment timing...")
    
    # Weekend/holiday payments
    payments_df['is_weekend_payment'] = (
        payments_df['payment_date'].dt.dayofweek >= 5
    ).astype(int)
    
    weekend_payment_contracts = payments_df[
        payments_df['is_weekend_payment'] == 1
    ]['contract_id'].unique()
    
    contracts_df['has_weekend_payments'] = contracts_df['contract_id'].isin(
        weekend_payment_contracts
    ).astype(int)
    
    print(f"   - Weekend payments detected: {payments_df['is_weekend_payment'].sum()}")
    print(f"   - Contracts with weekend payments: {contracts_df['has_weekend_payments'].sum()}")
    
    # ========================================================================
    # FEATURE 7: PAYMENT-CONTRACT AMOUNT MISMATCH
    # ========================================================================
    print("\n7. Detecting payment-contract mismatches...")
    
    # Calculate total payments per contract
    total_payments = payments_df.groupby('contract_id')['amount_inr'].sum().reset_index()
    total_payments.columns = ['contract_id', 'total_paid']
    contracts_df = contracts_df.merge(total_payments, on='contract_id', how='left')
    
    # Calculate overpayment/underpayment
    contracts_df['payment_variance_pct'] = (
        (contracts_df['total_paid'] - contracts_df['amount_inr']) / 
        contracts_df['amount_inr'] * 100
    )
    
    # Flag significant mismatches
    contracts_df['overpayment_flag'] = (
        contracts_df['payment_variance_pct'] > 5
    ).astype(int)
    
    contracts_df['underpayment_flag'] = (
        contracts_df['payment_variance_pct'] < -5
    ).astype(int)
    
    print(f"   - Overpayments detected: {contracts_df['overpayment_flag'].sum()}")
    print(f"   - Underpayments detected: {contracts_df['underpayment_flag'].sum()}")
    
    # ========================================================================
    # FEATURE 8: ADVANCE PAYMENT WITHOUT GUARANTEE
    # ========================================================================
    print("\n8. Checking advance payments without guarantees...")
    
    # Check if first payment is >50% of contract value without performance guarantee
    contracts_df['large_advance_no_guarantee'] = (
        (contracts_df['first_payment_amount'] > contracts_df['amount_inr'] * 0.5) &
        (contracts_df['performance_guarantee_pct'] == 0) &
        (contracts_df['amount_inr'] > 1000000)  # Only for contracts > 10 Lakh
    ).astype(int)
    
    print(f"   - Large advances without guarantee: {contracts_df['large_advance_no_guarantee'].sum()}")
    
    # ========================================================================
    # FEATURE 9: PAYMENT COMPOSITE RISK SCORE
    # ========================================================================
    print("\n9. Computing payment risk scores...")
    
    payment_risk_features = [
        'rapid_payment_flag',
        'has_duplicate_payments',
        'excessive_round_payments',
        'has_weekend_payments',
        'overpayment_flag',
        'large_advance_no_guarantee',
        'irregular_payment_frequency'
    ]
    
    # Calculate composite payment risk score (0-100)
    contracts_df['payment_risk_score'] = (
        contracts_df[payment_risk_features].sum(axis=1) / len(payment_risk_features) * 100
    )
    
    # Classify risk level
    contracts_df['payment_risk_level'] = pd.cut(
        contracts_df['payment_risk_score'],
        bins=[0, 20, 40, 60, 100],
        labels=['Low', 'Medium', 'High', 'Critical']
    )
    
    print(f"\n   Payment Risk Distribution:")
    print(contracts_df['payment_risk_level'].value_counts().to_string())
    
    # ========================================================================
    # SUMMARY REPORT
    # ========================================================================
    print("\n" + "=" * 80)
    print("PAYMENT FRAUD FEATURES - SUMMARY")
    print("=" * 80)
    
    high_risk_contracts = contracts_df[contracts_df['payment_risk_score'] > 40]
    
    print(f"\nTotal Contracts Analyzed: {len(contracts_df)}")
    print(f"High-Risk Payment Patterns: {len(high_risk_contracts)} ({len(high_risk_contracts)/len(contracts_df)*100:.1f}%)")
    print(f"Average Payment Risk Score: {contracts_df['payment_risk_score'].mean():.2f}")
    
    print(f"\nTop Payment Fraud Indicators:")
    for feature in payment_risk_features:
        count = contracts_df[feature].sum()
        pct = count / len(contracts_df) * 100
        print(f"  - {feature}: {count} contracts ({pct:.1f}%)")
    
    # Return enhanced dataframes
    return contracts_df, payments_df


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

# if __name__ == "__main__":
#     print("PAYMENT IRREGULARITY DETECTION MODULE")
#     print("=" * 80)
#     print("\nTo use this module with your data:")
#     # Load your data
#     contracts_df = pd.read_csv('india_contracts.csv')
#     payments_df = pd.read_csv('india_payments.csv')
    
#     # Engineer payment fraud features
#     contracts_enhanced, payments_enhanced = engineer_payment_fraud_features(
#         contracts_df, payments_df
#     )
    
#     # Save enhanced data
#     contracts_enhanced.to_csv('contracts_with_payment_features.csv', index=False)
#     payments_enhanced.to_csv('payments_enhanced.csv', index=False)
    
#     # Now use both contract AND payment features for fraud detection
#     all_features = [
#         # Original contract features
#         'amount_inr', 'num_bids', 'price_deviation_pct', 'vendor_contract_count',
#         # NEW payment features
#         'payment_risk_score', 'rapid_payment_flag', 'has_duplicate_payments',
#         'overpayment_flag', 'irregular_payment_frequency'
#     ]
    
#     X = contracts_enhanced[all_features].fillna(0)
#     # ... continue with your ML model
    
#     print("\n" + "=" * 80)
#     print("KEY PAYMENT FRAUD PATTERNS THIS MODULE DETECTS:")
#     print("=" * 80)
#     print("""
#     1. Rapid Payment Fraud: Payments made within 3 days of contract award
#     2. Duplicate Payments: Same invoice paid multiple times
#     3. Payment Splitting: Multiple small payments to avoid oversight
#     4. Round Number Fraud: Suspiciously round amounts (Benford's Law violation)
#     5. Weekend Payments: Payments processed on weekends
#     6. Overpayments: Total paid > contract value
#     7. Advance Without Guarantee: Large upfront payment without security
#     8. Irregular Frequency: Too many payments too quickly
#     """)