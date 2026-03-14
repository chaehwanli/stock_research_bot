import pandas as pd

class FinancialIndicators:
    """Calculates various financial ratios and metrics."""
    
    @staticmethod
    def calculate_roe(net_income: pd.Series, total_equity: pd.Series) -> pd.Series:
        """Return on Equity = Net Income / Total Equity"""
        return (net_income / total_equity).replace([float('inf'), -float('inf')], 0).fillna(0)

    @staticmethod
    def calculate_roic(nopat: pd.Series, invested_capital: pd.Series) -> pd.Series:
        """Return on Invested Capital = NOPAT / Invested Capital"""
        return (nopat / invested_capital).replace([float('inf'), -float('inf')], 0).fillna(0)

    @staticmethod
    def calculate_debt_ratio(total_liabilities: pd.Series, total_equity: pd.Series) -> pd.Series:
        """Debt Ratio = Total Liabilities / Total Equity"""
        return (total_liabilities / total_equity).replace([float('inf'), -float('inf')], 0).fillna(0)

    @staticmethod
    def calculate_current_ratio(current_assets: pd.Series, current_liabilities: pd.Series) -> pd.Series:
        """Current Ratio = Current Assets / Current Liabilities"""
        return (current_assets / current_liabilities).replace([float('inf'), -float('inf')], 0).fillna(0)

    @staticmethod
    def calculate_operating_margin(operating_income: pd.Series, revenue: pd.Series) -> pd.Series:
        """Operating Margin = Operating Income / Revenue"""
        return (operating_income / revenue).replace([float('inf'), -float('inf')], 0).fillna(0)

    @staticmethod
    def calculate_owner_earnings(net_income: pd.Series, depreciation: pd.Series, capex: pd.Series) -> pd.Series:
        """Owner Earnings = Net Income + Depreciation/Amortization - Capital Expenditures"""
        # Note: CAPEX is usually a negative cash flow in statements, so we might need to add it 
        # instead of subtract if it's already negative. We assume capex values are absolute positive here.
        return net_income + depreciation - capex

    @staticmethod
    def calculate_cagr(beginning_value: float, ending_value: float, years: int) -> float:
        """CAGR = (Ending Value / Beginning Value)^(1/years) - 1"""
        if beginning_value <= 0 or ending_value <= 0 or years <= 0:
            return 0.0
        return (ending_value / beginning_value) ** (1 / years) - 1
