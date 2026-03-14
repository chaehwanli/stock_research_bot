class RiskEngine:
    """Analyzes risk and anomalies specifically comparing cash flow vs net income."""
    
    @staticmethod
    def analyze(net_income_series, operating_cash_flow_series):
        """
        If net income is positive but operating cash flow is repeatedly negative, it's a red flag.
        Returns a tuple: (score, anomaly_detected, anomaly_reason)
        Score out of 100.
        """
        if net_income_series.empty or operating_cash_flow_series.empty:
            return 0.0, False, None
            
        anomaly_detected = False
        anomaly_reason = None
        
        # Calculate ratio of OCF to Net Income. Should ideally be > 1.0 securely over time.
        # Ensure we align series correctly.
        combined = net_income_series.to_frame('NI').join(operating_cash_flow_series.to_frame('OCF'))
        
        red_flags = 0
        for index, row in combined.tail(5).iterrows():
            if row['NI'] > 0 and row['OCF'] < 0:
                red_flags += 1
                
        if red_flags >= 2:
            anomaly_detected = True
            anomaly_reason = f"Operating Cash Flow was negative while Net Income was positive {red_flags} times in the last 5 years."
            
        score = 100.0
        if anomaly_detected:
            score = 30.0 # Heavy penalty
            
        return score, anomaly_detected, anomaly_reason
