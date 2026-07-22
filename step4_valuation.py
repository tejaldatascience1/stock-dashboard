# --- Step 4: DCF Valuation Model ---
class DCFValuation:
    def __init__(self, stock_ticker, balance_sheet, income_statement, cash_flow):
        self.stock = stock_ticker
        self.bs = balance_sheet.fillna(0)
        self.inc = income_statement.fillna(0)
        self.cf = cash_flow.fillna(0)
        
    def calculate_intrinsic_value(self):
        try:
            if self.cf.empty:
                return "Error: Cash flow data not available for Valuation."
                
            latest_cf_col = self.cf.columns[0]
            
            def get_val(df, col, names):
                for name in names:
                    if name in df.index:
                        return df.loc[name, col]
                return 0.0

            ocf = get_val(self.cf, latest_cf_col, ['Operating Cash Flow', 'Total Cash From Operating Activities'])
            capex = abs(get_val(self.cf, latest_cf_col, ['Capital Expenditures', 'Purchase Of Property Plant And Equipment']))
            
            fcf = ocf - capex
            if fcf <= 0:
                fcf = ocf * 0.5  
                
            growth_rate = 0.08      
            discount_rate = 0.10    
            terminal_growth = 0.03  
            years = 5
            
            future_fcf = []
            current_fcf = fcf
            for i in range(years):
                current_fcf *= (1 + growth_rate)
                discounted_val = current_fcf / ((1 + discount_rate) ** (i + 1))
                future_fcf.append(discounted_val)
                
            sum_present_value = sum(future_fcf)
            terminal_value = (future_fcf[-1] * (1 + terminal_growth)) / (discount_rate - terminal_growth)
            discounted_terminal_value = terminal_value / ((1 + discount_rate) ** years)
            
            enterprise_value = sum_present_value + discounted_terminal_value
            
            latest_bs_col = self.bs.columns[0]
            cash = get_val(self.bs, latest_bs_col, ['Cash And Cash Equivalents', 'Cash Cash Equivalents And Short Term Investments'])
            total_debt = get_val(self.bs, latest_bs_col, ['Total Debt', 'Long Term Debt', 'Short Long Term Debt'])
            
            equity_value = enterprise_value + cash - total_debt
            
            shares_outstanding = self.stock.info.get('sharesOutstanding', 0)
            if shares_outstanding == 0:
                return "Error: Shares outstanding data not available."
                
            intrinsic_value_per_share = equity_value / shares_outstanding
            
            # Robust price fetching fallback to eliminate N/A
            current_market_price = self.stock.info.get('currentPrice', 0)
            if current_market_price == 0:
                current_market_price = self.stock.info.get('regularMarketPrice', 0)
            if current_market_price == 0:
                hist_prices = self.stock.history(period="1d")
                if not hist_prices.empty:
                    current_market_price = hist_prices['Close'].iloc[-1]
            
            if current_market_price > 0:
                diff_percentage = ((intrinsic_value_per_share - current_market_price) / current_market_price) * 100
                if intrinsic_value_per_share > current_market_price:
                    status = f"Undervalued by {abs(round(diff_percentage, 2))}% (Good to Buy)"
                else:
                    status = f"Overvalued by {round(diff_percentage, 2)}% (Caution / Expensive)"
            else:
                status = "Market price unavailable"

            return {
                'Intrinsic Value': round(intrinsic_value_per_share, 2),
                'Current Price': round(current_market_price, 2),
                'Status': status
            }
            
        except Exception as e:
            return f"Error in Valuation: {e}"
