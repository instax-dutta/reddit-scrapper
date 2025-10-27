"""
Advanced Reddit Scraper with Enhanced Features
Includes comment scraping, sentiment analysis, and advanced filtering
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
from textblob import TextBlob
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

from config import (
    REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT,
    REDDIT_USERNAME, REDDIT_PASSWORD, SUBREDDITS,
    DIGITAL_MARKETING_KEYWORDS, WEBSITE_DEVELOPMENT_KEYWORDS,
    AUTOMATION_KEYWORDS, BUSINESS_INDICATORS,
    MIN_SCORE, MIN_COMMENTS, MAX_DAYS_OLD, LIMIT_PER_SUBREDDIT,
    OUTPUT_DIR, CSV_FILENAME, EXCEL_FILENAME
)

# Initialize colorama
init()

# Download required NLTK data
try:
    nltk.download('vader_lexicon', quiet=True)
except:
    pass

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('advanced_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AdvancedRedditScraper:
    def __init__(self):
        """Initialize advanced Reddit scraper with sentiment analysis"""
        try:
            self.reddit = praw.Reddit(
                client_id=REDDIT_CLIENT_ID,
                client_secret=REDDIT_CLIENT_SECRET,
                user_agent=REDDIT_USER_AGENT,
                username=REDDIT_USERNAME,
                password=REDDIT_PASSWORD
            )
            
            # Initialize sentiment analyzer
            self.sia = SentimentIntensityAnalyzer()
            
            # Test connection
            self.reddit.user.me()
            logger.info(f"{Fore.GREEN}✓ Advanced scraper initialized successfully{Style.RESET_ALL}")
            
        except Exception as e:
            logger.error(f"{Fore.RED}✗ Failed to initialize advanced scraper: {e}{Style.RESET_ALL}")
            raise
    
    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze sentiment of text using VADER"""
        scores = self.sia.polarity_scores(text)
        return {
            'positive': scores['pos'],
            'negative': scores['neg'],
            'neutral': scores['neu'],
            'compound': scores['compound']
        }
    
    def extract_budget_indicators(self, text: str) -> Dict[str, str]:
        """Extract budget-related information from text"""
        budget_info = {}
        text_lower = text.lower()
        
        # Budget ranges
        budget_patterns = [
            (r'\$(\d+)\s*-\s*\$(\d+)', 'range'),
            (r'\$(\d+)\s*to\s*\$(\d+)', 'range'),
            (r'budget\s*[:\-]?\s*\$?(\d+)', 'budget'),
            (r'budget\s*[:\-]?\s*\$?(\d+)\s*k', 'budget_k'),
            (r'budget\s*[:\-]?\s*\$?(\d+)\s*thousand', 'budget_k'),
            (r'willing\s*to\s*pay\s*\$?(\d+)', 'willing_pay'),
            (r'can\s*afford\s*\$?(\d+)', 'can_afford'),
            (r'looking\s*to\s*spend\s*\$?(\d+)', 'looking_spend')
        ]
        
        for pattern, budget_type in budget_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                if budget_type == 'range':
                    budget_info['budget_range'] = f"${matches[0][0]} - ${matches[0][1]}"
                elif budget_type == 'budget_k':
                    budget_info['budget'] = f"${matches[0]}k"
                else:
                    budget_info['budget'] = f"${matches[0]}"
                break
        
        return budget_info
    
    def extract_timeline_indicators(self, text: str) -> Dict[str, str]:
        """Extract timeline/urgency information from text"""
        timeline_info = {}
        text_lower = text.lower()
        
        timeline_patterns = [
            (r'asap|as soon as possible', 'urgent'),
            (r'urgent|urgently', 'urgent'),
            (r'deadline\s*[:\-]?\s*(\w+)', 'deadline'),
            (r'need\s*by\s*(\w+)', 'need_by'),
            (r'launch\s*(\w+)', 'launch'),
            (r'by\s*(\w+\s*\d+)', 'by_date'),
            (r'within\s*(\d+)\s*days', 'within_days'),
            (r'within\s*(\d+)\s*weeks', 'within_weeks'),
            (r'within\s*(\d+)\s*months', 'within_months')
        ]
        
        for pattern, timeline_type in timeline_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                timeline_info['timeline'] = matches[0] if matches[0] else timeline_type
                timeline_info['urgency'] = 'high' if timeline_type == 'urgent' else 'medium'
                break
        
        return timeline_info
    
    def scrape_comments(self, post, max_comments: int = 20) -> List[Dict]:
        """Scrape comments from a post for additional context"""
        comments_data = []
        
        try:
            post.comments.replace_more(limit=0)
            comments = post.comments.list()[:max_comments]
            
            for comment in comments:
                if hasattr(comment, 'body') and comment.body != '[deleted]':
                    comment_data = {
                        'comment_id': comment.id,
                        'author': str(comment.author) if comment.author else 'deleted',
                        'body': comment.body,
                        'score': comment.score,
                        'created_utc': datetime.fromtimestamp(comment.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
                        'sentiment': self.analyze_sentiment(comment.body)
                    }
                    comments_data.append(comment_data)
        
        except Exception as e:
            logger.warning(f"Error scraping comments for post {post.id}: {e}")
        
        return comments_data
    
    def calculate_advanced_score(self, post, keywords_found: Set[str], comments_data: List[Dict]) -> int:
        """Calculate advanced relevance score with sentiment and engagement analysis"""
        score = 0
        
        # Base keyword score
        score += len(keywords_found) * 10
        
        # Engagement score
        if post.score > 50:
            score += 30
        elif post.score > 20:
            score += 20
        elif post.score > 10:
            score += 10
        
        if post.num_comments > 20:
            score += 25
        elif post.num_comments > 10:
            score += 15
        elif post.num_comments > 5:
            score += 10
        
        # Sentiment analysis score
        post_text = f"{post.title} {post.selftext}"
        sentiment = self.analyze_sentiment(post_text)
        
        # Boost for positive sentiment (people looking for help)
        if sentiment['compound'] > 0.1:
            score += 15
        elif sentiment['compound'] < -0.1:
            score -= 10  # Negative sentiment might indicate problems
        
        # Comment sentiment analysis
        if comments_data:
            avg_comment_sentiment = sum(c['sentiment']['compound'] for c in comments_data) / len(comments_data)
            if avg_comment_sentiment > 0.1:
                score += 10
        
        # Budget indicators boost
        budget_info = self.extract_budget_indicators(post_text)
        if budget_info:
            score += 20
        
        # Timeline urgency boost
        timeline_info = self.extract_timeline_indicators(post_text)
        if timeline_info.get('urgency') == 'high':
            score += 25
        elif timeline_info.get('urgency') == 'medium':
            score += 15
        
        # Business context boost
        if self.has_business_context(post_text):
            score += 15
        
        # Recent post boost
        if self.is_recent_post(post):
            score += 5
        
        return max(0, score)  # Ensure non-negative score
    
    def has_business_context(self, text: str) -> bool:
        """Check if text contains business-related indicators"""
        text_lower = text.lower()
        return any(indicator.lower() in text_lower for indicator in BUSINESS_INDICATORS)
    
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
    
    def scrape_subreddit_advanced(self, subreddit_name: str, include_comments: bool = True) -> List[Dict]:
        """Advanced scraping of a specific subreddit with comments"""
        logger.info(f"{Fore.CYAN}Advanced scraping r/{subreddit_name}...{Style.RESET_ALL}")
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            potential_clients = []
            
            # Get hot posts
            posts = list(subreddit.hot(limit=LIMIT_PER_SUBREDDIT))
            
            for post in tqdm(posts, desc=f"Advanced processing r/{subreddit_name}"):
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
                    
                    # Scrape comments if requested
                    comments_data = []
                    if include_comments:
                        comments_data = self.scrape_comments(post)
                    
                    # Calculate advanced relevance score
                    relevance_score = self.calculate_advanced_score(post, all_keywords, comments_data)
                    
                    # Extract additional information
                    contact_info = self.extract_contact_info(full_text)
                    budget_info = self.extract_budget_indicators(full_text)
                    timeline_info = self.extract_timeline_indicators(full_text)
                    sentiment = self.analyze_sentiment(full_text)
                    
                    # Determine service categories
                    services_needed = []
                    if marketing_keywords:
                        services_needed.append("Digital Marketing")
                    if webdev_keywords:
                        services_needed.append("Website Development")
                    if automation_keywords:
                        services_needed.append("Business Automation")
                    
                    # Create advanced client record
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
                        'budget': budget_info.get('budget', ''),
                        'budget_range': budget_info.get('budget_range', ''),
                        'timeline': timeline_info.get('timeline', ''),
                        'urgency': timeline_info.get('urgency', ''),
                        'sentiment_positive': sentiment['positive'],
                        'sentiment_negative': sentiment['negative'],
                        'sentiment_neutral': sentiment['neutral'],
                        'sentiment_compound': sentiment['compound'],
                        'business_context': self.has_business_context(full_text),
                        'comment_count_analyzed': len(comments_data),
                        'avg_comment_sentiment': sum(c['sentiment']['compound'] for c in comments_data) / len(comments_data) if comments_data else 0
                    }
                    
                    potential_clients.append(client_data)
                    
                    # Rate limiting
                    time.sleep(0.2)
                    
                except Exception as e:
                    logger.warning(f"Error processing post {post.id}: {e}")
                    continue
            
            logger.info(f"{Fore.GREEN}✓ Advanced scraping found {len(potential_clients)} potential clients in r/{subreddit_name}{Style.RESET_ALL}")
            return potential_clients
            
        except Exception as e:
            logger.error(f"{Fore.RED}✗ Error in advanced scraping r/{subreddit_name}: {e}{Style.RESET_ALL}")
            return []
    
    def scrape_all_advanced(self, include_comments: bool = True) -> List[Dict]:
        """Advanced scraping of all configured subreddits"""
        logger.info(f"{Fore.YELLOW}Starting advanced Reddit scraping across {len(SUBREDDITS)} subreddits...{Style.RESET_ALL}")
        
        all_clients = []
        
        for subreddit in SUBREDDITS:
            try:
                clients = self.scrape_subreddit_advanced(subreddit, include_comments)
                all_clients.extend(clients)
                
                # Rate limiting between subreddits
                time.sleep(3)
                
            except Exception as e:
                logger.error(f"Failed to scrape r/{subreddit}: {e}")
                continue
        
        # Sort by relevance score
        all_clients.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        logger.info(f"{Fore.GREEN}✓ Advanced scraping complete! Found {len(all_clients)} total potential clients{Style.RESET_ALL}")
        return all_clients
    
    def save_advanced_data(self, clients: List[Dict]) -> Tuple[str, str]:
        """Save advanced client data to both CSV and Excel"""
        if not clients:
            logger.warning("No client data to save")
            return None, None
        
        # Create output directory
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        df = pd.DataFrame(clients)
        
        # Save CSV
        csv_filepath = os.path.join(OUTPUT_DIR, 'advanced_' + CSV_FILENAME)
        df.to_csv(csv_filepath, index=False)
        
        # Save Excel with multiple sheets
        excel_filepath = os.path.join(OUTPUT_DIR, 'advanced_' + EXCEL_FILENAME)
        
        with pd.ExcelWriter(excel_filepath, engine='openpyxl') as writer:
            # Main data sheet
            df.to_excel(writer, sheet_name='All Clients', index=False)
            
            # High-priority clients sheet
            high_priority = df[df['relevance_score'] > 50].copy()
            if not high_priority.empty:
                high_priority.to_excel(writer, sheet_name='High Priority', index=False)
            
            # Service-specific sheets
            for service in ['Digital Marketing', 'Website Development', 'Business Automation']:
                service_clients = df[df['services_needed'].str.contains(service, na=False)].copy()
                if not service_clients.empty:
                    service_clients.to_excel(writer, sheet_name=service.replace(' ', '_'), index=False)
            
            # Summary statistics sheet
            summary_data = {
                'Metric': [
                    'Total Clients Found',
                    'High Priority Clients (Score > 50)',
                    'Clients with Budget Info',
                    'Urgent Projects',
                    'Avg Sentiment Score',
                    'Most Active Subreddit'
                ],
                'Value': [
                    len(clients),
                    len(df[df['relevance_score'] > 50]),
                    len(df[df['budget'] != '']),
                    len(df[df['urgency'] == 'high']),
                    round(df['sentiment_compound'].mean(), 3),
                    df['subreddit'].mode().iloc[0] if not df.empty else 'N/A'
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        logger.info(f"{Fore.GREEN}✓ Advanced data saved to {csv_filepath} and {excel_filepath}{Style.RESET_ALL}")
        return csv_filepath, excel_filepath


def main():
    """Main function for advanced scraper"""
    print(f"{Fore.CYAN}{'='*60}")
    print("🚀 ADVANCED REDDIT CLIENT SCRAPER")
    print("Enhanced client discovery with sentiment analysis")
    print(f"{'='*60}{Style.RESET_ALL}\n")
    
    try:
        # Initialize advanced scraper
        scraper = AdvancedRedditScraper()
        
        # Ask user for preferences
        include_comments = input("Include comment analysis? (y/n): ").lower().startswith('y')
        
        # Scrape all subreddits
        clients = scraper.scrape_all_advanced(include_comments)
        
        if clients:
            # Save data
            csv_file, excel_file = scraper.save_advanced_data(clients)
            
            print(f"\n{Fore.GREEN}✓ Advanced scraping completed successfully!{Style.RESET_ALL}")
            print(f"📊 CSV file: {csv_file}")
            print(f"📊 Excel file: {excel_file}")
            
            # Display top prospects
            print(f"\n{Fore.CYAN}Top 3 High-Priority Prospects:{Style.RESET_ALL}")
            for i, client in enumerate(clients[:3], 1):
                print(f"\n{i}. {client['title'][:60]}...")
                print(f"   Score: {client['relevance_score']} | Services: {client['services_needed']}")
                if client['budget']:
                    print(f"   Budget: {client['budget']}")
                if client['urgency']:
                    print(f"   Urgency: {client['urgency']}")
                print(f"   URL: {client['url']}")
        
        else:
            print(f"{Fore.YELLOW}⚠ No potential clients found. Try adjusting the search criteria.{Style.RESET_ALL}")
    
    except Exception as e:
        logger.error(f"{Fore.RED}✗ Advanced scraping failed: {e}{Style.RESET_ALL}")
        print(f"{Fore.RED}✗ Error: {e}{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
