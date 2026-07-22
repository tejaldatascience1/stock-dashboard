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
            
            # Helper function to find values flexibly
            def get_val(df, col, names):
                for name in names:
                    if name in df.index:
                        return df.loc[name, col]
                return 0.0

            # Free Cash Flow (FCF) approximation: Operating Cash Flow - Capital Expenditures
            ocf = get_val(self.cf, latest_cf_col, ['Operating Cash Flow', 'Total Cash From Operating Activities'])
            capex = abs(get_val(self.cf, latest_cf_col, ['Capital Expenditures', 'Purchase Of Property Plant And Equipment']))
            
            fcf = ocf - capex
            if fcf <= 0:
                fcf = ocf * 0.5  # Fallback rough estimation if Capex data is messy
                
            # Assumptions for DCF
            growth_rate = 0.08      # Estimated 8% growth rate for next 5 years
            discount_rate = 0.10    # Required rate of return (Cost of Capital) ~ 10%
            terminal_growth = 0.03  # Long-term stable growth rate ~ 3%
            years = 5
            
            # Projecting Future Cash Flows
            future_fcf = []
            current_fcf = fcf
            for i in range(years):
                current_fcf *= (1 + growth_rate)
                discounted_val = current_fcf / ((1 + discount_rate) ** (i + 1))
                future_fcf.append(discounted_val)
                
            sum_present_value = sum(future_fcf)
            
            # Terminal Value Calculation
            terminal_value = (future_fcf[-1] * (1 + terminal_growth)) / (discount_rate - terminal_growth)
            discounted_terminal_value = terminal_value / ((1 + discount_rate) ** years)
            
            # Total Enterprise Value
            enterprise_value = sum_present_value + discounted_terminal_value
            
            # Equity Value = Enterprise Value + Cash - Total Debt
            latest_bs_col = self.bs.columns[0]
            cash = get_val(self.bs, latest_bs_col, ['Cash And Cash Equivalents', 'Cash Cash Equivalents And Short Term Investments'])
            total_debt = get_val(self.bs, latest_bs_col, ['Total Debt', 'Long Term Debt', 'Short Long Term Debt'])
            
            equity_value = enterprise_value + cash - total_debt
            
            # Intrinsic Value Per Share
            shares_outstanding = self.stock.info.get('sharesOutstanding', 0)
            if shares_outstanding == 0:
                return "Error: Shares outstanding data not available."
                
            intrinsic_value_per_share = equity_value / shares_outstanding
            current_market_price = self.stock.info.get('currentPrice', self.stock.info.get('regularMarketPrice', 0))
            
            # Margin of Safety / Status
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