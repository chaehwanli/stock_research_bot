from dataclasses import dataclass
from typing import Dict, List, Optional
import pandas as pd

@dataclass
class FinancialData:
    ticker: str
    income_statement: pd.DataFrame
    balance_sheet: pd.DataFrame
    cash_flow: pd.DataFrame
    
@dataclass
class AnalysisResult:
    ticker: str
    owner_earnings: pd.Series
    cagr: float
    moat_score: float
    growth_score: float
    stability_score: float
    efficiency_score: float
    risk_score: float
    total_score: float
    intrinsic_value: float
    margin_of_safety: float
    anomaly_detected: bool
    anomaly_reason: Optional[str]
