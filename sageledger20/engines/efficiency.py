class EfficiencyEngine:
    """Analyzes capital allocation efficiency (ROIC)."""
    
    @staticmethod
    def analyze(roic_series):
        """
        Evaluates if ROIC is consistently above cost of capital (assumed 10%).
        Returns a score out of 100.
        """
        if roic_series.empty:
            return 0.0
            
        # Target ROIC is 15% for max points
        avg_roic = roic_series.mean()
        
        if avg_roic < 0.10:
            return 0.0
            
        score = min(100.0, (avg_roic - 0.10) / 0.05 * 100)
        return score
