# --- Step 3: Altman Z-Score Analyzer ---
class AltmanZScoreAnalyzer:
    def __init__(self, stock_ticker, balance_sheet, income_statement):
        self.stock = stock_ticker
        self.bs = balance_sheet.fillna(0)
        self.inc = income_statement.fillna(0)
        
    def calculate_z_score(self):
        try:
            if self.bs.empty or self.inc.empty:
                return "Error: Financial data not available for Z-Score."
                
            latest_bs_col = self.bs.columns[0]
            latest_inc_col = self.inc.columns[0]
            
            def get_val(df, col, names):
                for name in names:
                    if name in df.index:
                        return df.loc[name, col]
                return 0.0

            total_assets = get_val(self.bs, latest_bs_col, ['Total Assets'])
            if total_assets == 0:
                return "Error: Total Assets cannot be zero."
                
            current_assets = get_val(self.bs, latest_bs_col, ['Current Assets', 'Total Current Assets'])
            current_liabilities = get_val(self.bs, latest_bs_col, ['Current Liabilities', 'Total Current Liabilities'])
            working_capital = current_assets - current_liabilities
            
            retained_earnings = get_val(self.bs, latest_bs_col, ['Retained Earnings'])
            ebit = get_val(self.inc, latest_inc_col, ['Operating Income', 'EBIT', 'Earnings Before Interest and Taxes'])
            
            market_cap = self.stock.info.get('marketCap', 0)
            total_liabilities = get_val(self.bs, latest_bs_col, ['Total Liabilities Net Minority Interest', 'Total Liabilities'])
            sales = get_val(self.inc, latest_inc_col, ['Total Revenue', 'Revenue'])
            
            # Altman Z-Score Components
            X1 = working_capital / total_assets
            X2 = retained_earnings / total_assets
            X3 = ebit / total_assets
            X4 = market_cap / total_liabilities if total_liabilities != 0 else 0
            X5 = sales / total_assets
            
            z_score = (1.2 * X1) + (1.4 * X2) + (3.3 * X3) + (0.6 * X4) + (0.999 * X5)
            
            if z_score > 2.99:
                zone = "Safe Zone (Low Bankruptcy Risk)"
            elif 1.81 <= z_score <= 2.99:
                zone = "Grey Zone (Caution / Moderate Risk)"
            else:
                zone = "Distress Zone (High Bankruptcy Risk)"
                
            return {
                'Z-Score': round(z_score, 2),
                'Zone': zone
            }
        except Exception as e:
            return f"Error calculating Z-Score: {e}"