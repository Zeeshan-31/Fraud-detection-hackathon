"""
Dashboard tab component for the dashboard.
Displays fraud analysis results and charts.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
import os

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import (
    generate_risk_scores,
    classify_risk_levels,
    calculate_risk_metrics,
    export_analysis_summary,
)

# Import Gemini Client
try:
    from src.gemini_integration.client import GeminiClient
except ImportError:
    # Fallback if run from different cwd
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from src.gemini_integration.client import GeminiClient


def render_metric_cards(metrics):
    """
    Render the four metric cards (Total, High Risk, Medium Risk, Low Risk).
    
    Args:
        metrics: Dictionary with risk metrics
    """
    col1, col2, col3, col4 = st.columns(4)
    
    # Card 1: Total Analyzed (Blue)
    with col1:
        st.markdown(f"""
        <div class="metric-card-blue">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">📊</div>
            <p class="metric-value">{metrics['total_tenders']:,}</p>
            <p style="font-size: 0.9rem; opacity: 0.9; margin-top: 0.5rem;">Total Tenders Analyzed</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Card 2: High Risk (Red)
    with col2:
        st.markdown(f"""
        <div class="metric-card-red">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">⚠️</div>
            <p class="metric-value">{metrics['high_risk_pct']:.1f}%</p>
            <p style="font-size: 0.9rem; opacity: 0.9; margin-top: 0.5rem;">High Risk ({metrics['high_risk_count']:,} tenders)</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Card 3: Medium Risk (Orange)
    with col3:
        st.markdown(f"""
        <div class="metric-card-orange">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">📈</div>
            <p class="metric-value">{metrics['medium_risk_pct']:.1f}%</p>
            <p style="font-size: 0.9rem; opacity: 0.9; margin-top: 0.5rem;">Medium Risk ({metrics['medium_risk_count']:,} tenders)</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Card 4: Low Risk (Green)
    with col4:
        st.markdown(f"""
        <div class="metric-card-green">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">✅</div>
            <p class="metric-value">{metrics['low_risk_pct']:.1f}%</p>
            <p style="font-size: 0.9rem; opacity: 0.9; margin-top: 0.5rem;">Low Risk ({metrics['low_risk_count']:,} tenders)</p>
        </div>
        """, unsafe_allow_html=True)


def render_risk_distribution_chart(df, metrics):
    """
    Render pie chart showing risk distribution.
    
    Args:
        df: DataFrame with analysis data
        metrics: Risk metrics
    """
    st.markdown("#### Risk Distribution")
    
    risk_data = pd.DataFrame({
        'Risk Level': ['High Risk', 'Medium Risk', 'Low Risk'],
        'Count': [metrics['high_risk_count'], metrics['medium_risk_count'], metrics['low_risk_count']]
    })
    
    fig_pie = px.pie(
        risk_data,
        values='Count',
        names='Risk Level',
        color='Risk Level',
        color_discrete_map={
            'High Risk': '#e74c3c',
            'Medium Risk': '#f39c12',
            'Low Risk': '#2ecc71'
        },
        hole=0.4
    )
    
    fig_pie.update_traces(
        textposition='inside',
        textinfo='percent+label',
        textfont_size=12,
        marker=dict(line=dict(color='#ffffff', width=2))
    )
    
    fig_pie.update_layout(
        showlegend=True,
        height=350,
        margin=dict(t=10, b=10, l=10, r=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#111827')
    )
    
    st.plotly_chart(fig_pie, use_container_width=True)


def render_risk_score_chart(df):
    """
    Render bar chart showing risk score distribution.
    
    Args:
        df: DataFrame with risk scores
    """
    st.markdown("#### Risk Score Distribution")
    
    score_ranges = pd.cut(
        df['risk_score'], 
        bins=[0, 20, 40, 60, 80, 100], 
        labels=['0-20', '21-40', '41-60', '61-80', '81-100']
    )
    range_counts = score_ranges.value_counts().sort_index()
    
    fig_bar = go.Figure(data=[
        go.Bar(
            x=range_counts.index.astype(str),
            y=range_counts.values,
            marker_color='#1f77b4',
            text=range_counts.values,
            textposition='auto',
            name='Number of Tenders'
        )
    ])
    
    fig_bar.update_layout(
        xaxis_title="Risk Score Range",
        yaxis_title="Count",
        height=350,
        margin=dict(t=10, b=10, l=10, r=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#111827'),
        showlegend=False
    )
    
    fig_bar.update_xaxes(showgrid=False)
    fig_bar.update_yaxes(showgrid=True, gridcolor='#e5e7eb')
    
    st.plotly_chart(fig_bar, use_container_width=True)


def render_high_risk_table(df):
    """
    Render table of high-risk tenders with statistics.
    Includes both Rule-Based High Risk and Top AI Anomalies (Hidden Risks).
    
    Args:
        df: DataFrame with risk levels
    """
    st.markdown('<p class="section-header">⚠️ High-Risk Tenders Requiring Review</p>', unsafe_allow_html=True)
    
    # --- Smart Filtering Logic ---
    # 1. Rule-Based High Risk (Score >= 70)
    rule_mask = df['risk_level'] == 'High'
    
    # 2. AI Hidden Risk (Top 2% Anomalies)
    # We use a strict 98th percentile to ensure we only flag "Genuine Anomalies" 
    # and avoid overwhelming the officer with false positives.
    if 'ml_risk_score' in df.columns:
        ml_threshold = df['ml_risk_score'].quantile(0.98)
        ai_mask = df['ml_risk_score'] > ml_threshold
    else:
        ai_mask = pd.Series(False, index=df.index)
        ml_threshold = 0
        
    # Combine: Show if EITHER system flags it
    high_risk_df = df[rule_mask | ai_mask].copy()
    
    # Add "Detection Source" to explain WHY it's here
    def get_source(row):
        # We check the RAW risk_score for Policy Violations (>= 70)
        # We check the RAW ml_risk_score for AI Anomalies (> threshold)
        # Note: row['risk_level'] might have been upgraded to 'High' by the dashboard logic,
        # so we cannot rely on it to distinguish between Rule vs AI.
        
        is_rule = row['risk_score'] >= 70
        is_ai = 'ml_risk_score' in row and row['ml_risk_score'] > ml_threshold
        
        if is_rule and is_ai: return "🚨 Critical (Both)"
        if is_rule: return "📜 Policy Violation"
        if is_ai: return "🤖 AI Anomaly"
        return "Unknown"

    if len(high_risk_df) > 0:
        if 'ml_risk_score' in high_risk_df.columns:
            high_risk_df['Detection Source'] = high_risk_df.apply(get_source, axis=1)
            
            # Reorder columns to put Detection Source first
            cols = list(high_risk_df.columns)
            cols.insert(0, cols.pop(cols.index('Detection Source')))
            high_risk_df = high_risk_df[cols]
            
        # Sort: Critical first, then by Risk Score
        high_risk_df = high_risk_df.sort_values(['risk_score', 'ml_risk_score'], ascending=[False, False])

        # Red header bar
        st.markdown(f"""
        <div style="background-color: #e74c3c; color: white; padding: 1rem 1.5rem; 
                    border-radius: 0.5rem 0.5rem 0 0; display: flex; 
                    align-items: center; justify-content: space-between; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span style="font-size: 1.25rem;">⚠️</span>
                <span style="font-weight: 600; font-size: 1rem;">High-Risk Tenders Requiring Review</span>
            </div>
            <span style="background-color: white; color: #e74c3c; padding: 0.25rem 0.75rem; 
                         border-radius: 1rem; font-weight: 600; font-size: 0.9rem;">{len(high_risk_df)} Items</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Display table
        st.dataframe(
            high_risk_df.head(50), # Show top 50 max
            use_container_width=True,
            hide_index=True,
            height=400
        )
        
        # Statistics
        with st.expander("📊 High-Risk Statistics"):
            stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
            with stat_col1:
                st.metric("Total Flagged", len(high_risk_df))
            with stat_col2:
                rule_count = sum(high_risk_df['Detection Source'].str.contains('Policy'))
                st.metric("Policy Violations", rule_count)
            with stat_col3:
                ai_count = sum(high_risk_df['Detection Source'].str.contains('AI'))
                st.metric("Hidden AI Risks", ai_count)
            with stat_col4:
                crit_count = sum(high_risk_df['Detection Source'].str.contains('Critical'))
                st.metric("Critical (Both)", crit_count)
    else:
        st.success("✅ No high-risk items found in the dataset!")


def render_ai_insights_section(df):
    """
    Render AI Insights section using Gemini API.
    
    Args:
        df: DataFrame with all data
    """
    st.markdown('<p class="section-header">🤖 AI Fraud Insights</p>', unsafe_allow_html=True)
    
    # --- Smart Filtering Logic (Same as Table) ---
    # 1. Rule-Based High Risk
    rule_mask = df['risk_level'] == 'High'
    
    # 2. AI Hidden Risk (Top 2%)
    if 'ml_risk_score' in df.columns:
        ml_threshold = df['ml_risk_score'].quantile(0.98)
        ai_mask = df['ml_risk_score'] > ml_threshold
    else:
        ai_mask = pd.Series(False, index=df.index)
        
    # Combine
    high_risk_df = df[rule_mask | ai_mask].copy()
    
    if len(high_risk_df) == 0:
        st.info("No high-risk tenders to analyze.")
        return
        
    # Sort by priority
    high_risk_df = high_risk_df.sort_values(['risk_score', 'ml_risk_score'], ascending=[False, False])
        
    # Prepare label components safely and ensure columns exist
    if 'dept_name' not in high_risk_df.columns:
        if 'department' in high_risk_df.columns:
            high_risk_df['dept_name'] = high_risk_df['department']
        elif 'Department' in high_risk_df.columns:
            high_risk_df['dept_name'] = high_risk_df['Department']
        elif 'buyer_name' in high_risk_df.columns:
            high_risk_df['dept_name'] = high_risk_df['buyer_name']
        else:
            high_risk_df['dept_name'] = "Unknown Dept"

    if 'contract_id' not in high_risk_df.columns:
        if 'Tender ID' in high_risk_df.columns:
            high_risk_df['contract_id'] = high_risk_df['Tender ID']
        elif 'tender_id' in high_risk_df.columns:
             high_risk_df['contract_id'] = high_risk_df['tender_id']
        else:
            high_risk_df['contract_id'] = "N/A"

    if 'contract_amount' not in high_risk_df.columns:
        if 'amount' in high_risk_df.columns:
            high_risk_df['contract_amount'] = high_risk_df['amount']
        elif 'Amount' in high_risk_df.columns:
            high_risk_df['contract_amount'] = high_risk_df['Amount']
        elif 'tender_value_amount' in high_risk_df.columns:
            high_risk_df['contract_amount'] = high_risk_df['tender_value_amount']
        else:
            high_risk_df['contract_amount'] = 0

    if 'bidder_count' not in high_risk_df.columns:
        if 'bidders_count' in high_risk_df.columns:
            high_risk_df['bidder_count'] = high_risk_df['bidders_count']
        else:
            # Default to 0 or N/A if missing, though risk calculation might have used it
            pass

    high_risk_df['label'] = (
        "Score: " + high_risk_df['risk_score'].astype(str) + 
        " | ID: " + high_risk_df['contract_id'].astype(str) +
        " | " + high_risk_df['dept_name'].astype(str)
    )
    
    selected_label = st.selectbox(
        "Select a High-Risk Tender to Analyze:",
        options=high_risk_df['label'].tolist()
    )
    
    if selected_label:
        selected_tender = high_risk_df[high_risk_df['label'] == selected_label].iloc[0]
        
        # Show mini details
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"**Contract ID:** {selected_tender['contract_id']}")
        with c2:
            st.markdown(f"**Amount:** ₹{selected_tender['contract_amount']:,}")
        with c3:
            st.markdown(f"**Risk Score:** {selected_tender['risk_score']}/100")
            
        if st.button("✨ Generate AI Explanation", type="primary"):
            st.markdown("---")
            with st.spinner("🤖 Consulting Gemini AI..."):
                try:
                    client = GeminiClient()
                    
                    # Identify triggered flags (columns with 1)
                    # We look for specific known flag columns
                    potential_flags = [
                        'single_bidder_flag', 'weak_competition', 'extreme_high_price',
                        'round_amount_flag', 'threshold_game', 'dec_rush', 'march_rush',
                        'weekend_award'
                    ]
                    
                    triggered_flags = []
                    for flag in potential_flags:
                        if flag in selected_tender and selected_tender[flag] == 1:
                            triggered_flags.append(flag)
                            
                    # Stream response
                    response_container = st.empty()
                    full_text = ""
                    
                    for chunk in client.get_fraud_explanation(
                        selected_tender.to_dict(), 
                        selected_tender['risk_score'],
                        triggered_flags
                    ):
                        full_text += chunk
                        response_container.markdown(full_text)
                        
                except Exception as e:
                    st.error(f"Error connecting to Gemini: {str(e)}")


def render_download_buttons(df):
    """
    Render download buttons for reports.
    
    Args:
        df: DataFrame to export
    """
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Main download button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Full Report",
            data=csv_data,
            file_name=f"fraud_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    # Additional reports
    st.markdown('<p class="section-header">📥 Additional Reports</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    # High-risk only
    with col1:
        high_risk_df = df[df['risk_level'] == 'High']
        if len(high_risk_df) > 0:
            high_risk_csv = high_risk_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "⚠️ High-Risk Items Only",
                high_risk_csv,
                f"high_risk_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "text/csv",
                use_container_width=True
            )
    
    # Medium-risk only
    with col2:
        medium_risk_df = df[df['risk_level'] == 'Medium']
        if len(medium_risk_df) > 0:
            medium_risk_csv = medium_risk_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📊 Medium-Risk Items",
                medium_risk_csv,
                f"medium_risk_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "text/csv",
                use_container_width=True
            )
    
    # Summary report
    with col3:
        metrics = calculate_risk_metrics(df)
        summary = export_analysis_summary(
            df, 
            st.session_state.get('risk_threshold', 70),
            st.session_state.get('upload_time', 'N/A'),
            metrics
        )
        st.download_button(
            "📄 Summary Report",
            summary,
            f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "text/plain",
            use_container_width=True
        )


from utils.ml_utils import run_ml_prediction

def load_ml_results(current_df):
    """
    Load ML results. First tries to load pre-computed results (fast).
    If not matching, runs prediction on the fly (flexible).
    
    Args:
        current_df: The dataframe currently loaded in the dashboard
        
    Returns:
        DataFrame: The dataframe with ML columns merged (if found), else original df
        bool: True if ML data was merged
    """
    ml_results_path = "experiments/model_results_v1.csv"
    
    # 1. Try Pre-computed Results (Fast Path)
    if os.path.exists(ml_results_path):
        try:
            ml_df = pd.read_csv(ml_results_path)
            
            # Simple check: if row counts match, we assume it's the same dataset
            if len(ml_df) == len(current_df):
                # Columns to merge
                cols_to_merge = ['ml_risk_score', 'ml_anomaly_label', 'ml_anomaly_score']
                
                # Only merge columns that exist in ml_df and NOT in current_df
                cols_to_add = [c for c in cols_to_merge if c in ml_df.columns and c not in current_df.columns]
                
                if cols_to_add:
                    if 'contract_id' in current_df.columns and 'contract_id' in ml_df.columns:
                        merged_df = current_df.merge(ml_df[['contract_id'] + cols_to_add], on='contract_id', how='left')
                        return merged_df, True
                    else:
                        ml_subset = ml_df[cols_to_add].reset_index(drop=True)
                        current_df = current_df.reset_index(drop=True)
                        merged_df = pd.concat([current_df, ml_subset], axis=1)
                        return merged_df, True
        except Exception as e:
            # If loading fails, fall through to on-the-fly prediction
            pass
            
    # 2. Run Prediction On-The-Fly (Flexible Path)
    # This handles new files like sample_tenders.csv
    with st.spinner("🤖 Running ML Model on new data..."):
        df_predicted, success = run_ml_prediction(current_df)
        return df_predicted, success


def render_ml_section(df):
    """
    Render the ML-based anomaly detection section.
    """
    st.markdown('<p class="section-header">🤖 ML-Based Anomaly Detection</p>', unsafe_allow_html=True)
    
    if 'ml_risk_score' not in df.columns:
        st.info("ML results not available for this dataset.")
        return

    # Metrics
    n_anomalies = df[df['ml_anomaly_label'] == -1].shape[0]
    pct_anomalies = (n_anomalies / len(df)) * 100
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("ML Detected Anomalies", f"{n_anomalies}", f"{pct_anomalies:.1f}% of total")
    with col2:
        st.metric("Max ML Risk Score", f"{df['ml_risk_score'].max():.2f}")
    with col3:
        # Correlation between Rule and ML
        if 'risk_score' in df.columns:
            corr = df['risk_score'].corr(df['ml_risk_score'])
            st.metric("Correlation (Rule vs ML)", f"{corr:.2f}")

    # Scatter Plot: Rule Score vs ML Score
    if 'risk_score' in df.columns:
        st.markdown("#### Rule-Based vs. ML-Based Risk Comparison")
        st.caption("Points in the top-right are flagged by BOTH systems (Highest Priority). Points in top-left or bottom-right are where models disagree.")
        
        # Add jitter to x-axis for better visibility
        # We create a temporary column for plotting so we don't mess up the actual data
        plot_df = df.copy()
        # Add random noise between -1.5 and 1.5 to the integer score to spread points out
        plot_df['risk_score_jittered'] = plot_df['risk_score'] + np.random.uniform(-1.5, 1.5, len(plot_df))
        
        # --- Prepare "Plain English" Interpretations ---
        plot_df['rule_interpretation'] = plot_df['risk_score'].apply(
            lambda x: "⚠️ High Policy Violations" if x > 70 else ("⚠️ Some Violations" if x > 40 else "✅ Follows Rules")
        )
        
        ml_threshold = df['ml_risk_score'].quantile(0.95)
        plot_df['ai_interpretation'] = plot_df['ml_risk_score'].apply(
            lambda x: "⚠️ Statistically Suspicious" if x > ml_threshold else "✅ Normal Pattern"
        )

        # Dynamic column selection for hover data
        # We force specific order for customdata: [risk_score, contract_id, contract_amount, dept_name, rule_interpretation, ai_interpretation]
        
        # 1. ID
        id_col = 'contract_id' if 'contract_id' in plot_df.columns else ('tender_id' if 'tender_id' in plot_df.columns else None)
        # 2. Amount
        amt_col = 'contract_amount' if 'contract_amount' in plot_df.columns else ('amount' if 'amount' in plot_df.columns else None)
        # 3. Dept
        dept_col = 'dept_name' if 'dept_name' in plot_df.columns else ('department' if 'department' in plot_df.columns else None)
        
        hover_cols = ['risk_score'] # Index 0
        if id_col: hover_cols.append(id_col) # Index 1
        if amt_col: hover_cols.append(amt_col) # Index 2
        if dept_col: hover_cols.append(dept_col) # Index 3
        
        hover_cols.append('rule_interpretation') # Index 4 (or 3 or 2 depending on missing cols)
        hover_cols.append('ai_interpretation') # Index 5
        
        fig = px.scatter(
            plot_df, 
            x='risk_score_jittered', 
            y='ml_risk_score',
            color='risk_level',
            hover_data=hover_cols,
            color_discrete_map={'High': '#e74c3c', 'Medium': '#f39c12', 'Low': '#2ecc71'},
            labels={
                'risk_score_jittered': 'Policy Violation Score (Rules)', 
                'ml_risk_score': 'Statistical Irregularity (AI)'
            },
            opacity=0.6,
            title="Risk Analysis: Policy Compliance vs. Behavioral Patterns"
        )
        
        # Add "Sweet Spot" (Hidden Risk) Highlight
        # Top-Left: Low Rule Score (< 40), High ML Score (> Threshold)
        fig.add_shape(
            type="rect",
            x0=-5, x1=40, # Low Rule Score area
            y0=ml_threshold, y1=df['ml_risk_score'].max() * 1.1, # High ML Score area
            line=dict(color="#E74C3C", width=2, dash="dot"),
            fillcolor="rgba(231, 76, 60, 0.1)",
        )
        
        fig.add_annotation(
            x=20, y=df['ml_risk_score'].max(),
            text="<b>Hidden Risk Detected</b><br>Compliant but Suspicious",
            showarrow=True,
            arrowhead=2,
            ax=0, ay=-40,
            bgcolor="white",
            bordercolor="#E74C3C",
            font=dict(color="#E74C3C")
        )
        
        # Add threshold lines
        fig.add_hline(y=ml_threshold, line_dash="dash", line_color="gray", annotation_text="AI Alert Threshold")
        fig.add_vline(x=70, line_dash="dash", line_color="gray", annotation_text="Policy Violation Threshold")
        
        st.plotly_chart(fig, use_container_width=True)


def render_dashboard_tab():
    """
    Render the main dashboard tab with all analysis results.
    """
    st.markdown('<p class="section-header">📊 Fraud Risk Analysis Dashboard</p>', unsafe_allow_html=True)
    
    if 'analyzed' in st.session_state and st.session_state['analyzed']:
        df = st.session_state['df']
        risk_threshold = st.session_state.get('risk_threshold', 70)
        
        # Generate risk scores and levels
        df = generate_risk_scores(df, seed=42)
        df = classify_risk_levels(df, risk_threshold)
        
        # INTEGRATION: Load ML Results
        df, has_ml = load_ml_results(df)
        
        # --- UPDATE RISK LEVELS WITH AI INSIGHTS ---
        # If AI finds a "Hidden Risk" (Top 2%), we should upgrade it to High Risk
        # so it appears in the Red Card and Pie Chart.
        if has_ml and 'ml_risk_score' in df.columns:
            ml_threshold = df['ml_risk_score'].quantile(0.98)
            # Find indices where AI is high but Rule is not High
            hidden_risk_mask = (df['ml_risk_score'] > ml_threshold) & (df['risk_level'] != 'High')
            count_upgraded = hidden_risk_mask.sum()
            
            if count_upgraded > 0:
                df.loc[hidden_risk_mask, 'risk_level'] = 'High'
                # Optional: Add a visual indicator that this was AI-upgraded? 
                # For now, we just ensure the metrics match the table.
        
        metrics = calculate_risk_metrics(df)
        
        # Render metric cards
        render_metric_cards(metrics)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Charts Section
        st.markdown('<p class="section-header">📊 Visual Analytics</p>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            render_risk_distribution_chart(df, metrics)
        
        with col2:
            render_risk_score_chart(df)
            
        # ML Section (New)
        if has_ml:
            st.markdown("<br>", unsafe_allow_html=True)
            render_ml_section(df)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # High-risk table
        render_high_risk_table(df)
        
        # AI Insights Section
        st.markdown("<br>", unsafe_allow_html=True)
        render_ai_insights_section(df)
        
        # Download buttons
        render_download_buttons(df)
    
    else:
        # No analysis yet
        st.markdown("""
        <div class="info-box-gray">
            <h3 style="color: #1f77b4; margin-top: 0;">📌 Getting Started</h3>
            <p style="color: #6b7280; margin: 0;">Follow these steps to analyze your procurement data:</p>
            <ol style="color: #6b7280; margin: 1rem 0 0 0; line-height: 2;">
                <li>Go to the <strong>Upload</strong> tab</li>
                <li>Upload your procurement data CSV file</li>
                <li>Click the <strong>Analyze for Fraud</strong> button</li>
                <li>Return here to view comprehensive analytics</li>
                <li>Use the <strong>AI Insights</strong> section below tables to generate explanations for valid fraud alerts</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
