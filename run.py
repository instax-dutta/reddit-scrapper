#!/usr/bin/env python3
"""
Simple Runner for Enhanced Reddit Client Scraper
Just run this to start the enhanced scraper with intelligent replies
"""

import os
import sys
from colorama import init, Fore, Style

# Initialize colorama
init()

def main():
    print(f"{Fore.CYAN}{'='*60}")
    print("🚀 ENHANCED REDDIT CLIENT SCRAPER")
    print("AI-powered client discovery with intelligent replies")
    print(f"{'='*60}{Style.RESET_ALL}\n")
    
    # Check if .env exists
    if not os.path.exists('.env'):
        print(f"{Fore.RED}❌ No .env file found!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Please run: python setup.py{Style.RESET_ALL}")
        return
    
    # Check if enhanced scraper exists
    if not os.path.exists('enhanced_reddit_scraper.py'):
        print(f"{Fore.RED}❌ Enhanced scraper not found!{Style.RESET_ALL}")
        return
    
    print(f"{Fore.GREEN}✅ Starting Enhanced Reddit Scraper...{Style.RESET_ALL}")
    print(f"{Fore.CYAN}This will find potential clients and generate intelligent replies{Style.RESET_ALL}\n")
    
    try:
        # Import and run the enhanced scraper
        import enhanced_reddit_scraper
        enhanced_reddit_scraper.main()
    except ImportError as e:
        print(f"{Fore.RED}❌ Import error: {e}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Please install requirements: pip install -r requirements.txt{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}❌ Error running scraper: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
