import pandas as pd
import joblib
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

df = pd.read_csv(r"C:\Users\mishr\Downloads\data_with_features.csv")

def rule_risk(row):
    score = 0

    if row["single_bidder_flag"] == 1:
        score += 30

    if row["extreme_high_price"] == 1:
        score += 25

    if row["dec_rush"] == 1 or row["march_rush"] == 1:
        score += 20

    if row["round_amount_flag"] == 1:
        score += 15

    if row["threshold_game"] == 1:
        score += 10

    return score

df["rule_risk_score"] = df.apply(rule_risk, axis=1)
