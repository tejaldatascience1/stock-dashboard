import streamlit as st
import pandas as pd
from main import ExecutiveDashboardPipeline

# --- Page Configuration ---
st.set_page_config(page_title="AI Financial & Valuation Dashboard", layout="wide")

st.title("📊 AI-Powered Executive Financial Dashboard")
st.write("Enter any stock ticker below to generate a live financial health, valuation, and AI insight report instantly.")

# --- Sidebar Input ---
st.sidebar.header("Configuration")
user_ticker = st.sidebar.text_input("Enter Stock Ticker", value="MSFT").upper()
run_button = st.sidebar.button("Generate Dashboard")

if run_button and user_ticker:
    with st.spinner(f"Fetching financial data and running pipeline for {user_ticker}..."):
        # Run through main.py pipeline
        pipeline = ExecutiveDashboardPipeline(user_ticker)
        result = pipeline.run_full_pipeline()
        
        if "error" in result:
            st.error(result["error"])
        else:
            st.success(f"Successfully generated report for {user_ticker}!")
            
            ratios = result["ratios"]
            z_result = result["z_result"]
            val_result = result["val_result"]
            ai_summary = result["ai_summary"]
            historical_data = result["historical_data"]
            
            # Parse Z-Score safely
            z_score = z_result.get('Z-Score', 0) if isinstance(z_result, dict) else 0
            zone = z_result.get('Zone', 'N/A') if isinstance(z_result, dict) else 'N/A'
            
            # Parse Valuation safely
            if isinstance(val_result, dict):
                intrinsic_val = val_result.get('Intrinsic Value', 'N/A')
                current_price = val_result.get('Current Price', 'N/A')
                val_status = val_result.get('Status', 'N/A')
            else:
                intrinsic_val = 'N/A'
                current_price = 'N/A'
                val_status = str(val_result) if val_result is not None else 'N/A'

            # --- UI Layout: Metrics Cards ---
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Current Price", f"${current_price}" if isinstance(current_price, (int, float)) else current_price)
            col2.metric("Intrinsic Value", f"${intrinsic_val}" if isinstance(intrinsic_val, (int, float)) else intrinsic_val)
            col3.metric("Altman Z-Score", f"{z_score}", zone)
            col4.metric("Debt-to-Equity", f"{ratios['Debt-to-Equity']}")

            st.markdown("---")
            
            # --- Financial Ratios Details ---
            st.subheader("📈 Core Financial Health Metrics")
            r_col1, r_col2, r_col3 = st.columns(3)
            r_col1.write(f"**Latest Financial Year:** {ratios['Latest Year']}")
            r_col2.write(f"**Working Capital:** {ratios['Working Capital']:,.2f}")
            r_col3.write(f"**Current Ratio:** {ratios['Current Ratio']}")
            st.write(f"**Valuation Status:** {val_status}")

            st.markdown("---")

            # --- AI Insights Section ---
            st.subheader("🤖 AI Executive Summary & Insights")
            st.info(ai_summary)
            
            # --- Stock Price Chart ---
            st.subheader("📉 6-Month Price Trend")
            if not historical_data.empty and 'Close' in historical_data.columns:
                st.line_chart(historical_data['Close'])
            else:
                st.warning("Historical price chart data not available.")
