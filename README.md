# Fraud-detection-hackathon
AI-powered fraud detection system for government procurement
Government procurement fraud detection using Machine Learning

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

1. **Competition Red Flags:** Single bidder, low competition
2. **Amount Red Flags:** Price inflation, round numbers
3. **Timing Red Flags:** Year-end rush, weekend submissions
4. **Process Red Flags:** Emergency procurement abuse
5. **Vendor Red Flags:** Repeat winners, new vendors

### Model Performance

- **Algorithm:** Isolation Forest (unsupervised anomaly detection)
- **Training Data:** 38,025 tenders
- **Features:** 15 engineered fraud indicators
- **Output:** Risk score 0-100% per tender

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
- [Demo Video](link-to-video)
- [Documentation](docs/)

---
**Built for Hack4Delhi| Jan 2025**
