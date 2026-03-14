class SustainabilityEngine:
    """Analyzes long-term profitability and economic moat."""
    
    @staticmethod
    def analyze(roe_series, operating_margin_series, years_threshold=10):
        """
        Checks if ROE and Operating Margin have been consistently high (e.g. ROE > 15%, Op Margin > 10%).
        Returns a score out of 100.
        """
        if roe_series is None or roe_series.empty:
            return 0.0
            
        # Consider the last N years
        recent_roe = roe_series.tail(years_threshold)
        recent_margin = operating_margin_series.tail(years_threshold)
        
        roe_score = len(recent_roe[recent_roe > 0.15]) / years_threshold * 50
        margin_score = len(recent_margin[recent_margin > 0.10]) / years_threshold * 50
        
        return min(100.0, roe_score + margin_score)
