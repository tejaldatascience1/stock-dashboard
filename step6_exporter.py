import pandas as pd
import os

class ExcelReportExporter:
    def __init__(self, ticker, ratios, z_score_result, valuation_result, ai_summary):
        self.ticker = ticker.upper()
        self.ratios = ratios if isinstance(ratios, dict) else {}
        self.z_score = z_score_result
        self.valuation = valuation_result
        self.ai_summary = ai_summary

    def export_to_excel(self):
        try:
            # Safe extraction for Z-Score
            if isinstance(self.z_score, dict):
                z_val = self.z_score.get('Z-Score', 0)
                z_zone = self.z_score.get('Zone', 'N/A')
            else:
                z_val = self.z_score if self.z_score is not None else 0
                z_zone = 'N/A'

            # Safe extraction for Valuation
            if isinstance(self.valuation, dict):
                intrinsic_val = self.valuation.get('Intrinsic Value', 'N/A')
                curr_price = self.valuation.get('Current Price', 'N/A')
                val_status = self.valuation.get('Status', 'N/A')
            else:
                intrinsic_val = 'N/A'
                curr_price = 'N/A'
                val_status = str(self.valuation) if self.valuation is not None else 'N/A'

            # Data structured format
            data = {
                "Metric Category": [
                    "Company Ticker", "Latest Financial Year", "Working Capital", 
                    "Current Ratio", "Debt-to-Equity Ratio", "Altman Z-Score", 
                    "Financial Health Zone", "Estimated Intrinsic Value ($)", 
                    "Current Market Price ($)", "Valuation Status", "Investment Risk"
                ],
                "Values": [
                    self.ticker,
                    self.ratios.get('Latest Year', 'N/A'),
                    self.ratios.get('Working Capital', 0),
                    self.ratios.get('Current Ratio', 0),
                    self.ratios.get('Debt-to-Equity', 0),
                    z_val,
                    z_zone,
                    intrinsic_val,
                    curr_price,
                    val_status,
                    "Managed via AI Pipeline"
                ]
            }

            df = pd.DataFrame(data)
            
            # File name with ticker name
            file_name = f"{self.ticker}_financial_report.xlsx"
            
            # Save to Excel
            df.to_excel(file_name, index=False)
            print(f"[✔] Report successfully exported to Excel: {file_name}")
            return file_name
            
        except Exception as e:
            print(f"Error exporting to Excel: {e}")
            return None
