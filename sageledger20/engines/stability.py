class StabilityEngine:
    """Analyzes debt levels and interest coverage."""
    
    @staticmethod
    def analyze(debt_ratio_series, current_ratio_series):
        """
        Evaluates financial stability based on low debt and high liquidity.
        Returns a score out of 100.
        """
        if debt_ratio_series.empty or current_ratio_series.empty:
            return 0.0
            
        latest_debt_ratio = debt_ratio_series.iloc[-1]
        latest_current_ratio = current_ratio_series.iloc[-1]
        
        # Scoring logic:
        # Debt Ratio < 0.5 (50%) gets 50 points, > 1.0 gets 0 points
        debt_score = max(0.0, 50 - (latest_debt_ratio * 50))
        if latest_debt_ratio > 1.0: debt_score = 0
            
        # Current Ratio > 1.5 gets 50 points, < 1.0 gets 0 points
        current_score = min(50.0, max(0.0, (latest_current_ratio - 1.0) / 0.5 * 50))
        
        return debt_score + current_score
