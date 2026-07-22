import pandas as pd
import yfinance as yf
from step3_altman import AltmanZScoreAnalyzer
from step4_valuation import DCFValuation
from step5_ai_insights import AIInsightsAnalyzer

# --- Step 6: Dedicated Individual Executive Dashboard Exporter (Wide Columns Format for Power BI) ---
class ExecutiveDashboardExporter:
    def __init__(self, ticker, ratios, z_score_result, valuation_result, ai_summary):
        self.ticker = ticker.upper()
        self.ratios = ratios
        
        if isinstance(z_score_result, dict):
            self.z_score = z_score_result.get('Z-Score', 0)
            self.zone = z_score_result.get('Zone', 'N/A')
        else:
            self.z_score = z_score_result if z_score_result is not None else 0
            self.zone = 'N/A'

        if isinstance(valuation_result, dict):
            self.intrinsic_value = valuation_result.get('Intrinsic Value', 'N/A')
            self.current_price = valuation_result.get('Current Price', 'N/A')
            self.status = valuation_result.get('Status', 'N/A')
        else:
            self.intrinsic_value = 'N/A'
            self.current_price = 'N/A'
            self.status = str(valuation_result) if valuation_result is not None else 'N/A'
            
        self.ai_summary = ai_summary

    def generate_dashboard_excel(self):
        file_name = f"{self.ticker}_executive_dashboard.xlsx"
        
        data = {
            "Ticker": [self.ticker],
            "Latest Financial Year": [self.ratios.get('Latest Year', 'N/A')],
            "Working Capital": [self.ratios.get('Working Capital', 0)],
            "Current Ratio": [self.ratios.get('Current Ratio', 0)],
            "Debt-to-Equity": [self.ratios.get('Debt-to-Equity', 0)],
            "Altman Z-Score": [self.z_score],
            "Financial Health Zone": [self.zone],
            "Estimated Intrinsic Value": [self.intrinsic_value],
            "Current Market Price": [self.current_price],
            "Valuation Status": [self.status]
        }

        df = pd.DataFrame(data)
        
        with pd.ExcelWriter(file_name, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=f"{self.ticker} Summary", index=False)
        
        print(f"[✔] Dedicated Executive Dashboard generated: {file_name}")
        return file_name

# --- Step 1: Data Collection ---
class DataCollector:
    def __init__(self, ticker: str):
        self.ticker = ticker.upper()
        self.stock = yf.Ticker(self.ticker)
        
    def fetch_financial_statements(self):
        try:
            income_statement = self.stock.financials
            balance_sheet = self.stock.balance_sheet
            cash_flow = self.stock.cashflow
            historical_data = self.stock.history(period="6mo")
            return income_statement, balance_sheet, cash_flow, historical_data
        except Exception as e:
            print(f"Error fetching statements for {self.ticker}: {e}")
            return None, None, None, None

# --- Step 2: Data Cleaning & Ratios ---
class DataCleaner:
    def __init__(self, balance_sheet, income_statement):
        self.bs = balance_sheet
        self.inc = income_statement
        
    def get_cleaned_financials(self):
        missing_bs_count = self.bs.isna().sum().sum()
        missing_inc_count = self.inc.isna().sum().sum()
        total_missing = missing_bs_count + missing_inc_count
        
        bs_clean = self.bs.fillna(0)
        inc_clean = self.inc.fillna(0)
        return bs_clean, inc_clean, total_missing

    def calculate_health_ratios(self, clean_bs):
        latest_col = clean_bs.columns[0]
        
        def find_row_value(possible_names):
            for name in possible_names:
                if name in clean_bs.index:
                    return clean_bs.loc[name, latest_col]
            return 0.0

        ca = find_row_value(['Current Assets', 'Total Current Assets'])
        cl = find_row_value(['Current Liabilities', 'Total Current Liabilities'])
        debt = find_row_value(['Total Debt', 'Long Term Debt', 'Total Liabilities Net Minority Interest'])
        equity = find_row_value(['Stockholders Equity', 'Common Stock Equity', 'Total Equity Gross Minority Interest'])
        
        if ca == 0 or cl == 0:
            for idx in clean_bs.index:
                idx_lower = str(idx).lower()
                if 'current assets' in idx_lower and ca == 0:
                    ca = clean_bs.loc[idx, latest_col]
                if 'current liabilities' in idx_lower and cl == 0:
                    cl = clean_bs.loc[idx, latest_col]

        working_capital = ca - cl
        current_ratio = (ca / cl) if cl != 0 else 0.0
        debt_to_equity = (debt / equity) if equity != 0 else 0.0
        
        return {
            'Latest Year': str(latest_col).split()[0],
            'Working Capital': working_capital,
            'Current Ratio': round(current_ratio, 2),
            'Debt-to-Equity': round(debt_to_equity, 2)
        }

# --- Main Execution Pipeline ---
if __name__ == "__main__":
    user_ticker = input("Enter the Stock Ticker Symbol (e.g., AAPL, MSFT, TSLA): ")
    
    print(f"\n--- Running Full AI-Powered Pipeline for {user_ticker.upper()} ---")
    
    collector = DataCollector(user_ticker)
    inc, bs, cf, hist = collector.fetch_financial_statements()
    
    if bs is not None and not bs.empty:
        print(f"[✔] Financial data fetched successfully ({len(bs.columns)} Years loaded).")
        
        cleaner = DataCleaner(bs, inc)
        clean_bs, clean_inc, total_missing = cleaner.get_cleaned_financials()
        ratios = cleaner.calculate_health_ratios(clean_bs)
        
        altman = AltmanZScoreAnalyzer(collector.stock, clean_bs, clean_inc)
        z_result = altman.calculate_z_score()
        
        valuation = DCFValuation(collector.stock, clean_bs, clean_inc, cf)
        val_result = valuation.calculate_intrinsic_value()
        
        ai_analyzer = AIInsightsAnalyzer(collector.stock, hist, ratios, z_result, val_result)
        ai_summary = ai_analyzer.generate_smart_executive_summary()
        
        # Generate Dedicated Individual Dashboard File
        exporter = ExecutiveDashboardExporter(user_ticker, ratios, z_result, val_result, ai_summary)
        dashboard_file = exporter.generate_dashboard_excel()
        
        print(f"\n==============================================")
        print(f"         COMPLETE FINANCIAL REPORT              ")
        print(f"==============================================")
        print(f"• Target Company                : {user_ticker.upper()}")
        print(f"• Missing Data Points Fixed     : {total_missing}")
        print(f"• Latest Financial Year         : {ratios.get('Latest Year', 'N/A')}")
        print(f"• Working Capital               : {ratios.get('Working Capital', 0):,.2f}")
        print(f"• Current Ratio                 : {ratios.get('Current Ratio', 0)}")
        print(f"• Debt-to-Equity Ratio          : {ratios.get('Debt-to-Equity', 0)}")
        
        if isinstance(z_result, dict):
            print(f"• Altman Z-Score                : {z_result['Z-Score']}")
            print(f"• Financial Health Zone         : {z_result['Zone']}")
        else:
            print(f"• Altman Z-Score                : {z_result}")
            
        if isinstance(val_result, dict):
            print(f"• Estimated Intrinsic Value     : {val_result['Intrinsic Value']}")
            print(f"• Current Market Price          : {val_result['Current Price']}")
            print(f"• Valuation Status              : {val_result['Status']}")
        else:
            print(f"• Valuation Output              : {val_result}")
            
        print(f"----------------------------------------------")
        print(ai_summary)
        print(f"----------------------------------------------")
        print(f"• Dedicated Dashboard File      : {dashboard_file}")
        print(f"==============================================")
        print(f"✔ Pipeline & Dashboard Generation Successful!")
        print(f"==============================================")
    else:
        print(f"Could not retrieve data for '{user_ticker}'.")