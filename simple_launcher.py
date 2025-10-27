"""
Simple Launcher for Enhanced Reddit Client Scraper
No external dependencies - just basic Python
"""

import os
import sys
from colorama import init, Fore, Style

# Initialize colorama
init()


def show_welcome():
    """Display welcome screen"""
    print("\n" + "="*80)
    print(f"{Fore.BLUE}🚀 ENHANCED REDDIT CLIENT SCRAPER{Style.RESET_ALL}")
    print("="*80)
    print(f"{Fore.CYAN}Find potential clients and generate intelligent replies to win business!{Style.RESET_ALL}")
    print()
    print(f"{Fore.YELLOW}Features:{Style.RESET_ALL}")
    print("• AI-powered client analysis and scoring")
    print("• Personalized reply generation")
    print("• Automated reply posting (optional)")
    print("• Custom text reports in your format")
    print("• Lead tracking and management")
    print("="*80)


def check_requirements():
    """Check if all requirements are installed"""
    print(f"\n{Fore.CYAN}🔍 Checking requirements...{Style.RESET_ALL}")
    
    missing_packages = []
    
    try:
        import praw
        print(f"{Fore.GREEN}✓ Reddit API (praw){Style.RESET_ALL}")
    except ImportError:
        missing_packages.append("praw")
        print(f"{Fore.RED}✗ Reddit API (praw){Style.RESET_ALL}")
    
    try:
        import mistralai
        print(f"{Fore.GREEN}✓ AI analysis (mistralai){Style.RESET_ALL}")
    except ImportError:
        missing_packages.append("mistralai")
        print(f"{Fore.RED}✗ AI analysis (mistralai){Style.RESET_ALL}")
    
    if missing_packages:
        print(f"\n{Fore.YELLOW}⚠ Missing packages: {', '.join(missing_packages)}{Style.RESET_ALL}")
        response = input("Install missing packages? (y/n): ").lower()
        if response.startswith('y'):
            print(f"{Fore.CYAN}Installing packages...{Style.RESET_ALL}")
            os.system("pip install -r requirements.txt")
            print(f"{Fore.GREEN}✓ Installation complete!{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}Cannot proceed without required packages{Style.RESET_ALL}")
            return False
    
    print(f"{Fore.GREEN}✓ All requirements satisfied!{Style.RESET_ALL}")
    return True


def check_configuration():
    """Check if configuration is set up"""
    print(f"\n{Fore.CYAN}⚙️ Checking configuration...{Style.RESET_ALL}")
    
    config_issues = []
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        config_issues.append("No .env file found")
        print(f"{Fore.RED}✗ .env file not found{Style.RESET_ALL}")
    else:
        print(f"{Fore.GREEN}✓ .env file exists{Style.RESET_ALL}")
        
        # Check for placeholder values
        with open('.env', 'r') as f:
            content = f.read()
            if 'your_client_id_here' in content:
                config_issues.append("Reddit API credentials not configured")
                print(f"{Fore.YELLOW}⚠ Reddit API credentials need configuration{Style.RESET_ALL}")
            else:
                print(f"{Fore.GREEN}✓ Reddit API configured{Style.RESET_ALL}")
            
            if 'your_mistral_api_key_here' in content:
                config_issues.append("Mistral AI API key not configured")
                print(f"{Fore.YELLOW}⚠ Mistral AI API key needs configuration{Style.RESET_ALL}")
            else:
                print(f"{Fore.GREEN}✓ Mistral AI configured{Style.RESET_ALL}")
    
    if config_issues:
        print(f"\n{Fore.YELLOW}⚠ Configuration issues found:{Style.RESET_ALL}")
        for issue in config_issues:
            print(f"  • {issue}")
        
        response = input("Open configuration guide? (y/n): ").lower()
        if response.startswith('y'):
            show_configuration_guide()
        return False
    
    print(f"{Fore.GREEN}✓ Configuration looks good!{Style.RESET_ALL}")
    return True


def show_configuration_guide():
    """Display configuration guide"""
    print(f"\n{Fore.CYAN}📋 Configuration Guide:{Style.RESET_ALL}")
    
    print(f"\n{Fore.BLUE}1. Reddit API Setup:{Style.RESET_ALL}")
    print("   • Go to: https://www.reddit.com/prefs/apps")
    print("   • Click 'Create App' or 'Create Another App'")
    print("   • Choose 'script' as app type")
    print("   • Copy Client ID and Secret to .env file")
    
    print(f"\n{Fore.BLUE}2. Mistral AI Setup:{Style.RESET_ALL}")
    print("   • Go to: https://console.mistral.ai/")
    print("   • Sign up and get your API key")
    print("   • Add API key to .env file")
    
    print(f"\n{Fore.BLUE}3. Auto-Reply Settings:{Style.RESET_ALL}")
    print("   • ENABLE_AUTO_REPLY: Set to 'true' to enable automatic replies")
    print("   • REPLY_DRY_RUN: Set to 'true' for testing (won't post actual replies)")
    print("   • MAX_REPLIES_PER_SESSION: Limit replies per scraping session")
    
    print(f"\n{Fore.YELLOW}After configuration, restart the launcher.{Style.RESET_ALL}")


def show_main_menu():
    """Display main menu options"""
    print(f"\n{Fore.CYAN}🎯 What would you like to do?{Style.RESET_ALL}")
    print()
    print("1. 🚀 Run Enhanced Reddit Scraper (Recommended)")
    print("2. 🔍 Run Basic Reddit Scraper")
    print("3. 🤖 Run AI-Enhanced Reddit Scraper")
    print("4. ⚙️ Configuration & Setup")
    print("5. 📊 View Previous Results")
    print("6. ❓ Help & Documentation")
    print("7. 🚪 Exit")
    print()
    
    while True:
        try:
            choice = input("Enter your choice (1-7): ").strip()
            if choice in ['1', '2', '3', '4', '5', '6', '7']:
                return choice
            else:
                print(f"{Fore.RED}Please enter a number between 1 and 7{Style.RESET_ALL}")
        except KeyboardInterrupt:
            return '7'


def launch_enhanced_scraper():
    """Launch the enhanced Reddit scraper"""
    print(f"\n{Fore.GREEN}🚀 Launching Enhanced Reddit Scraper...{Style.RESET_ALL}")
    try:
        os.system("python enhanced_reddit_scraper.py")
    except Exception as e:
        print(f"{Fore.RED}Error launching enhanced scraper: {e}{Style.RESET_ALL}")


def launch_basic_scraper():
    """Launch basic Reddit scraper"""
    print(f"\n{Fore.GREEN}🔍 Launching Basic Reddit Scraper...{Style.RESET_ALL}")
    try:
        os.system("python reddit_scraper.py")
    except Exception as e:
        print(f"{Fore.RED}Error launching basic scraper: {e}{Style.RESET_ALL}")


def launch_ai_enhanced_scraper():
    """Launch AI-enhanced Reddit scraper"""
    print(f"\n{Fore.GREEN}🤖 Launching AI-Enhanced Reddit Scraper...{Style.RESET_ALL}")
    try:
        os.system("python ai_enhanced_scraper.py")
    except Exception as e:
        print(f"{Fore.RED}Error launching AI-enhanced scraper: {e}{Style.RESET_ALL}")


def show_previous_results():
    """Show previous scraping results"""
    print(f"\n{Fore.CYAN}📊 Previous Results:{Style.RESET_ALL}")
    
    output_dir = "output"
    if not os.path.exists(output_dir):
        print(f"{Fore.YELLOW}No output directory found{Style.RESET_ALL}")
        return
    
    files = os.listdir(output_dir)
    if not files:
        print(f"{Fore.YELLOW}No previous results found{Style.RESET_ALL}")
        return
    
    # Group files by type
    csv_files = [f for f in files if f.endswith('.csv')]
    excel_files = [f for f in files if f.endswith('.xlsx')]
    text_files = [f for f in files if f.endswith('.txt')]
    
    if csv_files:
        print(f"\n{Fore.GREEN}CSV Files ({len(csv_files)}):{Style.RESET_ALL}")
        for file in sorted(csv_files)[-5:]:  # Show last 5
            print(f"  • {file}")
    
    if excel_files:
        print(f"\n{Fore.GREEN}Excel Files ({len(excel_files)}):{Style.RESET_ALL}")
        for file in sorted(excel_files)[-5:]:  # Show last 5
            print(f"  • {file}")
    
    if text_files:
        print(f"\n{Fore.GREEN}Text Reports ({len(text_files)}):{Style.RESET_ALL}")
        for file in sorted(text_files)[-5:]:  # Show last 5
            print(f"  • {file}")
    
    response = input("Open output directory? (y/n): ").lower()
    if response.startswith('y'):
        if sys.platform == "darwin":  # macOS
            os.system(f"open {output_dir}")
        elif sys.platform == "win32":  # Windows
            os.system(f"explorer {output_dir}")
        else:  # Linux
            os.system(f"xdg-open {output_dir}")


def show_help():
    """Display help and documentation"""
    print(f"\n{Fore.CYAN}❓ Help & Documentation:{Style.RESET_ALL}")
    
    print(f"\n{Fore.BLUE}What is this tool?{Style.RESET_ALL}")
    print("This is an enhanced Reddit client discovery scraper that finds potential")
    print("clients seeking digital marketing, website development, and business")
    print("automation services. It can also generate intelligent, personalized")
    print("replies to help you win more business.")
    
    print(f"\n{Fore.BLUE}Key Features:{Style.RESET_ALL}")
    print(f"• {Fore.RED}Reddit Scraping{Style.RESET_ALL} - Finds relevant posts across multiple subreddits")
    print(f"• {Fore.BLUE}AI Analysis{Style.RESET_ALL} - Intelligent lead scoring and qualification")
    print(f"• {Fore.GREEN}Reply Generation{Style.RESET_ALL} - Personalized responses to win clients")
    print(f"• {Fore.YELLOW}Automation{Style.RESET_ALL} - Optional automatic reply posting")
    print(f"• {Fore.MAGENTA}Custom Reports{Style.RESET_ALL} - Text reports in your requested format")
    
    print(f"\n{Fore.BLUE}Service Categories:{Style.RESET_ALL}")
    print("• Digital Marketing (SEO, PPC, Social Media, Content Marketing)")
    print("• Website Development (Custom Sites, E-commerce, WordPress)")
    print("• Business Automation (Workflow, API Integration, Process Optimization)")
    
    print(f"\n{Fore.BLUE}Getting Started:{Style.RESET_ALL}")
    print("1. Configure Reddit API credentials in .env file")
    print("2. Configure Mistral AI API key for intelligent analysis")
    print("3. Set auto-reply preferences (start with dry run mode)")
    print("4. Run the enhanced scraper")
    print("5. Review generated replies and results")
    print("6. Follow up with high-scoring leads")
    
    print(f"\n{Fore.BLUE}Safety Features:{Style.RESET_ALL}")
    print("• Dry run mode for testing replies without posting")
    print("• Rate limiting to avoid spam detection")
    print("• Reply limits per session")
    print("• AI-powered quality filtering")
    
    print(f"\n{Fore.YELLOW}For detailed setup instructions, see README.md{Style.RESET_ALL}")


def main():
    """Main launcher function"""
    show_welcome()
    
    # Check requirements
    if not check_requirements():
        return
    
    # Check configuration
    config_ok = check_configuration()
    
    while True:
        try:
            choice = show_main_menu()
            
            if choice == '7':  # Exit
                print(f"\n{Fore.BLUE}👋 Goodbye!{Style.RESET_ALL}")
                break
            
            elif choice == '1':  # Enhanced Scraper
                if config_ok:
                    launch_enhanced_scraper()
                else:
                    print(f"{Fore.RED}Please configure your credentials first{Style.RESET_ALL}")
            
            elif choice == '2':  # Basic Scraper
                if config_ok:
                    launch_basic_scraper()
                else:
                    print(f"{Fore.RED}Please configure your credentials first{Style.RESET_ALL}")
            
            elif choice == '3':  # AI-Enhanced Scraper
                if config_ok:
                    launch_ai_enhanced_scraper()
                else:
                    print(f"{Fore.RED}Please configure your credentials first{Style.RESET_ALL}")
            
            elif choice == '4':  # Configuration
                show_configuration_guide()
                config_ok = check_configuration()  # Re-check after guide
            
            elif choice == '5':  # Previous Results
                show_previous_results()
            
            elif choice == '6':  # Help
                show_help()
            
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Operation cancelled by user{Style.RESET_ALL}")
            break
        except Exception as e:
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
