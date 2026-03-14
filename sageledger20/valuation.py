class Valuation:
    """Calculates Intrinsic Value and Margin of Safety based on Owner Earnings."""
    
    @staticmethod
    def calculate_intrinsic_value(current_owner_earnings: float, growth_rate: float, discount_rate: float, terminal_multiple: float = 15.0, years: int = 10) -> float:
        """
        Discounted Cash Flow (DCF) logic using Owner Earnings.
        """
        if current_owner_earnings <= 0:
            return 0.0
            
        value = 0.0
        future_earnings = current_owner_earnings
        
        # Project Cash Flows for 'years'
        for i in range(1, years + 1):
            future_earnings *= (1 + growth_rate)
            discounted_cf = future_earnings / ((1 + discount_rate) ** i)
            value += discounted_cf
            
        # Terminal Value
        terminal_value = future_earnings * terminal_multiple
        discounted_tv = terminal_value / ((1 + discount_rate) ** years)
        value += discounted_tv
        
        return value

    @staticmethod
    def calculate_margin_of_safety(intrinsic_value: float, current_market_cap: float) -> float:
        """
        Margin of Safety = (Intrinsic Value - Current Market Cap) / Intrinsic Value
        """
        if intrinsic_value <= 0:
            return 0.0
        return (intrinsic_value - current_market_cap) / intrinsic_value
