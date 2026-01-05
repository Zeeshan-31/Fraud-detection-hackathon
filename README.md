# 🔍 Fraud Detection System - Advanced Tender Analysis Platform
A sophisticated machine learning-powered fraud detection system for government procurement tenders, featuring dual-model architecture, AI-powered explanations, and an interactive dashboard with real-time analytics.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.29-red.svg)](https://streamlit.io)


## 🎯 Problem Statement
How can machine learning systems detect fraud, irregularities, and anomalies in government spending, procurement, welfare delivery, and contracts?
Government procurement fraud costs billions annually. Manual audits are:
- ⏰ Time-consuming (months to review thousands of tenders)
- 💰 Expensive (requires large audit teams)
- 🎯 Inefficient (random sampling misses systematic fraud)

## 💡 Our Solution

An AI-powered system that:
1. ✅ Analyzes thousands of procurement tenders in seconds
2. 🚨 Flags high-risk contracts using 15+ fraud indicators
3. 🤖 Explains suspicious patterns using Gemini AI
4. 📊 Provides interactive dashboard for audit officers

---

## 🏗️ System Architecture

```

Upload CSV → Column Mapping → Feature Engineering → ML Model → Risk Scoring → Gemini Analysis → Results Dashboard

```

**Tech Stack:**
- **ML:** Scikit-learn (Isolation Forest)
- **NLP:** Google Gemini 2.0 Flash
- **Frontend:** Streamlit
- **Data:** 38,000+ real government tenders (Assam + Himachal Pradesh)

---
## 📊 Dataset

- **Source:** Assam Government eProcurement + Himachal Pradesh Civic Data Lab
- **Size:** 38,025 procurement tenders (2016-2024)
- **Columns:** Date, Department, Vendor, Amount, Bidders, Procurement Method, etc.

---

## 🚀 Quick Start

```


# Clone repository

git clone https://github.com/Zeeshan-31/fraud-detection-hackathon.git
cd fraud-detection-india

# Install dependencies

cd fraud-detection-hackathon
pip install -r requirements.txt

# Run dashboard (after development)

streamlit run dashboard/app.py

```

Open browser: `http://localhost:8501`

---

## 📁 Project Structure

```

├── data/               \# Data files (not in repo)
├── src/                \# Source code
│   ├── data_processing/
│   ├── models/
│   └── gemini_integration/
├── dashboard/          \# Streamlit app
├── models/             \# Trained ML models
├── notebooks/          \# Jupyter notebooks
└── docs/               \# Documentation

```

---
## 🎯 Features

### Fraud Detection Indicators

**Persistent File State Management:** No re-upload needed between page switches - maintains session state
- **Smart Column Mapping:** Automatically handles 30+ different CSV format variations and column naming conventions
- **Dynamic Risk Threshold Adjustment:** Flexible risk threshold slider (50-90%) for customized sensitivity
- **Comprehensive Data Overview:** 
  - 4 metric cards displaying total tenders, risk distribution, and total amounts
  - At-a-glance summary of your dataset's health
- **Visual Analytics:** 
  - Interactive pie charts for risk distribution
  - Bar charts showing risk categories breakdown
  - Scatter plots comparing Rule-based vs AI-based risk assessments
- **High-Risk Tender Filtering:** 
  - Filter by risk level (High, Medium, Low)
  - Detection source labels (Policy Violation, AI Anomaly, or Critical)
  - Easy identification of "why" each tender was flagged
- **Export Capabilities:** Full comprehensive, High-risk, Medium risk and Executive summary reports
- **Responsive Design:** Gradient cards, pill-shaped navigation, and modern UI/UX

### 2. **Dual-Model ML Architecture**

#### Rule-Based System
- **15+ Fraud Indicators** across multiple categories:
  - **Competition Risks:** Single bidder scenarios, low bidder participation
  - **Pricing Anomalies:** Unusual price-per-day calculations, outlier amounts
  - **Timing Red Flags:** Weekend publications, year-end rush, Q4 clustering
  - **Procurement Method Irregularities:** Direct procurement patterns, limited tender abuse
  - Scores on a 0-100 scale based on severity

#### AI-Based System
- **Pre-trained Isolation Forest Model:** Detects hidden statistical anomalies
- **20 Engineered Features:**
  - Bidder competition metrics
  - Z-score pricing analysis
  - Timeline patterns and seasonality
  - Department statistics and historical behavior
  - Price-to-duration ratios
- **Top 2% Anomaly Detection:** Focuses on the most suspicious outliers
- **Model Artifacts:** Saved with scaler and imputer for consistent predictions

#### Smart Fusion Logic
- **Hybrid Detection:** Flags tenders if EITHER system detects risk
- **Dual Scoring:** Shows both Rule-based (0-100) and ML anomaly scores
- **Detection Source Tracking:** Labels indicate which system triggered the alert
- **"Hidden Risk" Zone:** Highlights tenders that appear compliant by rules but are flagged by AI

### 3. **Gemini AI Integration**

- **Real-time Fraud Explanation Generation:** Powered by Google Gemini 2.5 Flash
- **Streaming Responses:** Better user experience with progressive loading
- **Context-Aware Analysis:** Identifies which specific fraud flags were triggered
- **Plain English Explanations:** Designed for audit officers without technical background
- **Interactive Tender Selection:** Click any tender for instant AI-powered analysis
- **Risk Assessment Breakdown:** Explains both rule-based and ML-detected anomalies


---
## 📖 Usage

### For Government Officers

1. Export tender data from eProcurement system (CSV format)
2. Upload to dashboard
3. Review high-risk tenders (risk score > 70%)
4. Download investigation report

### Required CSV Columns

Minimum required (flexible names):
- `id` / `tender_id`
- `date` / `publish_date`
- `department` / `buyer_name`
- `amount` / `tender_value`
- `description` / `tender_title`

---
## 🙏 Acknowledgments

- Data: Assam Government eProcurement Portal
- Data: Himachal Pradesh Civic Data Lab
- AI: Google Gemini API


## 🔗 Links
- [Presentation Slides](https://1drv.ms/p/c/01d9fb438aa7c576/IQDVb3MjE7mKTbwXksjIt9PrARswBOgbBzbx4_wWsT68cDg?e=1Vogx7)
- [Demo Video](https://drive.google.com/file/d/1VMnUclatpGH5zmO5rm2esegDqxu4oJgj/view)
- [Documentation](docs/)

---
**Built for Hack4Delhi| Jan 2025**
