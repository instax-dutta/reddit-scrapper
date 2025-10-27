"""
Simple Launcher for Enhanced Reddit Client Scraper
Easy-to-use interface for Reddit client discovery with intelligent replies
"""

import os
import sys
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
import inquirer
from colorama import init, Fore, Style

# Initialize colorama and rich console
init()
console = Console()


def show_welcome():
    """Display welcome screen"""
    console.print("\n" + "="*80)
    console.print(Panel.fit(
        "[bold blue]🚀 ENHANCED REDDIT CLIENT SCRAPER[/bold blue]\n\n"
        "[cyan]Find potential clients and generate intelligent replies to win business![/cyan]\n\n"
        "[yellow]Features:[/yellow]\n"
        "• AI-powered client analysis and scoring\n"
        "• Personalized reply generation\n"
        "• Automated reply posting (optional)\n"
        "• Custom text reports in your format\n"
        "• Lead tracking and management",
        border_style="blue"
    ))
    console.print("="*80)


def check_requirements():
    """Check if all requirements are installed"""
    console.print("\n[cyan]🔍 Checking requirements...[/cyan]")
    
    missing_packages = []
    
    try:
        import praw
        console.print("[green]✓ Reddit API (praw)[/green]")
    except ImportError:
        missing_packages.append("praw")
        console.print("[red]✗ Reddit API (praw)[/red]")
    
    try:
        import mistralai
        console.print("[green]✓ AI analysis (mistralai)[/green]")
    except ImportError:
        missing_packages.append("mistralai")
        console.print("[red]✗ AI analysis (mistralai)[/red]")
    
    try:
        import rich
        console.print("[green]✓ Rich UI (rich)[/green]")
    except ImportError:
        missing_packages.append("rich")
        console.print("[red]✗ Rich UI (rich)[/red]")
    
    if missing_packages:
        console.print(f"\n[yellow]⚠ Missing packages: {', '.join(missing_packages)}[/yellow]")
        if Confirm.ask("Install missing packages?"):
            console.print("[cyan]Installing packages...[/cyan]")
            os.system("pip install -r requirements.txt")
            console.print("[green]✓ Installation complete![/green]")
            return True
        else:
            console.print("[red]Cannot proceed without required packages[/red]")
            return False
    
    console.print("[green]✓ All requirements satisfied![/green]")
    return True


def check_configuration():
    """Check if configuration is set up"""
    console.print("\n[cyan]⚙️ Checking configuration...[/cyan]")
    
    config_issues = []
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        config_issues.append("No .env file found")
        console.print("[red]✗ .env file not found[/red]")
    else:
        console.print("[green]✓ .env file exists[/green]")
        
        # Check for placeholder values
        with open('.env', 'r') as f:
            content = f.read()
            if 'your_client_id_here' in content:
                config_issues.append("Reddit API credentials not configured")
                console.print("[yellow]⚠ Reddit API credentials need configuration[/yellow]")
            else:
                console.print("[green]✓ Reddit API configured[/green]")
            
            if 'your_mistral_api_key_here' in content:
                config_issues.append("Mistral AI API key not configured")
                console.print("[yellow]⚠ Mistral AI API key needs configuration[/yellow]")
            else:
                console.print("[green]✓ Mistral AI configured[/green]")
    
    if config_issues:
        console.print(f"\n[yellow]⚠ Configuration issues found:[/yellow]")
        for issue in config_issues:
            console.print(f"  • {issue}")
        
        if Confirm.ask("Open configuration guide?"):
            show_configuration_guide()
        return False
    
    console.print("[green]✓ Configuration looks good![/green]")
    return True


def show_configuration_guide():
    """Display configuration guide"""
    console.print("\n[cyan]📋 Configuration Guide:[/cyan]")
    
    console.print("\n[bold]1. Reddit API Setup:[/bold]")
    console.print("   • Go to: https://www.reddit.com/prefs/apps")
    console.print("   • Click 'Create App' or 'Create Another App'")
    console.print("   • Choose 'script' as app type")
    console.print("   • Copy Client ID and Secret to .env file")
    
    console.print("\n[bold]2. Mistral AI Setup:[/bold]")
    console.print("   • Go to: https://console.mistral.ai/")
    console.print("   • Sign up and get your API key")
    console.print("   • Add API key to .env file")
    
    console.print("\n[bold]3. Auto-Reply Settings:[/bold]")
    console.print("   • ENABLE_AUTO_REPLY: Set to 'true' to enable automatic replies")
    console.print("   • REPLY_DRY_RUN: Set to 'true' for testing (won't post actual replies)")
    console.print("   • MAX_REPLIES_PER_SESSION: Limit replies per scraping session")
    
    console.print("\n[yellow]After configuration, restart the launcher.[/yellow]")


def show_main_menu():
    """Display main menu options"""
    console.print("\n[cyan]🎯 What would you like to do?[/cyan]")
    
    questions = [
        inquirer.List(
            'action',
            message="Select an option:",
            choices=[
                '🚀 Run Enhanced Reddit Scraper (Recommended)',
                '🔍 Run Basic Reddit Scraper',
                '🤖 Run AI-Enhanced Reddit Scraper',
                '⚙️ Configuration & Setup',
                '📊 View Previous Results',
                '❓ Help & Documentation',
                '🚪 Exit'
            ]
        )
    ]
    
    answers = inquirer.prompt(questions)
    return answers['action'] if answers else '🚪 Exit'


def launch_enhanced_scraper():
    """Launch the enhanced Reddit scraper"""
    console.print("\n[green]🚀 Launching Enhanced Reddit Scraper...[/green]")
    try:
        os.system("python enhanced_reddit_scraper.py")
    except Exception as e:
        console.print(f"[red]Error launching enhanced scraper: {e}[/red]")


def launch_basic_scraper():
    """Launch basic Reddit scraper"""
    console.print("\n[green]🔍 Launching Basic Reddit Scraper...[/green]")
    try:
        os.system("python reddit_scraper.py")
    except Exception as e:
        console.print(f"[red]Error launching basic scraper: {e}[/red]")


def launch_ai_enhanced_scraper():
    """Launch AI-enhanced Reddit scraper"""
    console.print("\n[green]🤖 Launching AI-Enhanced Reddit Scraper...[/green]")
    try:
        os.system("python ai_enhanced_scraper.py")
    except Exception as e:
        console.print(f"[red]Error launching AI-enhanced scraper: {e}[/red]")


def show_previous_results():
    """Show previous scraping results"""
    console.print("\n[cyan]📊 Previous Results:[/cyan]")
    
    output_dir = "output"
    if not os.path.exists(output_dir):
        console.print("[yellow]No output directory found[/yellow]")
        return
    
    files = os.listdir(output_dir)
    if not files:
        console.print("[yellow]No previous results found[/yellow]")
        return
    
    # Group files by type
    csv_files = [f for f in files if f.endswith('.csv')]
    excel_files = [f for f in files if f.endswith('.xlsx')]
    text_files = [f for f in files if f.endswith('.txt')]
    
    if csv_files:
        console.print(f"\n[green]CSV Files ({len(csv_files)}):[/green]")
        for file in sorted(csv_files)[-5:]:  # Show last 5
            console.print(f"  • {file}")
    
    if excel_files:
        console.print(f"\n[green]Excel Files ({len(excel_files)}):[/green]")
        for file in sorted(excel_files)[-5:]:  # Show last 5
            console.print(f"  • {file}")
    
    if text_files:
        console.print(f"\n[green]Text Reports ({len(text_files)}):[/green]")
        for file in sorted(text_files)[-5:]:  # Show last 5
            console.print(f"  • {file}")
    
    if Confirm.ask("Open output directory?"):
        if sys.platform == "darwin":  # macOS
            os.system(f"open {output_dir}")
        elif sys.platform == "win32":  # Windows
            os.system(f"explorer {output_dir}")
        else:  # Linux
            os.system(f"xdg-open {output_dir}")


def show_help():
    """Display help and documentation"""
    console.print("\n[cyan]❓ Help & Documentation:[/cyan]")
    
    console.print("\n[bold]What is this tool?[/bold]")
    console.print("This is an enhanced Reddit client discovery scraper that finds potential")
    console.print("clients seeking digital marketing, website development, and business")
    console.print("automation services. It can also generate intelligent, personalized")
    console.print("replies to help you win more business.")
    
    console.print("\n[bold]Key Features:[/bold]")
    console.print("• [red]Reddit Scraping[/red] - Finds relevant posts across multiple subreddits")
    console.print("• [blue]AI Analysis[/blue] - Intelligent lead scoring and qualification")
    console.print("• [green]Reply Generation[/green] - Personalized responses to win clients")
    console.print("• [yellow]Automation[/yellow] - Optional automatic reply posting")
    console.print("• [magenta]Custom Reports[/magenta] - Text reports in your requested format")
    
    console.print("\n[bold]Service Categories:[/bold]")
    console.print("• Digital Marketing (SEO, PPC, Social Media, Content Marketing)")
    console.print("• Website Development (Custom Sites, E-commerce, WordPress)")
    console.print("• Business Automation (Workflow, API Integration, Process Optimization)")
    
    console.print("\n[bold]Getting Started:[/bold]")
    console.print("1. Configure Reddit API credentials in .env file")
    console.print("2. Configure Mistral AI API key for intelligent analysis")
    console.print("3. Set auto-reply preferences (start with dry run mode)")
    console.print("4. Run the enhanced scraper")
    console.print("5. Review generated replies and results")
    console.print("6. Follow up with high-scoring leads")
    
    console.print("\n[bold]Safety Features:[/bold]")
    console.print("• Dry run mode for testing replies without posting")
    console.print("• Rate limiting to avoid spam detection")
    console.print("• Reply limits per session")
    console.print("• AI-powered quality filtering")
    
    console.print("\n[yellow]For detailed setup instructions, see README.md[/yellow]")


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
            action = show_main_menu()
            
            if action == '🚪 Exit':
                console.print("\n[blue]👋 Goodbye![/blue]")
                break
            
            elif action == '🚀 Run Enhanced Reddit Scraper (Recommended)':
                if config_ok:
                    launch_enhanced_scraper()
                else:
                    console.print("[red]Please configure your credentials first[/red]")
            
            elif action == '🔍 Run Basic Reddit Scraper':
                if config_ok:
                    launch_basic_scraper()
                else:
                    console.print("[red]Please configure your credentials first[/red]")
            
            elif action == '🤖 Run AI-Enhanced Reddit Scraper':
                if config_ok:
                    launch_ai_enhanced_scraper()
                else:
                    console.print("[red]Please configure your credentials first[/red]")
            
            elif action == '⚙️ Configuration & Setup':
                show_configuration_guide()
                config_ok = check_configuration()  # Re-check after guide
            
            elif action == '📊 View Previous Results':
                show_previous_results()
            
            elif action == '❓ Help & Documentation':
                show_help()
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Operation cancelled by user[/yellow]")
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")


if __name__ == "__main__":
    main()
