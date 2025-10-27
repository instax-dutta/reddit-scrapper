"""
Scheduled Reddit Scraper
Automatically runs the scraper at specified intervals
"""

import schedule
import time
import logging
from datetime import datetime
from colorama import init, Fore, Style
import os
import sys

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from reddit_scraper import RedditClientScraper
from advanced_scraper import AdvancedRedditScraper

# Initialize colorama
init()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ScheduledScraper:
    def __init__(self, use_advanced: bool = True):
        """Initialize scheduled scraper"""
        self.use_advanced = use_advanced
        self.scraper = AdvancedRedditScraper() if use_advanced else RedditClientScraper()
        
    def run_scraping_job(self):
        """Run the scraping job"""
        try:
            logger.info(f"{Fore.CYAN}🔄 Starting scheduled scraping job at {datetime.now()}{Style.RESET_ALL}")
            
            if self.use_advanced:
                clients = self.scraper.scrape_all_advanced(include_comments=True)
                if clients:
                    csv_file, excel_file = self.scraper.save_advanced_data(clients)
                    logger.info(f"{Fore.GREEN}✓ Scheduled job completed. Found {len(clients)} clients{Style.RESET_ALL}")
                else:
                    logger.warning("No clients found in scheduled run")
            else:
                clients = self.scraper.scrape_all_subreddits()
                if clients:
                    csv_file = self.scraper.save_to_csv(clients)
                    excel_file = self.scraper.save_to_excel(clients)
                    logger.info(f"{Fore.GREEN}✓ Scheduled job completed. Found {len(clients)} clients{Style.RESET_ALL}")
                else:
                    logger.warning("No clients found in scheduled run")
                    
        except Exception as e:
            logger.error(f"{Fore.RED}✗ Scheduled scraping job failed: {e}{Style.RESET_ALL}")
    
    def setup_schedule(self):
        """Setup the scheduling"""
        # Run every 6 hours
        schedule.every(6).hours.do(self.run_scraping_job)
        
        # Run every day at 9 AM
        schedule.every().day.at("09:00").do(self.run_scraping_job)
        
        # Run every Monday at 8 AM (start of work week)
        schedule.every().monday.at("08:00").do(self.run_scraping_job)
        
        logger.info(f"{Fore.GREEN}✓ Schedule configured:{Style.RESET_ALL}")
        logger.info("  • Every 6 hours")
        logger.info("  • Daily at 9:00 AM")
        logger.info("  • Every Monday at 8:00 AM")
    
    def run_scheduler(self):
        """Run the scheduler"""
        self.setup_schedule()
        
        print(f"{Fore.CYAN}{'='*60}")
        print("⏰ REDDIT SCRAPER SCHEDULER")
        print("Automated client discovery running in background")
        print(f"{'='*60}{Style.RESET_ALL}\n")
        
        logger.info("🚀 Scheduler started. Press Ctrl+C to stop.")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info(f"{Fore.YELLOW}⏹ Scheduler stopped by user{Style.RESET_ALL}")
            print(f"\n{Fore.YELLOW}⏹ Scheduler stopped{Style.RESET_ALL}")


def main():
    """Main function for scheduler"""
    print("Choose scraper type:")
    print("1. Basic scraper (faster)")
    print("2. Advanced scraper (with sentiment analysis)")
    
    choice = input("Enter choice (1 or 2): ").strip()
    use_advanced = choice == "2"
    
    scraper_type = "Advanced" if use_advanced else "Basic"
    print(f"\n{Fore.GREEN}✓ Using {scraper_type} scraper{Style.RESET_ALL}")
    
    # Initialize and run scheduler
    scheduled_scraper = ScheduledScraper(use_advanced=use_advanced)
    scheduled_scraper.run_scheduler()


if __name__ == "__main__":
    main()
