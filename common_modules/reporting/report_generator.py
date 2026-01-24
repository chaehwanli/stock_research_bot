from datetime import datetime

class ReportGenerator:
    def __init__(self):
        pass

    def generate_markdown_report(self, stats, candidates, llm_reports):
        """
        Generates a comprehensive Markdown report.
        """
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report = f"# Deep Value Asset Stock Report\n"
        report += f"**Date**: {now}\n\n"
        
        # 1. Executive Summary (Funnel)
        report += "## 1. Screening Summary (Funnel)\n"
        report += "| Stage | Count | Pass Rate (approx) |\n"
        report += "|---|---|---|\n"
        
        total = stats.get('total_scanned', 0)
        pbr = stats.get('passed_pbr', 0)
        profit = stats.get('passed_profit', 0)
        cash = stats.get('passed_cash', 0)
        holder = stats.get('passed_shareholder', 0)
        
        report += f"| Total Scanned | {total} | 100% |\n"
        report += f"| Passed PBR (<= 0.6) | {pbr} | {self._pct(pbr, total)} |\n"
        report += f"| Passed Profit (5yrs > 0) | {profit} | {self._pct(profit, pbr)} |\n"
        report += f"| Passed Cash Ratio (>= 30%) | {cash} | {self._pct(cash, profit)} |\n"
        report += f"| Passed Shareholder (>= 30%) | {holder} | {self._pct(holder, cash)} |\n"
        report += f"| **Final Candidates** | **{stats.get('final_candidates', 0)}** | - |\n\n"
        
        # 2. Candidate List
        report += "## 2. Candidate List\n"
        if not candidates:
            report += "No candidates found.\n\n"
        else:
            report += "| Ticker | Name | PBR | Cash Ratio | Stake |\n"
            report += "|---|---|---|---|---|\n"
            for c in candidates:
                report += f"| {c['ticker']} | {c['name']} | {c['pbr']} | {c['cash_ratio']:.2%} | {c['shareholder_stake']}% |\n"
            report += "\n"

        # 3. Detailed Analysis
        report += "## 3. Operations Analysis (LLM)\n"
        if not llm_reports:
             report += "No analysis available.\n"
        else:
            for rep in llm_reports:
                report += rep + "\n\n---\n\n"
                
        return report

    def _pct(self, num, denom):
        if denom == 0: return "0%"
        return f"{(num/denom):.1%}"
