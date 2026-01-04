def compute_final_risk(if_risk, lof_risk, rule_risk):
    return (
        0.5 * if_risk +
        0.2 * lof_risk +
        0.3 * rule_risk
    )


def risk_label(score):
    if score >= 70:
        return "High Risk"
    elif score >= 50:
        return "Medium Risk"
    else:
        return "Low Risk"
