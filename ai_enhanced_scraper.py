"""
AI-Enhanced Reddit Scraper with Custom Text Output
Combines Mistral AI analysis with clean, formatted text output
"""

import praw
import pandas as pd
import re
import time
from datetime import datetime, timedelta
from typing import List, Dict, Set, Tuple
import os
from tqdm import tqdm
import logging
from colorama import init, Fore, Style
import json

from config import (
    REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT,
    REDDIT_USERNAME, REDDIT_PASSWORD, SUBREDDITS,
    DIGITAL_MARKETING_KEYWORDS, WEBSITE_DEVELOPMENT_KEYWORDS,
    AUTOMATION_KEYWORDS, BUSINESS_INDICATORS,
    MIN_SCORE, MIN_COMMENTS, MAX_DAYS_OLD, LIMIT_PER_SUBREDDIT,
    OUTPUT_DIR, MISTRAL_API_KEY, MISTRAL_MODEL, USE_AI_ANALYSIS
)

from ai_analyzer import AIEnhancedAnalyzer

# Initialize colorama
init()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ai_enhanced_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AIEnhancedRedditScraper:
    def __init__(self):
        """Initialize AI-enhanced Reddit scraper"""
        try:
            # Initialize Reddit API
            self.reddit = praw.Reddit(
                client_id=REDDIT_CLIENT_ID,
                client_secret=REDDIT_CLIENT_SECRET,
                user_agent=REDDIT_USER_AGENT,
                username=REDDIT_USERNAME,
                password=REDDIT_PASSWORD
            )
            
            # Test Reddit connection
            self.reddit.user.me()
            logger.info(f"{Fore.GREEN}✓ Reddit API connected successfully{Style.RESET_ALL}")
            
            # Initialize AI analyzer
            self.ai_analyzer = AIEnhancedAnalyzer(MISTRAL_API_KEY, USE_AI_ANALYSIS)
            
            logger.info(f"{Fore.GREEN}✓ AI-Enhanced scraper initialized{Style.RESET_ALL}")
            
        except Exception as e:
            logger.error(f"{Fore.RED}✗ Failed to initialize scraper: {e}{Style.RESET_ALL}")
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
        
        # Phone pattern
        phone_pattern = r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
        phones = re.findall(phone_pattern, text)
        if phones:
            contact_info['phone'] = ''.join(phones[0])
        
        return contact_info
    
    def scrape_subreddit(self, subreddit_name: str) -> List[Dict]:
        """Scrape posts from a specific subreddit with AI analysis"""
        logger.info(f"{Fore.CYAN}AI-Enhanced scraping r/{subreddit_name}...{Style.RESET_ALL}")
        
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
                    
                    # Create basic post data
                    post_data = {
                        'subreddit': subreddit_name,
                        'post_id': post.id,
                        'title': post.title,
                        'content': post.selftext,
                        'author': str(post.author) if post.author else 'deleted',
                        'score': post.score,
                        'comments': post.num_comments,
                        'created_utc': datetime.fromtimestamp(post.created_utc),
                        'url': f"https://reddit.com{post.permalink}",
                        'services_needed': services_needed,
                        'keywords_found': list(all_keywords),
                        'contact_info': contact_info,
                        'business_context': self.has_business_context(full_text)
                    }
                    
                    # Get AI analysis
                    ai_analysis = self.ai_analyzer.analyze_post(post_data)
                    
                    # Combine all data
                    client_data = {
                        **post_data,
                        'ai_analysis': ai_analysis,
                        'final_score': ai_analysis.get('combined_score', 50),
                        'ai_enhanced': ai_analysis.get('ai_enhanced', False)
                    }
                    
                    potential_clients.append(client_data)
                    
                    # Rate limiting
                    time.sleep(0.3)
                    
                except Exception as e:
                    logger.warning(f"Error processing post {post.id}: {e}")
                    continue
            
            logger.info(f"{Fore.GREEN}✓ Found {len(potential_clients)} potential clients in r/{subreddit_name}{Style.RESET_ALL}")
            return potential_clients
            
        except Exception as e:
            logger.error(f"{Fore.RED}✗ Error scraping r/{subreddit_name}: {e}{Style.RESET_ALL}")
            return []
    
    def scrape_all_subreddits(self) -> List[Dict]:
        """Scrape all configured subreddits with AI analysis"""
        logger.info(f"{Fore.YELLOW}Starting AI-enhanced scraping across {len(SUBREDDITS)} subreddits...{Style.RESET_ALL}")
        
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
        
        # Sort by final score
        all_clients.sort(key=lambda x: x['final_score'], reverse=True)
        
        logger.info(f"{Fore.GREEN}✓ AI-enhanced scraping complete! Found {len(all_clients)} total potential clients{Style.RESET_ALL}")
        return all_clients
    
    def generate_custom_text_report(self, clients: List[Dict]) -> str:
        """Generate custom text report in the requested format"""
        if not clients:
            return "No potential clients found."
        
        report = []
        report.append("=" * 80)
        report.append("REDDIT CLIENT LEADS - AI ENHANCED ANALYSIS")
        report.append("=" * 80)
        report.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total leads found: {len(clients)}")
        report.append(f"AI analysis enabled: {self.ai_analyzer.use_ai}")
        report.append("=" * 80)
        report.append("")
        
        for i, client in enumerate(clients, 1):
            report.append(f"LEAD #{i}")
            report.append("-" * 40)
            
            # What they want
            if client.get('ai_analysis', {}).get('ai_analysis'):
                ai_services = client['ai_analysis']['ai_analysis'].get('services_needed', [])
                if ai_services and ai_services != ["Unknown"]:
                    report.append(f"What they want: {', '.join(ai_services)}")
                else:
                    report.append(f"What they want: {', '.join(client.get('services_needed', ['Unknown']))}")
            else:
                report.append(f"What they want: {', '.join(client.get('services_needed', ['Unknown']))}")
            
            # When it was posted
            post_date = client['created_utc'].strftime('%Y-%m-%d %H:%M:%S')
            report.append(f"When it was posted: {post_date}")
            
            # Username/name of the poster
            author = client.get('author', 'Unknown')
            report.append(f"Username/name of the poster: {author}")
            
            # Link to the post
            report.append(f"Link to the post: {client.get('url', 'N/A')}")
            
            # Other contact details if any
            contact_info = client.get('contact_info', {})
            contact_details = []
            
            if contact_info.get('email'):
                contact_details.append(f"Email: {contact_info['email']}")
            if contact_info.get('website'):
                contact_details.append(f"Website: {contact_info['website']}")
            if contact_info.get('phone'):
                contact_details.append(f"Phone: {contact_info['phone']}")
            
            # Add AI-extracted business info if available
            if client.get('ai_analysis', {}).get('ai_business_info'):
                business_info = client['ai_analysis']['ai_business_info']
                if business_info.get('company_name') and business_info['company_name'] != 'Unknown':
                    contact_details.append(f"Company: {business_info['company_name']}")
                if business_info.get('location') and business_info['location'] != 'Unknown':
                    contact_details.append(f"Location: {business_info['location']}")
            
            if contact_details:
                report.append(f"Other contact details: {'; '.join(contact_details)}")
            else:
                report.append("Other contact details: None found")
            
            # Additional AI insights
            if client.get('ai_analysis', {}).get('ai_analysis'):
                ai_analysis = client['ai_analysis']['ai_analysis']
                
                # Budget information
                budget_info = ai_analysis.get('budget_indicators', {})
                if budget_info.get('budget_range') and budget_info['budget_range'] != 'Unknown':
                    report.append(f"Budget indication: {budget_info['budget_range']}")
                
                # Urgency level
                urgency = ai_analysis.get('urgency_level', 'Unknown')
                if urgency != 'Unknown':
                    report.append(f"Urgency level: {urgency}")
                
                # Business maturity
                maturity = ai_analysis.get('business_maturity', 'Unknown')
                if maturity != 'Unknown':
                    report.append(f"Business type: {maturity}")
                
                # Key insights
                insights = ai_analysis.get('key_insights', [])
                if insights and insights != ["AI analysis failed - manual review needed"]:
                    report.append(f"Key insights: {'; '.join(insights[:3])}")  # Limit to 3 insights
                
                # Recommended approach
                approach = ai_analysis.get('recommended_approach', '')
                if approach and approach != 'Standard outreach':
                    report.append(f"Recommended approach: {approach}")
            
            # Engagement metrics
            report.append(f"Post engagement: {client.get('score', 0)} upvotes, {client.get('comments', 0)} comments")
            
            # Final score
            report.append(f"Lead quality score: {client.get('final_score', 0)}/100")
            
            # AI summary if available
            if client.get('ai_analysis', {}).get('ai_summary'):
                summary = client['ai_analysis']['ai_summary'][:200] + "..." if len(client['ai_analysis']['ai_summary']) > 200 else client['ai_analysis']['ai_summary']
                report.append(f"AI Summary: {summary}")
            
            report.append("")
            report.append("=" * 80)
            report.append("")
        
        # Add summary statistics
        report.append("SUMMARY STATISTICS")
        report.append("-" * 40)
        
        # Service breakdown
        service_counts = {}
        for client in clients:
            for service in client.get('services_needed', []):
                service_counts[service] = service_counts.get(service, 0) + 1
        
        report.append("Services needed breakdown:")
        for service, count in sorted(service_counts.items(), key=lambda x: x[1], reverse=True):
            report.append(f"  • {service}: {count} leads")
        
        # High-priority leads
        high_priority = [c for c in clients if c.get('final_score', 0) > 70]
        report.append(f"\nHigh-priority leads (score > 70): {len(high_priority)}")
        
        # Leads with contact info
        with_contact = [c for c in clients if c.get('contact_info', {}).get('email') or c.get('contact_info', {}).get('website')]
        report.append(f"Leads with contact information: {len(with_contact)}")
        
        # AI analysis coverage
        ai_analyzed = [c for c in clients if c.get('ai_enhanced', False)]
        report.append(f"Leads analyzed by AI: {len(ai_analyzed)}")
        
        report.append("")
        report.append("=" * 80)
        report.append("END OF REPORT")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def save_custom_text_report(self, clients: List[Dict]) -> str:
        """Save the custom text report to file"""
        if not clients:
            logger.warning("No client data to save")
            return None
        
        # Create output directory
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        # Generate report
        report_content = self.generate_custom_text_report(clients)
        
        # Save to file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"reddit_client_leads_{timestamp}.txt"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        logger.info(f"{Fore.GREEN}✓ Custom text report saved to {filepath}{Style.RESET_ALL}")
        return filepath
    
    def save_csv_backup(self, clients: List[Dict]) -> str:
        """Save CSV backup for data analysis"""
        if not clients:
            return None
        
        # Flatten the data for CSV
        flattened_clients = []
        for client in clients:
            flat_client = {
                'subreddit': client.get('subreddit', ''),
                'post_id': client.get('post_id', ''),
                'title': client.get('title', ''),
                'content': client.get('content', '')[:500] + "..." if len(client.get('content', '')) > 500 else client.get('content', ''),
                'author': client.get('author', ''),
                'score': client.get('score', 0),
                'comments': client.get('comments', 0),
                'created_utc': client.get('created_utc', datetime.now()).strftime('%Y-%m-%d %H:%M:%S'),
                'url': client.get('url', ''),
                'services_needed': ', '.join(client.get('services_needed', [])),
                'keywords_found': ', '.join(client.get('keywords_found', [])),
                'email': client.get('contact_info', {}).get('email', ''),
                'website': client.get('contact_info', {}).get('website', ''),
                'phone': client.get('contact_info', {}).get('phone', ''),
                'final_score': client.get('final_score', 0),
                'ai_enhanced': client.get('ai_enhanced', False)
            }
            
            # Add AI analysis data if available
            if client.get('ai_analysis', {}).get('ai_analysis'):
                ai_data = client['ai_analysis']['ai_analysis']
                flat_client.update({
                    'ai_client_potential_score': ai_data.get('client_potential_score', 0),
                    'ai_services': ', '.join(ai_data.get('services_needed', [])),
                    'ai_budget_range': ai_data.get('budget_indicators', {}).get('budget_range', ''),
                    'ai_urgency': ai_data.get('urgency_level', ''),
                    'ai_business_maturity': ai_data.get('business_maturity', ''),
                    'ai_decision_maker': ai_data.get('decision_maker', False),
                    'ai_contact_readiness': ai_data.get('contact_readiness', ''),
                    'ai_key_insights': '; '.join(ai_data.get('key_insights', [])),
                    'ai_recommended_approach': ai_data.get('recommended_approach', ''),
                    'ai_opportunity_summary': ai_data.get('opportunity_summary', '')
                })
            
            flattened_clients.append(flat_client)
        
        # Save CSV
        df = pd.DataFrame(flattened_clients)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_filename = f"reddit_client_leads_backup_{timestamp}.csv"
        csv_filepath = os.path.join(OUTPUT_DIR, csv_filename)
        df.to_csv(csv_filepath, index=False)
        
        logger.info(f"{Fore.GREEN}✓ CSV backup saved to {csv_filepath}{Style.RESET_ALL}")
        return csv_filepath


def main():
    """Main function for AI-enhanced scraper"""
    print(f"{Fore.CYAN}{'='*60}")
    print("🚀 AI-ENHANCED REDDIT CLIENT SCRAPER")
    print("Advanced client discovery with Mistral AI analysis")
    print(f"{'='*60}{Style.RESET_ALL}\n")
    
    try:
        # Initialize AI-enhanced scraper
        scraper = AIEnhancedRedditScraper()
        
        # Scrape all subreddits
        clients = scraper.scrape_all_subreddits()
        
        if clients:
            # Save custom text report
            text_file = scraper.save_custom_text_report(clients)
            
            # Save CSV backup
            csv_file = scraper.save_csv_backup(clients)
            
            print(f"\n{Fore.GREEN}✓ AI-enhanced scraping completed successfully!{Style.RESET_ALL}")
            print(f"📄 Main report: {text_file}")
            print(f"📊 CSV backup: {csv_file}")
            
            # Display summary
            high_priority = [c for c in clients if c.get('final_score', 0) > 70]
            with_contact = [c for c in clients if c.get('contact_info', {}).get('email') or c.get('contact_info', {}).get('website')]
            
            print(f"\n{Fore.CYAN}Quick Summary:{Style.RESET_ALL}")
            print(f"• Total leads found: {len(clients)}")
            print(f"• High-priority leads: {len(high_priority)}")
            print(f"• Leads with contact info: {len(with_contact)}")
            print(f"• AI analysis enabled: {scraper.ai_analyzer.use_ai}")
            
            # Show top 3 leads
            print(f"\n{Fore.YELLOW}Top 3 High-Priority Leads:{Style.RESET_ALL}")
            for i, client in enumerate(clients[:3], 1):
                print(f"\n{i}. {client['title'][:60]}...")
                print(f"   Score: {client['final_score']} | Services: {', '.join(client['services_needed'])}")
                if client.get('contact_info', {}).get('email'):
                    print(f"   Email: {client['contact_info']['email']}")
                print(f"   URL: {client['url']}")
        
        else:
            print(f"{Fore.YELLOW}⚠ No potential clients found. Try adjusting the search criteria.{Style.RESET_ALL}")
    
    except Exception as e:
        logger.error(f"{Fore.RED}✗ AI-enhanced scraping failed: {e}{Style.RESET_ALL}")
        print(f"{Fore.RED}✗ Error: {e}{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
