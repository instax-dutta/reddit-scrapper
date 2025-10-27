"""
Reddit Scraper for Finding Potential Clients
Scrapes Reddit posts and comments to identify potential clients for:
- Digital Marketing Services
- Website Development
- Business Process Automation
"""

import praw
import pandas as pd
import re
import time
from datetime import datetime, timedelta
from typing import List, Dict, Set
import os
from tqdm import tqdm
import logging
from colorama import init, Fore, Style

from config import (
    REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT,
    REDDIT_USERNAME, REDDIT_PASSWORD, SUBREDDITS,
    DIGITAL_MARKETING_KEYWORDS, WEBSITE_DEVELOPMENT_KEYWORDS,
    AUTOMATION_KEYWORDS, BUSINESS_INDICATORS,
    MIN_SCORE, MIN_COMMENTS, MAX_DAYS_OLD, LIMIT_PER_SUBREDDIT,
    OUTPUT_DIR, CSV_FILENAME, EXCEL_FILENAME
)

# Initialize colorama for colored output
init()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('reddit_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class RedditClientScraper:
    def __init__(self):
        """Initialize Reddit API connection"""
        try:
            self.reddit = praw.Reddit(
                client_id=REDDIT_CLIENT_ID,
                client_secret=REDDIT_CLIENT_SECRET,
                user_agent=REDDIT_USER_AGENT,
                username=REDDIT_USERNAME,
                password=REDDIT_PASSWORD
            )
            
            # Test connection
            self.reddit.user.me()
            logger.info(f"{Fore.GREEN}✓ Successfully connected to Reddit API{Style.RESET_ALL}")
            
        except Exception as e:
            logger.error(f"{Fore.RED}✗ Failed to connect to Reddit API: {e}{Style.RESET_ALL}")
            raise
    
    def is_recent_post(self, post) -> bool:
        """Check if post is within the specified time range"""
        post_time = datetime.fromtimestamp(post.created_utc)
        cutoff_time = datetime.now() - timedelta(days=MAX_DAYS_OLD)
        return post_time >= cutoff_time
    
    def extract_keywords(self, text: str, keyword_lists: List[List[str]]) -> Set[str]:
        """Extract matching keywords from text"""
        found_keywords = set()
        text_lower = text.lower()
        
        for keyword_list in keyword_lists:
            for keyword in keyword_list:
                if keyword.lower() in text_lower:
                    found_keywords.add(keyword)
        
        return found_keywords
    
    def has_business_context(self, text: str) -> bool:
        """Check if text contains business-related indicators"""
        text_lower = text.lower()
        return any(indicator.lower() in text_lower for indicator in BUSINESS_INDICATORS)
    
    def calculate_relevance_score(self, post, keywords_found: Set[str]) -> int:
        """Calculate relevance score based on various factors"""
        score = 0
        
        # Base score from keywords found
        score += len(keywords_found) * 10
        
        # Boost for high engagement
        if post.score > 20:
            score += 20
        elif post.score > 10:
            score += 10
        
        if post.num_comments > 10:
            score += 15
        elif post.num_comments > 5:
            score += 10
        
        # Boost for business context
        if self.has_business_context(post.title + " " + post.selftext):
            score += 15
        
        # Boost for recent posts
        if self.is_recent_post(post):
            score += 5
        
        return score
    
    def extract_contact_info(self, text: str) -> Dict[str, str]:
        """Extract potential contact information from text"""
        contact_info = {}
        
        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            contact_info['email'] = emails[0]
        
        # Website/URL pattern
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, text)
        if urls:
            contact_info['website'] = urls[0]
        
        # Phone pattern (basic)
        phone_pattern = r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
        phones = re.findall(phone_pattern, text)
        if phones:
            contact_info['phone'] = ''.join(phones[0])
        
        return contact_info
    
    def scrape_subreddit(self, subreddit_name: str) -> List[Dict]:
        """Scrape posts from a specific subreddit"""
        logger.info(f"{Fore.CYAN}Scraping r/{subreddit_name}...{Style.RESET_ALL}")
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            potential_clients = []
            
            # Get hot posts
            posts = list(subreddit.hot(limit=LIMIT_PER_SUBREDDIT))
            
            for post in tqdm(posts, desc=f"Processing r/{subreddit_name}"):
                try:
                    # Skip if post doesn't meet basic criteria
                    if (post.score < MIN_SCORE or 
                        post.num_comments < MIN_COMMENTS or 
                        not self.is_recent_post(post)):
                        continue
                    
                    # Combine title and content
                    full_text = f"{post.title} {post.selftext}"
                    
                    # Extract keywords
                    marketing_keywords = self.extract_keywords(full_text, [DIGITAL_MARKETING_KEYWORDS])
                    webdev_keywords = self.extract_keywords(full_text, [WEBSITE_DEVELOPMENT_KEYWORDS])
                    automation_keywords = self.extract_keywords(full_text, [AUTOMATION_KEYWORDS])
                    
                    all_keywords = marketing_keywords | webdev_keywords | automation_keywords
                    
                    # Skip if no relevant keywords found
                    if not all_keywords:
                        continue
                    
                    # Calculate relevance score
                    relevance_score = self.calculate_relevance_score(post, all_keywords)
                    
                    # Extract contact information
                    contact_info = self.extract_contact_info(full_text)
                    
                    # Determine service categories
                    services_needed = []
                    if marketing_keywords:
                        services_needed.append("Digital Marketing")
                    if webdev_keywords:
                        services_needed.append("Website Development")
                    if automation_keywords:
                        services_needed.append("Business Automation")
                    
                    # Create client record
                    client_data = {
                        'subreddit': subreddit_name,
                        'post_id': post.id,
                        'title': post.title,
                        'content': post.selftext[:500] + "..." if len(post.selftext) > 500 else post.selftext,
                        'author': str(post.author) if post.author else 'deleted',
                        'score': post.score,
                        'comments': post.num_comments,
                        'created_utc': datetime.fromtimestamp(post.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
                        'url': f"https://reddit.com{post.permalink}",
                        'services_needed': ', '.join(services_needed),
                        'keywords_found': ', '.join(all_keywords),
                        'relevance_score': relevance_score,
                        'email': contact_info.get('email', ''),
                        'website': contact_info.get('website', ''),
                        'phone': contact_info.get('phone', ''),
                        'business_context': self.has_business_context(full_text)
                    }
                    
                    potential_clients.append(client_data)
                    
                    # Rate limiting
                    time.sleep(0.1)
                    
                except Exception as e:
                    logger.warning(f"Error processing post {post.id}: {e}")
                    continue
            
            logger.info(f"{Fore.GREEN}✓ Found {len(potential_clients)} potential clients in r/{subreddit_name}{Style.RESET_ALL}")
            return potential_clients
            
        except Exception as e:
            logger.error(f"{Fore.RED}✗ Error scraping r/{subreddit_name}: {e}{Style.RESET_ALL}")
            return []
    
    def scrape_all_subreddits(self) -> List[Dict]:
        """Scrape all configured subreddits"""
        logger.info(f"{Fore.YELLOW}Starting Reddit scraping across {len(SUBREDDITS)} subreddits...{Style.RESET_ALL}")
        
        all_clients = []
        
        for subreddit in SUBREDDITS:
            try:
                clients = self.scrape_subreddit(subreddit)
                all_clients.extend(clients)
                
                # Rate limiting between subreddits
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Failed to scrape r/{subreddit}: {e}")
                continue
        
        # Sort by relevance score
        all_clients.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        logger.info(f"{Fore.GREEN}✓ Scraping complete! Found {len(all_clients)} total potential clients{Style.RESET_ALL}")
        return all_clients
    
    def save_to_csv(self, clients: List[Dict]) -> str:
        """Save client data to CSV file"""
        if not clients:
            logger.warning("No client data to save")
            return None
        
        # Create output directory if it doesn't exist
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        df = pd.DataFrame(clients)
        filepath = os.path.join(OUTPUT_DIR, CSV_FILENAME)
        df.to_csv(filepath, index=False)
        
        logger.info(f"{Fore.GREEN}✓ Client data saved to {filepath}{Style.RESET_ALL}")
        return filepath
    
    def save_to_excel(self, clients: List[Dict]) -> str:
        """Save client data to Excel file with formatting"""
        if not clients:
            logger.warning("No client data to save")
            return None
        
        # Create output directory if it doesn't exist
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        df = pd.DataFrame(clients)
        filepath = os.path.join(OUTPUT_DIR, EXCEL_FILENAME)
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Potential Clients', index=False)
            
            # Get the workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets['Potential Clients']
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        logger.info(f"{Fore.GREEN}✓ Client data saved to {filepath}{Style.RESET_ALL}")
        return filepath
    
    def generate_summary_report(self, clients: List[Dict]) -> str:
        """Generate a summary report of findings"""
        if not clients:
            return "No potential clients found."
        
        # Calculate statistics
        total_clients = len(clients)
        high_score_clients = len([c for c in clients if c['relevance_score'] > 50])
        
        # Service breakdown
        service_counts = {}
        for client in clients:
            for service in client['services_needed'].split(', '):
                service = service.strip()
                if service:
                    service_counts[service] = service_counts.get(service, 0) + 1
        
        # Subreddit breakdown
        subreddit_counts = {}
        for client in clients:
            subreddit = client['subreddit']
            subreddit_counts[subreddit] = subreddit_counts.get(subreddit, 0) + 1
        
        # Generate report
        report = f"""
{Fore.CYAN}=== REDDIT CLIENT SCRAPING SUMMARY ==={Style.RESET_ALL}

{Fore.YELLOW}Total Potential Clients Found: {total_clients}{Style.RESET_ALL}
{Fore.YELLOW}High-Relevance Clients (Score > 50): {high_score_clients}{Style.RESET_ALL}

{Fore.CYAN}Services Needed Breakdown:{Style.RESET_ALL}
"""
        for service, count in sorted(service_counts.items(), key=lambda x: x[1], reverse=True):
            report += f"  • {service}: {count} clients\n"
        
        report += f"\n{Fore.CYAN}Top Subreddits for Client Discovery:{Style.RESET_ALL}\n"
        for subreddit, count in sorted(subreddit_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            report += f"  • r/{subreddit}: {count} clients\n"
        
        report += f"\n{Fore.GREEN}Top 5 High-Priority Prospects:{Style.RESET_ALL}\n"
        for i, client in enumerate(clients[:5], 1):
            report += f"  {i}. {client['title'][:60]}... (Score: {client['relevance_score']})\n"
            report += f"     r/{client['subreddit']} | {client['services_needed']}\n"
            if client['email']:
                report += f"     Email: {client['email']}\n"
            report += f"     URL: {client['url']}\n\n"
        
        return report


def main():
    """Main function to run the scraper"""
    print(f"{Fore.CYAN}{'='*60}")
    print("🚀 REDDIT CLIENT SCRAPER")
    print("Finding potential clients for your digital services")
    print(f"{'='*60}{Style.RESET_ALL}\n")
    
    try:
        # Initialize scraper
        scraper = RedditClientScraper()
        
        # Scrape all subreddits
        clients = scraper.scrape_all_subreddits()
        
        if clients:
            # Save data
            csv_file = scraper.save_to_csv(clients)
            excel_file = scraper.save_to_excel(clients)
            
            # Generate and display summary
            summary = scraper.generate_summary_report(clients)
            print(summary)
            
            print(f"{Fore.GREEN}✓ Scraping completed successfully!{Style.RESET_ALL}")
            print(f"📊 Data saved to: {csv_file}")
            print(f"📊 Excel file: {excel_file}")
            
        else:
            print(f"{Fore.YELLOW}⚠ No potential clients found. Try adjusting the search criteria.{Style.RESET_ALL}")
    
    except Exception as e:
        logger.error(f"{Fore.RED}✗ Scraping failed: {e}{Style.RESET_ALL}")
        print(f"{Fore.RED}✗ Error: {e}{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
