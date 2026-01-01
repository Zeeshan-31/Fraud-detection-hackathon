import pandas as pd
import numpy as np
from scipy import stats

def engineer_fraud_features(df):
    """
    Create fraud detection features

    Args:
        df: Preprocessed DataFrame

    Returns:
        DataFrame: With engineered features
    """

    print("🔨 Engineering fraud detection features...")

    # Ensure date is datetime
    df['pub_date'] = pd.to_datetime(df['pub_date'], errors='coerce')

    # Extract date components
    df['tender_month'] = df['pub_date'].dt.month
    df['day_of_week'] = df['pub_date'].dt.dayofweek

    # COMPETITION FEATURES
    df['single_bidder_flag'] = (df['bidder_count'] == 1).astype(int)
    df['weak_competition'] = (df['bidder_count'] < 3).astype(int)
    df['competition_score'] = (df['bidder_count'].clip(upper=10) / 10 * 100)

    # PRICE FEATURES
    dept_avg = df.groupby('dept_name')['contract_amount'].transform('mean')
    df['dept_avg_amount'] = dept_avg
    df['price_vs_dept_avg'] = ((df['contract_amount'] - dept_avg) / dept_avg * 100)
    df['extreme_high_price'] = (df['price_vs_dept_avg'] > 100).astype(int)
    df['round_amount_flag'] = (df['contract_amount'] % 100000 == 0).astype(int)
    df['threshold_game'] = (
        ((df['contract_amount'] >= 950000) & (df['contract_amount'] < 1000000)) |
        ((df['contract_amount'] >= 2400000) & (df['contract_amount'] < 2500000))
    ).astype(int)

    # TIMING FEATURES
    df['dec_rush'] = (df['tender_month'] == 12).astype(int)
    df['march_rush'] = (df['tender_month'] == 3).astype(int)
    df['weekend_award'] = (df['day_of_week'] >= 5).astype(int)

    # DEPARTMENT FEATURES
    dept_counts = df.groupby('dept_name').size()
    df['dept_tender_volume'] = df['dept_name'].map(dept_counts)

    dept_single = df[df['single_bidder_flag']==1].groupby('dept_name').size()
    dept_single_rate = (dept_single / dept_counts * 100).fillna(0)
    df['dept_single_bid_rate'] = df['dept_name'].map(dept_single_rate)

    # COMPOSITE RISK SCORE
    df['fraud_risk_score'] = (
        df['single_bidder_flag'] * 30 +
        df['extreme_high_price'] * 25 +
        (df['dec_rush'] | df['march_rush']) * 20 +
        df['round_amount_flag'] * 15 +
        df['threshold_game'] * 10
    ).clip(0, 100)

    print(f"✅ Created{len([c for c in df.columns if c not in ['contract_id', 'pub_date', 'contract_amount', 'bidder_count', 'dept_name', 'proc_method', 'data_source']])} features")

    return df


if __name__ == "__main__":
    # Test
    df = pd.read_csv('data/processed/preprocessed_data.csv')
    df = engineer_fraud_features(df)
    df.to_csv('data/processed/data_with_features.csv', index=False)
    print("💾 Saved to data/processed/data_with_features.csv")