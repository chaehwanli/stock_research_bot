import os
import matplotlib.pyplot as plt
from common_modules.publishing.wiki_publisher import WikiPublisher

class Reporter:
    """Generates markdown reports and AI anomaly investigation prompts, then publishes them."""
    
    def __init__(self, use_wiki=True):
        self.use_wiki = use_wiki
        self.publisher = WikiPublisher() if use_wiki else None

    def generate_ai_prompt(self, anomaly_reason: str, ticker: str) -> str:
        """
        Creates a prompt for an LLM to investigate the detected anomaly.
        """
        return f"The financial analysis engine detected an anomaly for {ticker}: '{anomaly_reason}'. " \
               "Please analyze the company's recent earnings call transcripts and business context " \
               "to explain why this occurred and whether it poses a structural threat."

    def _create_chart(self, title: str, series_dict: dict, filename: str, report_dir: str) -> str:
        """
        Creates a line chart for the given series and saves it.
        Returns the relative path for markdown embedding.
        """
        import matplotlib.ticker as ticker
        
        fig, ax = plt.subplots(figsize=(12, 6))
        for label, series in series_dict.items():
            if series is not None and not series.empty:
                # Convert index to numeric or string that plots cleanly
                ax.plot(series.index.astype(str), series.values, marker='o', label=label)
                
        ax.set_title(title)
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.legend()
        
        plt.xticks(rotation=45, ha='right')
        ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=20, integer=True))
        plt.tight_layout()
        
        # Save locally in reports/images/
        images_dir = os.path.join(report_dir, "images")
        os.makedirs(images_dir, exist_ok=True)
        
        filepath = os.path.join(images_dir, filename)
        plt.savefig(filepath)
        plt.close()
        
        # Return path relative to the report file (i.e., 'images/...')
        return f"images/{filename}", filepath

    def generate_charts(self, ticker: str, processed_data: dict, report_dir: str, timestamp: str = ""):
        """
        Generates all charts and returns a dict mapping engine to relative chart path, and a list of absolute paths.
        """
        charts = {}
        abs_paths = []
        suffix = f"_{timestamp}" if timestamp else ""
        
        # 1. Moat: ROE, Op Margin
        rel, abs_p = self._create_chart(f"{ticker} - Sustainability (Moat)", 
                                        {'ROE': processed_data.get('c_roe'), 'Operating Margin': processed_data.get('c_op_margin')},
                                        f"{ticker}_moat{suffix}.png", report_dir)
        charts['moat'] = rel
        abs_paths.append(abs_p)
        
        # 2. Growth: Revenue, Net Income
        rel, abs_p = self._create_chart(f"{ticker} - Growth", 
                                        {'Revenue': processed_data.get('c_revenue'), 'Net Income': processed_data.get('c_net_income')},
                                        f"{ticker}_growth{suffix}.png", report_dir)
        charts['growth'] = rel
        abs_paths.append(abs_p)
        
        # 3. Stability: Debt Ratio, Current Ratio
        rel, abs_p = self._create_chart(f"{ticker} - Financial Stability", 
                                        {'Debt Ratio': processed_data.get('c_debt_ratio'), 'Current Ratio': processed_data.get('c_current_ratio')},
                                        f"{ticker}_stability{suffix}.png", report_dir)
        charts['stability'] = rel
        abs_paths.append(abs_p)

        # 4. Efficiency: ROIC
        rel, abs_p = self._create_chart(f"{ticker} - Capital Efficiency", 
                                        {'ROIC': processed_data.get('c_roic')},
                                        f"{ticker}_efficiency{suffix}.png", report_dir)
        charts['efficiency'] = rel
        abs_paths.append(abs_p)

        # 5. Risk: Net Income vs OCF
        rel, abs_p = self._create_chart(f"{ticker} - Risk (Earnings Quality)", 
                                        {'Net Income': processed_data.get('c_net_income'), 'Operating Cash Flow': processed_data.get('c_ocf')},
                                        f"{ticker}_risk{suffix}.png", report_dir)
        charts['risk'] = rel
        abs_paths.append(abs_p)
        
        return charts, abs_paths

    def create_markdown_report(self, ticker: str, scores: dict, charts: dict = None, processed_data: dict = None) -> str:
        """
        Formats the evaluation results into a clean Markdown document.
        """
        charts = charts or {}
        
        md = f"# SageLedger20 Analysis Report: {ticker}\n\n"
        md += "## Overall Evaluation\n"
        md += f"- **Total Score**: {scores['total_score']:.1f} / 100\n"
        md += f"- **Buffett Criteria Met**: {'✅ Yes' if scores['buffett_criteria_met'] else '❌ No'}\n"
        
        md += "\n## Core Engine Scores (핵심 엔진 평가)\n"
        
        md += "### 🏰 Moat (기업의 해자 및 지속가능성)\n"
        md += f"**Score: {scores['moat_score']:.1f} / 100**\n"
        md += "> 기업이 장기적으로 경쟁 우위를 유지하며 꾸준한 수익(ROE, 영업이익률)을 내고 있는지 평가합니다.\n\n"
        if 'moat' in charts: md += f"![Moat Chart]({charts['moat']})\n\n"
        
        md += "### 📈 Growth (성장성)\n"
        md += f"**Score: {scores['growth_score']:.1f} / 100**\n"
        md += "> 과거 10년간 매출과 순이익이 얼마나 꾸준히 복리로 성장(CAGR)해 왔는지 평가합니다.\n\n"
        if 'growth' in charts: md += f"![Growth Chart]({charts['growth']})\n\n"
        
        md += "### 🛡️ Financial Stability (재무 안정성)\n"
        md += f"**Score: {scores['stability_score']:.1f} / 100**\n"
        md += "> 부채 비율과 유동 비율을 분석하여 경제 위기에도 파산하지 않고 버틸 수 있는 안전한 재무 상태인지 평가합니다.\n\n"
        if 'stability' in charts: md += f"![Stability Chart]({charts['stability']})\n\n"
        
        md += "### ⚙️ Capital Efficiency (자본 효율성)\n"
        md += f"**Score: {scores['efficiency_score']:.1f} / 100**\n"
        md += "> 경영진이 주주들의 자본(ROIC)을 얼마나 효율적으로 재투자하여 이익을 창출하고 있는지 평가합니다.\n\n"
        if 'efficiency' in charts: md += f"![Efficiency Chart]({charts['efficiency']})\n\n"
        
        md += "### ⚠️ Risk (위험도 및 분식회계 가능성)\n"
        md += f"**Score: {scores['risk_score']:.1f} / 100**\n"
        md += "> 장부상 이익(당기순이익)과 실제 들어온 현금(영업현금흐름)을 비교하여 재무 리스크나 회계 조작 가능성이 없는지 확인합니다.\n\n"
        if 'risk' in charts: md += f"![Risk Chart]({charts['risk']})\n\n"

        if scores['anomaly_detected']:
            md += "\n## ⚠️ Anomaly Detected\n"
            md += f"{scores['anomaly_reason']}\n\n"
            md += "### Recommended AI Investigation Prompt\n"
            prompt = self.generate_ai_prompt(scores['anomaly_reason'], ticker)
            md += f"> {prompt}\n"
            
        if processed_data:
            md += "\n## 📊 Raw Historical Data\n\n"
            table_dict = {
                'Revenue': processed_data.get('c_revenue'),
                'Net Income': processed_data.get('c_net_income'),
                'OCF': processed_data.get('c_ocf'),
                'ROE': processed_data.get('c_roe'),
                'Op Margin': processed_data.get('c_op_margin'),
                'Debt Ratio': processed_data.get('c_debt_ratio'),
                'Current Ratio': processed_data.get('c_current_ratio'),
                'ROIC': processed_data.get('c_roic')
            }
            # Remove empty series
            table_dict = {k: v for k, v in table_dict.items() if v is not None}
            
            if table_dict:
                import pandas as pd
                df = pd.DataFrame(table_dict)
                df.index = df.index.astype(str)
                try: 
                    df = df.sort_index()
                except: 
                    pass
                
                columns = ['Period'] + list(df.columns)
                md += "| " + " | ".join(columns) + " |\n"
                md += "| " + " | ".join(["---"] * len(columns)) + " |\n"
                
                for idx, row in df.iterrows():
                    # Check if index has specific formats and crop dates like '2024-03-31 00:00:00' to just '2024-03-31'
                    clean_idx = str(idx)[:10] if len(str(idx)) >= 10 and '-' in str(idx) else str(idx)
                    row_str = f"| {clean_idx} "
                    
                    for col in df.columns:
                        val = row[col]
                        if pd.isna(val):
                            row_str += "| - "
                        elif isinstance(val, (int, float)):
                            if any(x in col for x in ["Ratio", "Margin", "ROE", "ROIC"]):
                                row_str += f"| {val:.2%} "
                            elif abs(val) > 1000:
                                row_str += f"| {val:,.0f} "
                            else:
                                row_str += f"| {val:.2f} "
                        else:
                            row_str += f"| {val} "
                    row_str += "|\n"
                    md += row_str

        md += "\n---\n*Generated by SageLedger20*"
        return md

    def publish(self, ticker: str, scores: dict, processed_data: dict, report_dir: str, timestamp: str = ""):
        """
        Creates and conditionally publishes the report to the Wiki.
        """
        charts, abs_paths = self.generate_charts(ticker, processed_data, report_dir, timestamp)
        report_content = self.create_markdown_report(ticker, scores, charts, processed_data)
        
        if self.use_wiki and self.publisher:
            page_title = f"SageLedger20 Report - {ticker}"
            url = self.publisher.publish_report(report_content, page_title, attachments=abs_paths)
            return True, url, report_content
            
        return False, None, report_content
