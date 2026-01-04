import pandas as pd
import numpy as np
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
    # Priority for Date: Tender Start > Award Date > Enquiry Start > Generic Date
    # We create a new 'clean_date' column by trying these in order
    assam['clean_date'] = assam['tender_bidOpening_date']
    
    # If Start Date is missing, try Award Date
    if 'award_date' in assam.columns:
        assam['clean_date'] = assam['clean_date'].fillna(assam['award_date'])
        
    # If still missing, try Enquiry Start
    if 'tender_enquiryPeriod_startDate' in assam.columns:
        assam['clean_date'] = assam['clean_date'].fillna(assam['tender_enquiryPeriod_startDate'])
        
    # Last resort: the 'date' column (even if it was constant, it's better than Null)
    if 'date' in assam.columns:
        assam['clean_date'] = assam['clean_date'].fillna(assam['date'])
    # Standard cleaning (duplicates & invalid amounts)
    assam = assam.drop_duplicates(subset=['tender_id'])
    assam['tender_value_amount'] = pd.to_numeric(assam['tender_value_amount'], errors='coerce')
    assam = assam[assam['tender_value_amount'] > 0]
    # Clean Himachal
    print("🧹 Cleaning Himachal data...")
    # ---------------------------------------------------------
    # 2. CLEAN HIMACHAL DATA (Applying same logic)
    # ---------------------------------------------------------
    print("Cleaning Himachal data...")
    
    # Check what date columns exist in Himachal and prioritize
    # Use underscore notation (actual column names in the CSV)
    himachal['clean_date'] = np.nan # Start empty
    
    # List of potential date columns in Himachal data (Order of preference)
    potential_hp_dates = [
        'tender_tenderPeriod_startDate', 
        'tender_awardPeriod_startDate', 
        'award_date', 
        'tender_datePublished'
    ]
    
    for col in potential_hp_dates:
        if col in himachal.columns:
            himachal['clean_date'] = himachal['clean_date'].fillna(himachal[col])

    # Standard cleaning
    himachal = himachal.drop_duplicates(subset=['ocid'])
    himachal['tender_value_amount'] = pd.to_numeric(himachal['tender_value_amount'], errors='coerce')
    himachal = himachal[himachal['tender_value_amount'] > 0]

    # ---------------------------------------------------------
    # 3. STANDARDIZE & COMBINE
    # ---------------------------------------------------------
    print("Standardizing columns...")
    
    assam_std = pd.DataFrame({
        'contract_id': assam['tender_id'],
        'pub_date': assam['clean_date'],   # <--- Uses our fixed date
        'contract_amount': assam['tender_value_amount'],
        'bidder_count': assam['tender_numberOfTenderers'],
        'dept_name': assam['buyer_name'],
        'proc_method': assam['tender_procurementMethod'],
        'data_source': 'Assam'
    })

    himachal_std = pd.DataFrame({
        'contract_id': himachal['ocid'],
        'pub_date': himachal['clean_date'], # <--- Uses our fixed date
        'contract_amount': himachal['tender_value_amount'],
        'bidder_count': himachal['tender_numberOfTenderers'],
        'dept_name': himachal['buyer_name'],
        'proc_method': himachal['tender_procurementMethod'],
        'data_source': 'Himachal Pradesh'
    })

    combined = pd.concat([assam_std, himachal_std], ignore_index=True)
    
    # Separate data by source for better date parsing
    assam_mask = combined['data_source'] == 'Assam'
    himachal_mask = combined['data_source'] == 'Himachal Pradesh'
    
    # Parse Assam dates with DD-MM-YYYY HH:MM format
    combined.loc[assam_mask, 'pub_date'] = pd.to_datetime(
        combined.loc[assam_mask, 'pub_date'], 
        format='%d-%m-%Y %H:%M', 
        errors='coerce'
    ).dt.date
    
    # Parse Himachal dates with ISO format
    combined.loc[himachal_mask, 'pub_date'] = pd.to_datetime(
        combined.loc[himachal_mask, 'pub_date'], 
        errors='coerce'
    ).dt.date
    
    # Remove rows where date could not be parsed
    print(f"Rows before date cleanup: {len(combined)}")
    combined = combined.dropna(subset=['pub_date'])
    print(f"Rows after date cleanup: {len(combined)}")

    return combined

if __name__ == "__main__":
    # Update paths to your actual file locations
    assam_path = "data/raw/assam_extracted/full/main.csv" 
    himachal_path = "data/raw/himachal_extracted/full/main.csv"
    
    df = clean_and_combine_data(assam_path, himachal_path)
    df.to_csv("data/processed/cleaned_master_data.csv", index=False)
    print("Saved to data/processed/cleaned_master_data.csv")