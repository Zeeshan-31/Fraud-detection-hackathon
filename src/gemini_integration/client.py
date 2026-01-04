"""
Gemini API Client for generating fraud insights.
"""
import os
import google.generativeai as genai
import streamlit as st

class GeminiClient:
    def __init__(self, api_key=None):
        """
        Initialize Gemini client.
        
        Args:
            api_key: Optional API key. If not provided, looks for GEMINI_API_KEY env var
                    or in streamlit secrets.
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        
        # Check streamlit secrets if not found in env
        if not self.api_key:
            try:
                self.api_key = st.secrets["GEMINI_API_KEY"]
            except:
                pass
                
        if not self.api_key:
            print("⚠️ Warning: No Gemini API Key found")
            
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            
    def get_fraud_explanation(self, tender_data, risk_score, risk_factors):
        """
        Generate an explanation for why a tender was flagged as fraud.
        
        Args:
            tender_data: Dictionary of tender details
            risk_score: Float, calculated fraud risk score
            risk_factors: List of strings describing triggered risk factors
            
        Returns:
            Generator: Streaming response from Gemini
        """
        if not self.api_key:
            yield "⚠️ Error: Gemini API Key not configured. Please set GEMINI_API_KEY environment variable."
            return

        prompt = f"""
        You are an expert fraud auditor for government procurement. 
        Analyze the following flagged tender and explain why it is suspicious.
        
        TENDER DETAILS:
        - ID: {tender_data.get('contract_id', 'N/A')}
        - Department: {tender_data.get('dept_name', 'N/A')}
        - Amount: ₹{tender_data.get('contract_amount', 0):,}
        - Bidders: {tender_data.get('bidder_count', 'N/A')}
        
        RISK ASSESSMENT:
        - Risk Score: {risk_score}/100
        - Triggered Risk Factors: {', '.join(risk_factors)}
        
        Please provide a concise, professional analysis (max 3-4 paragraphs).
        1. Start with a direct summary of why this is high risk.
        2. Explain the specific implications of the triggered risk factors (e.g. why a single bidder is bad combined with high price).
        3. Recommend specific audit steps to verify if this is actual fraud.
        
        Format the output with Markdown. Use bolding for key points.
        """
        
        try:
            response = self.model.generate_content(prompt, stream=True)
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            yield f"⚠️ Error generating explanation: {str(e)}"
