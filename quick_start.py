"""
Quick Start Script for Reddit Client Scraper
A simple script to get you started quickly
"""

import os
import sys
from colorama import init, Fore, Style

# Initialize colorama
init()

def check_requirements():
    """Check if required packages are installed"""
    try:
        import praw
        import pandas
        import openpyxl
        return True
    except ImportError:
        return False

def check_env_file():
    """Check if .env file exists and has credentials"""
    if not os.path.exists('.env'):
        return False
    
    with open('.env', 'r') as f:
        content = f.read()
        return 'your_client_id_here' not in content

def main():
    """Main quick start function"""
    print(f"{Fore.CYAN}{'='*60}")
    print("🚀 REDDIT CLIENT SCRAPER - QUICK START")
    print(f"{'='*60}{Style.RESET_ALL}\n")
    
    # Check requirements
    if not check_requirements():
        print(f"{Fore.RED}❌ Missing required packages{Style.RESET_ALL}")
        print("Please run: pip install -r requirements.txt")
        return
    
    print(f"{Fore.GREEN}✅ Required packages installed{Style.RESET_ALL}")
    
    # Check .env file
    if not check_env_file():
        print(f"{Fore.YELLOW}⚠️  Reddit API credentials not configured{Style.RESET_ALL}")
        print("Please:")
        print("1. Get Reddit API credentials from: https://www.reddit.com/prefs/apps")
        print("2. Update the .env file with your credentials")
        return
    
    print(f"{Fore.GREEN}✅ Reddit API credentials configured{Style.RESET_ALL}")
    
    # Ask user what they want to do
    print(f"\n{Fore.CYAN}What would you like to do?{Style.RESET_ALL}")
    print("1. Run basic scraper (fast)")
    print("2. Run advanced scraper (with sentiment analysis)")
    print("3. Run AI-enhanced scraper (with Mistral AI + custom text output)")
    print("4. Set up scheduled scraping")
    print("5. View configuration")
    
    choice = input("\nEnter your choice (1-5): ").strip()
    
    if choice == "1":
        print(f"\n{Fore.GREEN}🚀 Starting basic scraper...{Style.RESET_ALL}")
        os.system("python reddit_scraper.py")
    
    elif choice == "2":
        print(f"\n{Fore.GREEN}🚀 Starting advanced scraper...{Style.RESET_ALL}")
        os.system("python advanced_scraper.py")
    
    elif choice == "3":
        print(f"\n{Fore.GREEN}🚀 Starting AI-enhanced scraper...{Style.RESET_ALL}")
        os.system("python ai_enhanced_scraper.py")
    
    elif choice == "4":
        print(f"\n{Fore.GREEN}🚀 Starting scheduler...{Style.RESET_ALL}")
        os.system("python scheduler.py")
    
    elif choice == "5":
        print(f"\n{Fore.CYAN}Current Configuration:{Style.RESET_ALL}")
        print(f"• Monitoring {len(['entrepreneur', 'smallbusiness', 'startups', 'marketing', 'digitalmarketing', 'webdev', 'freelance', 'forhire', 'business', 'ecommerce', 'shopify', 'woocommerce', 'automation', 'productivity', 'saas', 'sideproject', 'indiehackers', 'entrepreneurridealong', 'businessideas', 'marketing'])} subreddits")
        print("• Looking for digital marketing, web development, and automation clients")
        print("• Minimum post score: 5")
        print("• Minimum comments: 2")
        print("• Maximum post age: 30 days")
        print("\nTo customize, edit config.py")
    
    else:
        print(f"{Fore.RED}Invalid choice{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
