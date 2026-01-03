"""
Dashboard tab component for the dashboard.
Displays fraud analysis results and charts.
"""

import streamlit as st
import pandas as pd
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
    
    Args:
        df: DataFrame with risk levels
    """
    st.markdown('<p class="section-header">⚠️ High-Risk Tenders Requiring Review</p>', unsafe_allow_html=True)
    
    high_risk_df = df[df['risk_level'] == 'High'].sort_values('risk_score', ascending=False)
    
    if len(high_risk_df) > 0:
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
            high_risk_df.head(20),
            use_container_width=True,
            hide_index=True,
            height=400
        )
        
        # Statistics
        with st.expander("📊 High-Risk Statistics"):
            stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
            with stat_col1:
                st.metric("Average Risk Score", f"{high_risk_df['risk_score'].mean():.1f}")
            with stat_col2:
                st.metric("Highest Risk Score", f"{high_risk_df['risk_score'].max()}")
            with stat_col3:
                st.metric("Items > 90 Score", len(high_risk_df[high_risk_df['risk_score'] > 90]))
            with stat_col4:
                st.metric("Items > 80 Score", len(high_risk_df[high_risk_df['risk_score'] > 80]))
    else:
        st.success("✅ No high-risk items found in the dataset!")


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
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # High-risk table
        render_high_risk_table(df)
        
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
            </ol>
        </div>
        """, unsafe_allow_html=True)
