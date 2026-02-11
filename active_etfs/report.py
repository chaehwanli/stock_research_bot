from datetime import datetime

class ReportGenerator:
    def __init__(self, title):
        self.title = title
        self.content = f"# {title}\n\n"
        self.content += f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    def add_summary_table(self, results):
        self.content += "## Summary\n\n"
        self.content += "| Ticker | Name | Price | 1Y Return | Dividend |\n"
        self.content += "| --- | --- | --- | --- | --- |\n"
        
        # Sort by 1Y Return descending
        sorted_results = sorted(results, key=lambda x: x.get('1Y Return (%)', 0), reverse=True)
        
        for res in sorted_results:
            self.content += f"| {res['Ticker']} | {res['Name']} | {res['Current Price']:,} | {res['1Y Return (%)']}% | {res['Dividend']} |\n"
        self.content += "\n"

    def add_details(self, results, images_map):
        self.content += "## Details\n\n"
        
        for res in results:
            ticker = res['Ticker']
            self.content += f"### {res['Name']} ({ticker})\n\n"
            self.content += f"- **Current Price**: {res['Current Price']:,}\n"
            self.content += f"- **1Y Return**: {res['1Y Return (%)']}%\n"
            self.content += f"- **1Y Range**: {res['1Y Low']:,} - {res['1Y High']:,}\n"
            self.content += f"- **Avg Volume**: {res['Avg Volume']:,}\n"
            self.content += f"- **Avg Tx Value**: {res['Avg Tx Value']:,}\n"
            self.content += f"- **Dividend**: {res['Dividend']}\n\n"
            
            # Add Images
            if ticker in images_map:
                for img_path in images_map[ticker]:
                    # Assume images are in 'images/' folder relative to the wiki page
                    if "price" in img_path:
                        self.content += f"![Price History](images/{img_path})\n"
                    elif "volume" in img_path:
                        self.content += f"![Volume History](images/{img_path})\n"
            self.content += "\n---\n"

    def get_markdown(self):
        return self.content
