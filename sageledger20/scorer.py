from .engines.sustainability import SustainabilityEngine
from .engines.growth import GrowthEngine
from .engines.stability import StabilityEngine
from .engines.efficiency import EfficiencyEngine
from .engines.risk import RiskEngine

class Scorer:
    """Aggregates engine scores and enforces Buffett criteria."""
    
    @staticmethod
    def evaluate(processed_data):
        """
        Evaluates a processed FinancialData object containing all indicators.
        Returns a dictionary of scores.
        """
        # We assume processed_data contains the necessary pandas Series as attributes
        # For demonstration, we construct dict with dummy passing
        
        moat = SustainabilityEngine.analyze(processed_data.get('roe'), processed_data.get('op_margin'))
        growth = GrowthEngine.analyze(processed_data.get('revenue'), processed_data.get('net_income'))
        stability = StabilityEngine.analyze(processed_data.get('debt_ratio'), processed_data.get('current_ratio'))
        efficiency = EfficiencyEngine.analyze(processed_data.get('roic'))
        risk_score, anomaly, reason = RiskEngine.analyze(processed_data.get('net_income'), processed_data.get('ocf'))
        
        # Buffett strict criteria check (e.g. 10yr Avg ROE > 15%)
        roe_series = processed_data.get('roe')
        buffett_pass = False
        if roe_series is not None and len(roe_series) >= 10:
            avg_10yr_roe = roe_series.tail(10).mean()
            if avg_10yr_roe >= 0.15:
                buffett_pass = True
        elif roe_series is not None and len(roe_series) > 0:
            avg_roe = roe_series.mean()
            if avg_roe >= 0.15:
               buffett_pass = True
               
        total_score = (moat + growth + stability + efficiency + risk_score) / 5.0
        
        return {
            'moat_score': moat,
            'growth_score': growth,
            'stability_score': stability,
            'efficiency_score': efficiency,
            'risk_score': risk_score,
            'total_score': total_score,
            'buffett_criteria_met': buffett_pass,
            'anomaly_detected': anomaly,
            'anomaly_reason': reason
        }
