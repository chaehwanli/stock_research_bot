import sys
import os

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
import argparse
import pandas as pd
from tesla_like_stocks_in_kospi.screener import TeslaLikeScreener

def main():
    parser = argparse.ArgumentParser(description="Find Tesla-like high volatility stocks in KOSPI.")
    parser.add_argument("--mock", action="store_true", help="Use mock data for testing")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of stocks to scan (for testing)")
    args = parser.parse_args()

    print("=" * 60)
    print(" 🚀 KOSPI 'Tesla-like' Stock Screener")
    print("=" * 60)
    print("Logic based on: tesla_like_stocks_in_kospi/README.md")
    print("- Hard Filter: Avg Daily Amount > 100억 KRW")
    print("- Scoring: Daily Vol (40%) + RSI Vol (30%) + Weekly Vol (30%)")
    print("-" * 60)

    screener = TeslaLikeScreener(use_mock=args.mock)
    
    try:
        df = screener.run(limit=args.limit)
        
        if df.empty:
            print("No results found.")
            return

        print("\n\n🏆 Top 20 Candidates (TVS Ranking)")
        print("=" * 80)
        # Display Columns
        cols = ['rank_tvs', 'ticker', 'name', 'TVS', 'daily_vol', 'rsi_std', 'weekly_vol']
        
        # Add a Rank column
        df['rank_tvs'] = range(1, len(df) + 1)
        
        # Format floating points for display
        display_df = df.copy()
        display_df['TVS'] = display_df['TVS'].map('{:.1f}'.format)
        display_df['daily_vol'] = display_df['daily_vol'].map('{:.4f}'.format)
        display_df['rsi_std'] = display_df['rsi_std'].map('{:.2f}'.format)
        display_df['weekly_vol'] = display_df['weekly_vol'].map('{:.4f}'.format)
        
        # Print
        print(display_df[cols].head(20).to_string(index=False))
        print("=" * 80)
        
        # --- Reporting Pipeline ---
        print("\n\n📊 Generating Report...")
        from tesla_like_stocks_in_kospi.report_generator import TeslaReportGenerator
        from common_modules.publishing.wiki_publisher import WikiPublisher
        from common_modules.notification.telegram_bot import TelegramNotifier
        
        generator = TeslaReportGenerator()
        report_content = generator.generate_report(df) # Pass original df with rank_tvs
        
        print("📝 Publishing to Wiki...")
        wiki = WikiPublisher()
        page_title = f"KOSPI Tesla-like Stocks Candidates ({datetime.now().strftime('%Y-%m-%d')})"
        public_url = wiki.publish_report(report_content, page_title)
        
        if public_url:
            print(f"✅ Wiki Published: {public_url}")
            
            # Notify Telegram
            print("📨 Sending Telegram Notification...")
            bot = TelegramNotifier()
            
            top_1 = df.iloc[0]
            msg = f"🚀 [Tesla-Like Screener] Report Ready!\n"
            msg += f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}\n"
            msg += f"🔍 Found {len(df)} candidates.\n\n"
            msg += f"🥇 Rank #1: {top_1['name']} ({top_1['TVS']:.1f})\n"
            
            # Find Tesla
            tesla = df[df['ticker'] == 'TSLA']
            if not tesla.empty:
                t_rank = tesla.iloc[0]['rank_tvs']
                t_score = tesla.iloc[0]['TVS']
                msg += f"🏎️ Tesla Rank: #{t_rank} ({t_score:.1f})\n"
                
            msg += f"\n👉 Full Report: {public_url}"
            
            bot.send_message(msg)
        else:
            print("⚠️ Wiki publish failed or skipped. Telegram notification aborted.")

    except KeyboardInterrupt:
        print("\nAborted.")
    except Exception as e:
        print(f"\nError occurred: {e}")

if __name__ == "__main__":
    main()
