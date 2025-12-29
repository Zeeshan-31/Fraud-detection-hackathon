import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import json

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

print("=" * 80)
print("INDIA GOVERNMENT PROCUREMENT FRAUD DETECTION DATASET GENERATOR")
print("=" * 80)

# Configuration
NUM_CONTRACTS = 2000
FRAUD_RATE = 0.10  # 10% fraudulent

# India-specific data
INDIAN_STATES = [
    'Maharashtra', 'Delhi', 'Karnataka', 'Tamil Nadu', 'Uttar Pradesh',
    'Gujarat', 'West Bengal', 'Rajasthan', 'Madhya Pradesh', 'Punjab',
    'Haryana', 'Kerala', 'Telangana', 'Bihar', 'Odisha'
]

INDIAN_CITIES = {
    'Maharashtra': ['Mumbai', 'Pune', 'Nagpur'],
    'Delhi': ['New Delhi', 'Delhi'],
    'Karnataka': ['Bangalore', 'Mysore'],
    'Tamil Nadu': ['Chennai', 'Coimbatore'],
    'Uttar Pradesh': ['Lucknow', 'Kanpur', 'Noida'],
    'Gujarat': ['Ahmedabad', 'Surat'],
    'West Bengal': ['Kolkata'],
    'Rajasthan': ['Jaipur', 'Udaipur'],
    'Madhya Pradesh': ['Bhopal', 'Indore'],
    'Punjab': ['Chandigarh', 'Ludhiana'],
    'Haryana': ['Gurgaon', 'Faridabad'],
    'Kerala': ['Thiruvananthapuram', 'Kochi'],
    'Telangana': ['Hyderabad'],
    'Bihar': ['Patna'],
    'Odisha': ['Bhubaneswar']
}

MINISTRIES = [
    'Ministry of Health', 'Ministry of Education', 'Ministry of Defence',
    'Ministry of Railways', 'Ministry of Road Transport', 'Ministry of Agriculture',
    'Ministry of Power', 'Ministry of Communications', 'Ministry of Rural Development',
    'Ministry of Urban Development', 'State PWD', 'State Health Department',
    'Municipal Corporation', 'State Education Board'
]

# Indian procurement categories with realistic INR pricing
CATEGORIES = {
    'Medical Equipment': {'avg': 2500000, 'std': 750000},  # ₹25 Lakh
    'IT Hardware': {'avg': 1500000, 'std': 450000},  # ₹15 Lakh
    'Software Development': {'avg': 3000000, 'std': 900000},  # ₹30 Lakh
    'Construction': {'avg': 8000000, 'std': 2500000},  # ₹80 Lakh
    'Road Development': {'avg': 12000000, 'std': 4000000},  # ₹1.2 Cr
    'School Furniture': {'avg': 500000, 'std': 150000},  # ₹5 Lakh
    'Office Supplies': {'avg': 200000, 'std': 60000},  # ₹2 Lakh
    'Vehicle Purchase': {'avg': 1800000, 'std': 500000},  # ₹18 Lakh
    'Consulting Services': {'avg': 2000000, 'std': 600000},  # ₹20 Lakh
    'Building Maintenance': {'avg': 1000000, 'std': 300000}  # ₹10 Lakh
}

PROCEDURE_TYPES = ['Open Tender', 'Limited Tender', 'Single Source', 'Two Stage Bidding', 'E-Procurement']
BUSINESS_TYPES = ['Private Limited', 'Public Limited', 'Partnership', 'Proprietorship', 'LLP']

# Common Indian company name patterns
COMPANY_PREFIXES = ['Bharat', 'Indian', 'National', 'Supreme', 'United', 'Global', 'Modern', 'New', 'Star', 'Excel']
COMPANY_SUFFIXES = ['Enterprises', 'Industries', 'Solutions', 'Technologies', 'Services', 'Corporation', 'Systems', 'Traders', 'Suppliers', 'Constructions']

# Generate vendors
num_vendors = 300
vendors_data = []

for i in range(num_vendors):
    vendor_id = f"VEN{str(i+1).zfill(5)}"
    vendor_name = f"{random.choice(COMPANY_PREFIXES)} {random.choice(COMPANY_SUFFIXES)}"
    if random.random() < 0.3:  # 30% add "Pvt Ltd"
        vendor_name += " Pvt Ltd"
    
    reg_date = datetime(2015, 1, 1) + timedelta(days=random.randint(0, 2500))
    
    state = random.choice(INDIAN_STATES)
    city = random.choice(INDIAN_CITIES[state])
    
    # Address
    address = f"{random.randint(1, 999)}- {random.choice(['Main Road', 'MG Road', 'Ring Road', 'Industrial Area', 'Sector ' + str(random.randint(1, 50))])}"
    
    pincode = random.randint(100000, 999999)
    biz_type = random.choice(BUSINESS_TYPES)
    employees = random.choice([5, 10, 25, 50, 100, 200, 500, 1000])
    
    # GST number (realistic format)
    gst_state_code = f"{random.randint(1, 36):02d}"
    gst_number = f"{gst_state_code}{random.choice(['A', 'B', 'C'])}{random.randint(1000000000, 9999999999)}{random.randint(1, 9)}Z{random.choice(['A', 'B', 'C'])}"
    
    blacklisted = 'No'
    
    vendors_data.append([
        vendor_id, vendor_name, reg_date, address, city, state, pincode,
        biz_type, employees, gst_number, blacklisted
    ])

vendors_df = pd.DataFrame(vendors_data, columns=[
    'vendor_id', 'vendor_name', 'registration_date', 'address', 'city', 
    'state', 'pincode', 'business_type', 'employees', 'gst_number', 'blacklisted'
])

# Create suspicious vendors (shell companies)
suspicious_vendors = random.sample(list(vendors_df['vendor_id']), 20)
shell_address = "123- Fake Complex-Industrial Area"
shell_gst_prefix = "27A"  # Maharashtra

for i in range(7):
    idx = vendors_df[vendors_df['vendor_id'] == suspicious_vendors[i]].index[0]
    vendors_df.loc[idx, 'address'] = shell_address
    vendors_df.loc[idx, 'city'] = 'Mumbai'
    vendors_df.loc[idx, 'state'] = 'Maharashtra'
    vendors_df.loc[idx, 'employees'] = 1
    vendors_df.loc[idx, 'gst_number'] = f"{shell_gst_prefix}{random.randint(1000000000, 9999999999)}{random.randint(1, 9)}ZA"

# Generate contracts
contracts_data = []
fraud_labels = []
fraud_reasons = []

start_date = datetime(2022, 1, 1)

for i in range(NUM_CONTRACTS):
    contract_id = f"GEM/2024/{random.randint(100000, 999999)}"  # GeM portal format
    tender_number = f"TN-{random.randint(1000, 9999)}-{random.randint(2022, 2024)}"
    
    award_date = start_date + timedelta(days=random.randint(0, 800))
    
    # Determine fraud
    is_fraud = random.random() < FRAUD_RATE
    fraud_reason = []
    
    # Select vendor
    if is_fraud and random.random() < 0.35:  # Shell company
        vendor_id = random.choice(suspicious_vendors[:7])
        fraud_reason.append("shell_company")
    else:
        vendor_id = random.choice(vendors_df['vendor_id'].tolist())
    
    vendor_row = vendors_df[vendors_df['vendor_id'] == vendor_id].iloc[0]
    vendor_name = vendor_row['vendor_name']
    vendor_state = vendor_row['state']
    
    ministry = random.choice(MINISTRIES)
    category = random.choice(list(CATEGORIES.keys()))
    
    # Generate amount
    base_amount = np.random.normal(CATEGORIES[category]['avg'], CATEGORIES[category]['std'])
    base_amount = max(50000, base_amount)  # Minimum ₹50K
    
    # Fraud: Inflated pricing
    if is_fraud and random.random() < 0.4:
        amount = base_amount * random.uniform(2.8, 4.5)
        fraud_reason.append("inflated_price")
    else:
        amount = base_amount
    
    amount = round(amount, 2)
    
    # Fraud: Just below oversight threshold (₹10 Lakh)
    if is_fraud and random.random() < 0.25:
        amount = 995000.00  # Just under ₹10L
        fraud_reason.append("threshold_avoidance")
    
    # Procurement procedure
    if is_fraud and random.random() < 0.45:
        procedure_type = 'Single Source'
        num_bids = 1
        fraud_reason.append("non_competitive")
    else:
        procedure_type = random.choice(PROCEDURE_TYPES)
        if procedure_type == 'Single Source':
            num_bids = 1
        else:
            num_bids = random.randint(2, 12)
    
    # Advertisement period (days)
    if is_fraud and random.random() < 0.3:
        ad_period = random.randint(1, 3)  # Too short
        fraud_reason.append("short_advertisement")
    else:
        ad_period = random.randint(7, 30)
    
    publication_date = award_date - timedelta(days=ad_period + random.randint(5, 20))
    
    # Contract duration
    contract_duration = random.choice([30, 60, 90, 180, 365])
    
    # Fraud: Weekend award
    if is_fraud and random.random() < 0.15:
        award_date = award_date + timedelta(days=(5 - award_date.weekday()))
        fraud_reason.append("weekend_award")
    
    completion_date = award_date + timedelta(days=contract_duration)
    if random.random() < 0.25:
        completion_date = None
    
    officer_id = f"OFF{random.randint(1, 35):03d}"
    
    # Fraud: Corrupt officer pattern
    if is_fraud and random.random() < 0.25:
        officer_id = "OFF007"  # Suspicious officer
        fraud_reason.append("suspicious_officer")
    
    # Payment terms
    payment_terms = random.choice(['100% Advance', '50-50', '30-70', 'Milestone Based', 'On Completion'])
    
    # Performance guarantee
    performance_guarantee = random.choice([0, 5, 10]) if amount > 1000000 else 0
    
    # Geographic anomaly - vendor from different state winning local contract
    if is_fraud and random.random() < 0.2:
        if 'Municipal' in ministry or 'State' in ministry:
            # Vendor from different state winning local contract
            ministry_state = random.choice(INDIAN_STATES)
            if vendor_state != ministry_state:
                fraud_reason.append("geographic_anomaly")
    
    contracts_data.append([
        contract_id, tender_number, publication_date, award_date, vendor_id, 
        vendor_name, amount, ministry, category, procedure_type, num_bids,
        ad_period, contract_duration, completion_date, officer_id,
        payment_terms, performance_guarantee
    ])
    
    fraud_labels.append(1 if is_fraud else 0)
    fraud_reasons.append("; ".join(fraud_reason) if fraud_reason else "legitimate")

contracts_df = pd.DataFrame(contracts_data, columns=[
    'contract_id', 'tender_number', 'publication_date', 'award_date', 'vendor_id',
    'vendor_name', 'amount_inr', 'ministry', 'category', 'procedure_type', 
    'num_bids', 'advertisement_days', 'contract_duration_days', 'completion_date',
    'officer_id', 'payment_terms', 'performance_guarantee_pct'
])

contracts_df['is_fraud'] = fraud_labels
contracts_df['fraud_reason'] = fraud_reasons

# Generate payments with Indian banking details
payments_data = []
payment_counter = 1

for _, contract in contracts_df.iterrows():
    # Number of payments based on payment terms
    if contract['payment_terms'] == '100% Advance':
        num_payments = 1
    elif contract['payment_terms'] in ['50-50', '30-70']:
        num_payments = 2
    else:
        num_payments = random.randint(2, 5)
    
    payment_amount = contract['amount_inr'] / num_payments
    
    for j in range(num_payments):
        days_offset = random.randint(10, 45) * (j + 1)
        payment_date = contract['award_date'] + timedelta(days=days_offset)
        
        payment_id = f"PAY-{payment_counter:06d}"
        invoice_num = f"INV/{contract['award_date'].year}/{payment_counter:05d}"
        
        # UTR number (realistic Indian format)
        utr_number = f"UTR{random.randint(100000000000, 999999999999)}"
        
        payment_method = random.choice(['RTGS', 'NEFT', 'Cheque'])
        approver_id = f"APP{random.randint(1, 20):03d}"
        
        # Fraud: Rapid payment
        if contract['is_fraud'] == 1 and random.random() < 0.3:
            payment_date = contract['award_date'] + timedelta(days=random.randint(1, 3))
        
        payments_data.append([
            payment_id, contract['contract_id'], payment_date, 
            round(payment_amount, 2), invoice_num, utr_number,
            payment_method, approver_id
        ])
        payment_counter += 1

payments_df = pd.DataFrame(payments_data, columns=[
    'payment_id', 'contract_id', 'payment_date', 'amount_inr',
    'invoice_number', 'utr_number', 'payment_method', 'approver_id'
])

# Market reference prices (India-specific)
market_prices_df = pd.DataFrame([
    ['Medical Equipment', 'X-Ray Machine', 2500000, 750000],
    ['Medical Equipment', 'Hospital Beds', 150000, 40000],
    ['IT Hardware', 'Laptops', 50000, 10000],
    ['IT Hardware', 'Servers', 500000, 150000],
    ['Software Development', 'Web Portal', 3000000, 900000],
    ['Construction', 'School Building', 8000000, 2500000],
    ['Road Development', 'Per KM', 12000000, 4000000],
    ['School Furniture', 'Desks & Chairs', 500000, 150000],
    ['Office Supplies', 'Stationery', 200000, 60000],
    ['Vehicle Purchase', 'Cars', 1800000, 500000]
], columns=['category', 'subcategory', 'avg_price_inr', 'std_dev'])

# Display summary
print(f"\n{'='*80}")
print("DATASET SUMMARY")
print("="*80)
print(f"Total Contracts: {len(contracts_df)}")
print(f"Fraudulent Contracts: {contracts_df['is_fraud'].sum()} ({contracts_df['is_fraud'].mean()*100:.1f}%)")
print(f"Total Vendors: {len(vendors_df)}")
print(f"Total Payments: {len(payments_df)}")
print(f"Date Range: {contracts_df['award_date'].min().date()} to {contracts_df['award_date'].max().date()}")
print(f"Total Value: ₹{contracts_df['amount_inr'].sum()/10000000:.2f} Crores")

print(f"\n{'='*80}")
print("FRAUD PATTERNS DETECTED")
print("="*80)
fraud_counts = contracts_df[contracts_df['is_fraud']==1]['fraud_reason'].value_counts()
for reason, count in fraud_counts.head(10).items():
    print(f"  {reason}: {count} cases")

print(f"\n{'='*80}")
print("STATE-WISE CONTRACT DISTRIBUTION (Top 10)")
print("="*80)
state_contracts = vendors_df.merge(
    contracts_df[['vendor_id', 'amount_inr']], on='vendor_id'
).groupby('state')['amount_inr'].agg(['count', 'sum'])
state_contracts['sum'] = state_contracts['sum'] / 10000000  # Convert to Crores
print(state_contracts.sort_values('count', ascending=False).head(10).to_string())

print(f"\n{'='*80}")
print("TOP SUSPICIOUS CONTRACTS")
print("="*80)
suspicious = contracts_df[contracts_df['is_fraud']==1].nlargest(5, 'amount_inr')
print(suspicious[['contract_id', 'vendor_name', 'amount_inr', 'procedure_type', 'fraud_reason']].to_string(index=False))

print(f"\n{'='*80}")
print("SHELL COMPANY NETWORK")
print("="*80)
print(f"Suspicious Address: {shell_address}")
shell_vendors = vendors_df[vendors_df['address'] == shell_address]
print(f"Number of vendors: {len(shell_vendors)}")
print(shell_vendors[['vendor_id', 'vendor_name', 'gst_number', 'employees']].to_string(index=False))

print(f"\n{'='*80}")
print("EXPORT TO CSV")
print("="*80)

#To save these datasets, add these lines:

contracts_df.to_csv('india_contracts.csv', index=False)
vendors_df.to_csv('india_vendors.csv', index=False)
payments_df.to_csv('india_payments.csv', index=False)
market_prices_df.to_csv('india_market_prices.csv', index=False)

# Remove fraud labels for ML training (simulate real scenario)
#contracts_df_clean = contracts_df.drop(['is_fraud', 'fraud_reason'], axis=1)
#contracts_df_clean.to_csv('india_contracts_unlabeled.csv', index=False)

# Keep labels separately for validation
#labels_df = contracts_df[['contract_id', 'is_fraud', 'fraud_reason']]
#labels_df.to_csv('india_fraud_labels.csv', index=False)
