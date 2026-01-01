import pandas as pd
import os

def clean_and_combine_data(assam_path, himachal_path):
    """
    Clean and combine both state datasets

    Args:
        assam_path: Path to Assam CSV
        himachal_path: Path to Himachal CSV

    Returns:
        DataFrame: Combined and cleaned data
    """

    # Load data
    print("📥 Loading data...")
    assam = pd.read_csv(assam_path)
    himachal = pd.read_csv(himachal_path)

    # Clean Assam
    print("🧹 Cleaning Assam data...")
    assam = assam.drop_duplicates(subset=['tender_id'])
    assam = assam[assam['tender_value_amount'].notna()]
    assam['tender_value_amount'] = pd.to_numeric(assam['tender_value_amount'], errors='coerce')
    assam = assam[assam['tender_value_amount'] > 0]

    # Clean Himachal
    print("🧹 Cleaning Himachal data...")
    himachal = himachal.drop_duplicates(subset=['ocid'])
    himachal = himachal[himachal['tender_value_amount'].notna()]
    himachal['tender_value_amount'] = pd.to_numeric(himachal['tender_value_amount'], errors='coerce')
    himachal = himachal[himachal['tender_value_amount'] > 0]

    # Standardize columns
    print("🔄 Standardizing columns...")
    assam_std = pd.DataFrame({
        'contract_id': assam['tender_id'],
        'pub_date': assam['date'],
        'contract_amount': assam['tender_value_amount'],
        'bidder_count': assam['tender_numberOfTenderers'],
        'dept_name': assam['buyer_name'],
        'proc_method': assam['tender_procurementMethod'],
        'data_source': 'Assam'
    })

    himachal_std = pd.DataFrame({
        'contract_id': himachal['ocid'],
        'pub_date': himachal['tender_datePublished'],
        'contract_amount': himachal['tender_value_amount'],
        'bidder_count': himachal['tender_numberOfTenderers'],
        'dept_name': himachal['buyer_name'],
        'proc_method': himachal['tender_procurementMethod'],
        'data_source': 'Himachal Pradesh'
    })

    # Combine
    combined = pd.concat([assam_std, himachal_std], ignore_index=True)

    print(f"✅ Combined{len(combined):,} records")
    return combined


if __name__ == "__main__":
    # Test the function
    assam_path = "data/raw/assam_extracted/full/main.csv"
    himachal_path = "data/raw/himachal_extracted/full/main.csv"

    df = clean_and_combine_data(assam_path, himachal_path)
    df.to_csv('data/processed/cleaned_master_data.csv', index=False)
    print("💾 Saved to data/processed/cleaned_master_data.csv")