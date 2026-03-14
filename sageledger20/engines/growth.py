from ..indicators import FinancialIndicators

class GrowthEngine:
    """Analyzes revenue and profit CAGR."""
    
    @staticmethod
    def analyze(revenue_series, net_income_series):
        """
        Calculates 10-year or 5-year CAGR for Revenue and Net Income.
        Returns a score out of 100.
        """
        if revenue_series.empty or net_income_series.empty or len(revenue_series) < 2:
            return 0.0
            
        years = len(revenue_series) - 1
        rev_cagr = FinancialIndicators.calculate_cagr(revenue_series.iloc[0], revenue_series.iloc[-1], years)
        ni_cagr = FinancialIndicators.calculate_cagr(net_income_series.iloc[0], net_income_series.iloc[-1], years)
        
        # Scoring logic: 15% CAGR = 50 points each
        rev_score = min(50.0, max(0.0, rev_cagr / 0.15 * 50))
        ni_score = min(50.0, max(0.0, ni_cagr / 0.15 * 50))
        
        return rev_score + ni_score
