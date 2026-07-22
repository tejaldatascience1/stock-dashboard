import yfinance as yf
import pandas as pd
from step3_altman import AltmanZScoreAnalyzer
from step4_valuation import DCFValuation
from step5_ai_insights import AIInsightsAnalyzer

class ExecutiveDashboardPipeline:
    def __init__(self, ticker_symbol):
        self.ticker_symbol = ticker_symbol.upper()
        self.stock = yf.Ticker(self.ticker_symbol)
        
    def run_full_pipeline(self):
        try:
            # 1. Data Collection
            income_statement = self.stock.financials
            balance_sheet = self.stock.balance_sheet
            cash_flow = self.stock.cashflow
            historical_data = self.stock.history(period="6mo")
            
            if balance_sheet is None or balance_sheet.empty:
                return {"error": f"Could not retrieve financial statements for {self.ticker_symbol}."}
                
            # 2. Cleaning & Basic Ratios
            bs_clean = balance_sheet.fillna(0)
            inc_clean = income_statement.fillna(0)
            cf_clean = cash_flow.fillna(0)
            
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
            
            # 3. Altman Z-Score Analysis
            altman = AltmanZScoreAnalyzer(self.stock, bs_clean, inc_clean)
            z_result = altman.calculate_z_score()
            
            # 4. DCF Valuation Analysis
            valuation = DCFValuation(self.stock, bs_clean, inc_clean, cf_clean)
            val_result = valuation.calculate_intrinsic_value()
            
            # 5. AI Insights Generation
            ai_analyzer = AIInsightsAnalyzer(self.stock, historical_data, ratios, z_result, val_result)
            ai_summary = ai_analyzer.generate_smart_executive_summary()
            
            return {
                "success": True,
                "ticker": self.ticker_symbol,
                "ratios": ratios,
                "z_result": z_result,
                "val_result": val_result,
                "ai_summary": ai_summary,
                "historical_data": historical_data
            }
            
        except Exception as e:
            return {"error": str(e)}
