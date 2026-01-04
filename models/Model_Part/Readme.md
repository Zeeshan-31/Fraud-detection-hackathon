# Fraud Detection Model – Handover Guide

## Files Included
- isolation_forest_model.pkl → Trained Isolation Forest model
- feature_config.py → Frozen feature list
- rule_scoring.py → Rule-based fraud scoring logic
- ensemble_logic.py → Final risk score computation
- sample_input.csv → Example input format (optional)

## How to Use (Streamlit)
1. Load CSV data
2. Select FEATURE_COLS
3. Load model using joblib
4. Compute Isolation Forest risk
5. Compute rule-based risk
6. (Optional) Compute LOF risk on uploaded batch
7. Combine using ensemble logic
8. Label risk using thresholds

## Risk Thresholds
- High Risk: ≥ 70
- Medium Risk: 50–69
- Low Risk: < 50

## Notes
- Model flags risk, not proof of fraud
- Human audit is required for confirmation
