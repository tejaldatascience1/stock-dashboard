import streamlit as st
import pandas as pd
import yfinance as yf
from step3_altman import AltmanZScoreAnalyzer
from step4_valuation import DCFValuation
from step5_ai_insights import AIInsightsAnalyzer

# --- Page Configuration ---
st.set_page_config(page_title="AI Financial & Valuation Dashboard", layout="wide")

st.title("📊 AI-Powered Executive Financial Dashboard")
st.write("Enter any stock ticker below to generate a live financial health, valuation, and AI insight report instantly.")

# --- Sidebar Input ---
st.sidebar.header("Configuration")
user_ticker = st.sidebar.text_input("Enter Stock Ticker", value="MSFT").upper()
run_button = st.sidebar.button("Generate Dashboard")

if run_button and user_ticker:
    with st.spinner(f"Fetching financial data and running AI models for {user_ticker}..."):
        try:
            # --- Step 1: Data Collection ---
            stock = yf.Ticker(user_ticker)
            income_statement = stock.financials
            balance_sheet = stock.balance_sheet
            cash_flow = stock.cashflow
            historical_data = stock.history(period="6mo")
            
            if balance_sheet is not None and not balance_sheet.empty:
                # --- Step 2: Data Cleaning & Ratios ---
                bs_clean = balance_sheet.fillna(0)
                inc_clean = income_statement.fillna(0)
                
                latest_col = bs_clean.columns[0]
                
                def find_row_value(possible_names):
                    for name in possible_names:
                        if name in bs_clean.index:
                            return bs_clean.loc[name, latest_col]
                    return 0.0

                ca = find_row_value(['Current Assets', 'Total Current Assets'])
                cl = find_row_value(['Current Liabilities', 'Total Current Liabilities'])
                debt = find_row_value(['Total Debt', 'Long Term Debt', 'Total Liabilities Net Minority Interest'])
                equity = find_row_value(['Stockholders Equity', 'Common Stock Equity', 'Total Equity Gross Minority Interest'])
                
                working_capital = ca - cl
                current_ratio = (ca / cl) if cl != 0 else 0.0
                debt_to_equity = (debt / equity) if equity != 0 else 0.0
                
                ratios = {
                    'Latest Year': str(latest_col).split()[0],
                    'Working Capital': working_capital,
                    'Current Ratio': round(current_ratio, 2),
                    'Debt-to-Equity': round(debt_to_equity, 2)
                }
                
                # --- Step 3 & 4 & 5: Analysis ---
                altman = AltmanZScoreAnalyzer(stock, bs_clean, inc_clean)
                z_result = altman.calculate_z_score()
                
                valuation = DCFValuation(stock, bs_clean, inc_clean, cash_flow)
                val_result = valuation.calculate_intrinsic_value()
                
                ai_analyzer = AIInsightsAnalyzer(stock, historical_data, ratios, z_result, val_result)
                ai_summary = ai_analyzer.generate_smart_executive_summary()
                
                # --- Parse Results for UI ---
                z_score = z_result.get('Z-Score', 0) if isinstance(z_result, dict) else (z_result or 0)
                zone = z_result.get('Zone', 'N/A') if isinstance(z_result, dict) else 'N/A'
                
                intrinsic_val = val_result.get('Intrinsic Value', 'N/A') if isinstance(val_result, dict) else 'N/A'
                current_price = val_result.get('Current Price', 'N/A') if isinstance(val_result, dict) else 'N/A'
                val_status = val_result.get('Status', 'N/A') if isinstance(val_result, dict) else str(val_result)

                # --- UI Layout: Metrics Cards ---
                st.success(f"Successfully generated report for {user_ticker}!")
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Current Price", f"${current_price}" if isinstance(current_price, (int, float)) else current_price)
                col2.metric("Intrinsic Value", f"${intrinsic_val}" if isinstance(intrinsic_val, (int, float)) else intrinsic_val)
                col3.metric("Altman Z-Score", f"{z_score}", zone)
                col4.metric("Debt-to-Equity", f"{debt_to_equity}")

                st.markdown("---")
                
                # --- Financial Ratios Details ---
                st.subheader("📈 Core Financial Health Metrics")
                r_col1, r_col2, r_col3 = st.columns(3)
                r_col1.write(f"**Latest Financial Year:** {ratios['Latest Year']}")
                r_col2.write(f"**Working Capital:** {ratios['Working Capital']:,.2f}")
                r_col3.write(f"**Current Ratio:** {ratios['Current Ratio']}")
                r_col4 = st.write(f"**Valuation Status:** {val_status}")

                st.markdown("---")

                # --- AI Insights Section ---
                st.subheader("🤖 AI Executive Summary & Insights")
                st.info(ai_summary)
                
                # --- Stock Price Chart ---
                st.subheader("📉 6-Month Price Trend")
                st.line_chart(historical_data['Close'])

            else:
                st.error(f"Could not retrieve financial statements for {user_ticker}. Please check the ticker symbol.")
                
        except Exception as e:
                st.error(f"An error occurred: {e}")