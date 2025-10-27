"""
Enhanced Reddit Client Scraper with Intelligent Reply Generation
Finds potential clients and generates personalized, lucrative replies to win business
"""

import praw
import pandas as pd
import re
import time
import random
from datetime import datetime, timedelta
from typing import List, Dict, Set, Optional
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
    OUTPUT_DIR, MISTRAL_API_KEY, MISTRAL_MODELS, USE_AI_ANALYSIS,
    ENABLE_AUTO_REPLY, REPLY_DELAY_MIN, REPLY_DELAY_MAX, 
    MAX_REPLIES_PER_SESSION, REPLY_DRY_RUN,
    REPLY_TEMPLATES, YOUR_SERVICES, YOUR_EXPERIENCE
)

from mistral_multi_model_analyzer import MistralMultiModelAnalyzer

# Initialize colorama
init()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_reddit_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class EnhancedRedditClientScraper:
    def __init__(self):
        """Initialize enhanced Reddit scraper with reply capabilities"""
        try:
            # Initialize Reddit API
            self.reddit = praw.Reddit(
                client_id=REDDIT_CLIENT_ID,
                client_secret=REDDIT_CLIENT_SECRET,
                user_agent=REDDIT_USER_AGENT,
                username=REDDIT_USERNAME,
                password=REDDIT_PASSWORD
            )
            
            # Test connection
            self.reddit.user.me()
            logger.info(f"{Fore.GREEN}✓ Reddit API connected successfully{Style.RESET_ALL}")
            
            # Initialize Mistral multi-model AI analyzer
            self.ai_analyzer = MistralMultiModelAnalyzer(MISTRAL_API_KEY, MISTRAL_MODELS) if MISTRAL_API_KEY and USE_AI_ANALYSIS else None
            
            # Reply tracking
            self.replies_sent = 0
            self.reply_history = []
            self.user_reply_cooldown = {}  # Track when we last replied to each user
            
            logger.info(f"{Fore.GREEN}✓ Enhanced Reddit scraper initialized{Style.RESET_ALL}")
            
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
    
    def extract_budget_indicators(self, text: str) -> Dict[str, str]:
        """Extract budget-related information from text"""
        budget_info = {}
        text_lower = text.lower()
        
        # Budget patterns
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
    
    def determine_service_category(self, keywords: Set[str]) -> str:
        """Determine the primary service category based on keywords"""
        marketing_count = len(keywords.intersection(set(DIGITAL_MARKETING_KEYWORDS)))
        webdev_count = len(keywords.intersection(set(WEBSITE_DEVELOPMENT_KEYWORDS)))
        automation_count = len(keywords.intersection(set(AUTOMATION_KEYWORDS)))
        
        if marketing_count >= webdev_count and marketing_count >= automation_count:
            return 'digital_marketing'
        elif webdev_count >= automation_count:
            return 'website_development'
        else:
            return 'business_automation'
    
    def generate_personalized_reply(self, post_data: Dict, ai_analysis: Dict = None) -> str:
        """Generate a personalized, lucrative reply for a Reddit post"""
        try:
            # Determine service category
            keywords = set(post_data.get('keywords_found', []))
            service_category = self.determine_service_category(keywords)
            
            # Get templates for this service category
            templates = REPLY_TEMPLATES.get(service_category, REPLY_TEMPLATES['digital_marketing'])
            
            # Extract post information
            title = post_data.get('title', '')
            content = post_data.get('content', '')
            author = post_data.get('author', '')
            subreddit = post_data.get('subreddit', '')
            
            # Get AI insights if available
            ai_insights = {}
            if ai_analysis:
                ai_insights = {
                    'budget': ai_analysis.get('budget_indicators', {}).get('budget_range', ''),
                    'urgency': ai_analysis.get('urgency_level', ''),
                    'business_type': ai_analysis.get('business_maturity', ''),
                    'industry': 'your industry'  # Could be extracted from AI analysis
                }
            
            # Build personalized reply
            reply_parts = []
            
            # Opening
            opening = random.choice(templates['opening'])
            reply_parts.append(opening)
            
            # Add specific value proposition
            value_prop = random.choice(templates['value_prop'])
            
            # Personalize value proposition
            if service_category == 'digital_marketing':
                service = random.choice(YOUR_SERVICES['digital_marketing'])
                metric = random.choice(['conversion rates', 'website traffic', 'lead generation', 'ROI'])
                percentage = random.choice(['25-40%', '150-300%', '200%', '35%'])
                strategy = random.choice(['data-driven approach', 'conversion-focused strategy', 'multi-channel approach'])
                business_type = ai_insights.get('business_type', 'businesses like yours')
                industry = ai_insights.get('industry', 'your industry')
                
                value_prop = value_prop.format(
                    service=service,
                    metric=metric,
                    percentage=percentage,
                    strategy=strategy,
                    business_type=business_type,
                    industry=industry
                )
            
            elif service_category == 'website_development':
                technology = random.choice(['modern web technologies', 'responsive design', 'performance optimization'])
                project_type = random.choice(['websites', 'e-commerce sites', 'landing pages'])
                result = random.choice(['increased conversions', 'better user experience', 'higher search rankings'])
                speed = random.choice(['2', '3', '2.5'])
                percentage = random.choice(['25%', '40%', '30%'])
                business_impact = random.choice(['doubled their online sales', 'increased lead generation by 200%', 'improved user engagement significantly'])
                
                value_prop = value_prop.format(
                    technology=technology,
                    project_type=project_type,
                    result=result,
                    speed=speed,
                    percentage=percentage,
                    business_impact=business_impact
                )
            
            elif service_category == 'business_automation':
                business_type = ai_insights.get('business_type', 'businesses')
                time_saved = random.choice(['10-20 hours', '15 hours', '8-12 hours'])
                process = random.choice(['data entry', 'customer follow-up', 'report generation'])
                percentage = random.choice(['70%', '80%', '60%'])
                workflow = random.choice(['customer onboarding', 'inventory management', 'lead nurturing'])
                manual_task = random.choice(['manual data entry', 'repetitive email sending', 'manual report creation'])
                metric = random.choice(['efficiency', 'accuracy', 'productivity'])
                
                value_prop = value_prop.format(
                    business_type=business_type,
                    time_saved=time_saved,
                    process=process,
                    percentage=percentage,
                    workflow=workflow,
                    manual_task=manual_task,
                    metric=metric
                )
            
            reply_parts.append(value_prop)
            
            # Add specific mention of their situation
            if 'startup' in content.lower() or 'new business' in content.lower():
                reply_parts.append("I understand the challenges of getting a new business off the ground and can help you establish a strong foundation.")
            elif 'growing' in content.lower() or 'scale' in content.lower():
                reply_parts.append("Scaling a business requires strategic thinking, and I can help you implement systems that grow with you.")
            elif 'struggling' in content.lower() or 'help' in content.lower():
                reply_parts.append("I've helped many businesses overcome similar challenges and would love to help you succeed too.")
            
            # Add credibility
            reply_parts.append(f"With {YOUR_EXPERIENCE['years_experience']} years of experience working with {', '.join(YOUR_EXPERIENCE['industries'][:3])} businesses, I bring proven strategies to the table.")
            
            # Closing
            closing = random.choice(templates['closing'])
            reply_parts.append(closing)
            
            # Add helpful closing (no promotional language)
            if ai_insights.get('urgency') == 'high':
                reply_parts.append("Given the urgency of your project, I'd be happy to share more specific strategies that could help.")
            else:
                reply_parts.append("I'd be happy to elaborate on any of these approaches if you find them helpful.")
            
            # Combine all parts
            full_reply = " ".join(reply_parts)
            
            # Ensure reply is not too long (Reddit has character limits)
            if len(full_reply) > 1000:
                # Truncate while keeping it natural
                full_reply = full_reply[:950] + "..."
            
            # Check for promotional language that might trigger automoderation
            if self._contains_promotional_language(full_reply):
                logger.warning(f"{Fore.YELLOW}⚠ Reply contains promotional language, using fallback{Style.RESET_ALL}")
                return self.generate_fallback_reply(post_data)
            
            return full_reply
            
        except Exception as e:
            logger.error(f"Error generating personalized reply: {e}")
            return self.generate_fallback_reply(post_data)
    
    def _contains_promotional_language(self, text: str) -> bool:
        """Check if text contains promotional language that might trigger automoderation"""
        promotional_phrases = [
            'dm me', 'message me', 'contact me', 'reach out', 'get in touch',
            'free consultation', 'free audit', 'free proposal', 'free call',
            'schedule a call', 'book a call', 'let\'s connect', 'let\'s chat',
            'portfolio', 'case studies', 'references', 'testimonials',
            'hire me', 'work with me', 'collaborate', 'partnership',
            'my services', 'my company', 'my business', 'my agency',
            'check out', 'visit my', 'see my work', 'view my',
            'no obligation', 'no commitment', 'risk-free'
        ]
        
        text_lower = text.lower()
        for phrase in promotional_phrases:
            if phrase in text_lower:
                return True
        
        return False

    def generate_fallback_reply(self, post_data: Dict) -> str:
        """Generate a simple fallback reply if AI generation fails"""
        service_category = self.determine_service_category(set(post_data.get('keywords_found', [])))
        
        if service_category == 'digital_marketing':
            return ("This is a common challenge many businesses face. For digital marketing, I usually recommend starting with SEO and Google Ads as they tend to work well. "
                   "The key is focusing on conversion rates and measuring results consistently. "
                   "Happy to share more details about what's worked in similar situations if you're interested.")
        
        elif service_category == 'website_development':
            return ("This is a great project idea! For web development, I usually recommend modern frameworks like React or WordPress depending on your needs. "
                   "The key is focusing on user experience and performance. "
                   "Happy to share more technical details about the approach if you're interested.")
        
        else:  # business_automation
            return ("This is a common challenge that many businesses face. For automation, I usually recommend starting with the most repetitive tasks first. "
                   "The key is identifying workflows that can be streamlined and building reliable systems. "
                   "Happy to share more details about automation approaches if you're interested.")
    
    def should_reply_to_post(self, post_data: Dict, ai_analysis: Dict = None) -> bool:
        """Determine if we should reply to this post"""
        # Don't reply if we've already reached the limit
        if self.replies_sent >= MAX_REPLIES_PER_SESSION:
            return False
        
        # Don't reply to our own posts
        if post_data.get('author') == REDDIT_USERNAME:
            return False
        
        # Check if we've already replied to this post
        post_id = post_data.get('post_id')
        if post_id in self.reply_history:
            return False
        
        # Check if we've replied to this user recently (24-hour cooldown)
        author = post_data.get('author', '')
        if author and author != '[deleted]' and author != REDDIT_USERNAME:
            current_time = time.time()
            last_reply_time = self.user_reply_cooldown.get(author, 0)
            if current_time - last_reply_time < 86400:  # 24 hours
                logger.info(f"{Fore.YELLOW}⚠ Skipping reply to {author} - cooldown active{Style.RESET_ALL}")
                return False
        
        # Check AI analysis for reply recommendation
        if ai_analysis and ai_analysis.get('client_potential_score'):
            client_score = ai_analysis.get('client_potential_score', 0)
            decision_maker = ai_analysis.get('decision_maker', False)
            contact_readiness = ai_analysis.get('contact_readiness', 'low')
            
            # Only reply to high-potential clients
            if client_score < 60:
                return False
            
            # Prefer decision makers
            if not decision_maker and client_score < 80:
                return False
            
            # Prefer clients ready for contact
            if contact_readiness == 'low' and client_score < 75:
                return False
        
        # Check basic criteria
        score = post_data.get('score', 0)
        comments = post_data.get('comments', 0)
        
        # Only reply to posts with decent engagement
        if score < 3 and comments < 2:
            return False
        
        return True
    
    def post_reply(self, post, reply_text: str) -> bool:
        """Post a reply to a Reddit post"""
        try:
            if REPLY_DRY_RUN:
                logger.info(f"{Fore.YELLOW}[DRY RUN] Would post reply to {post.id}:{Style.RESET_ALL}")
                logger.info(f"{Fore.CYAN}Reply: {reply_text[:100]}...{Style.RESET_ALL}")
                return True
            
            # Post the reply
            comment = post.reply(reply_text)
            
            # Track the reply
            self.replies_sent += 1
            self.reply_history.append(post.id)
            
            # Track user cooldown
            author = post.author.name if post.author else 'unknown'
            self.user_reply_cooldown[author] = time.time()
            
            logger.info(f"{Fore.GREEN}✓ Posted reply to {post.id} (Reply #{self.replies_sent}){Style.RESET_ALL}")
            
            # Add delay between replies to avoid spam detection
            delay = random.randint(REPLY_DELAY_MIN, REPLY_DELAY_MAX)
            logger.info(f"{Fore.YELLOW}Waiting {delay} seconds before next reply...{Style.RESET_ALL}")
            time.sleep(delay)
            
            return True
            
        except Exception as e:
            logger.error(f"{Fore.RED}✗ Failed to post reply to {post.id}: {e}{Style.RESET_ALL}")
            return False
    
    def scrape_subreddit_with_replies(self, subreddit_name: str) -> List[Dict]:
        """Scrape posts from a specific subreddit and generate replies"""
        logger.info(f"{Fore.CYAN}Enhanced scraping r/{subreddit_name}...{Style.RESET_ALL}")
        
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
                    budget_info = self.extract_budget_indicators(full_text)
                    
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
                        'budget_info': budget_info,
                        'business_context': self.has_business_context(full_text)
                    }
                    
                    # Get AI analysis
                    ai_analysis = self.ai_analyzer.analyze_client_potential(post_data) if self.ai_analyzer else {}
                    
                    # Combine all data
                    client_data = {
                        **post_data,
                        'ai_analysis': ai_analysis,
                        'final_score': ai_analysis.get('client_potential_score', 50),
                        'ai_enhanced': bool(self.ai_analyzer)
                    }
                    
                    potential_clients.append(client_data)
                    
                    # Generate and post reply if conditions are met
                    if ENABLE_AUTO_REPLY and self.should_reply_to_post(client_data, ai_analysis):
                        reply_text = self.generate_personalized_reply(client_data, ai_analysis)
                        success = self.post_reply(post, reply_text)
                        
                        # Add reply information to client data
                        client_data['reply_generated'] = True
                        client_data['reply_text'] = reply_text
                        client_data['reply_posted'] = success
                    else:
                        client_data['reply_generated'] = False
                        client_data['reply_text'] = ''
                        client_data['reply_posted'] = False
                    
                    # Rate limiting
                    time.sleep(0.3)
                    
                except Exception as e:
                    logger.warning(f"Error processing post {post.id}: {e}")
                    continue
            
            logger.info(f"{Fore.GREEN}✓ Found {len(potential_clients)} potential clients in r/{subreddit_name}{Style.RESET_ALL}")
            if ENABLE_AUTO_REPLY:
                replies_in_subreddit = sum(1 for c in potential_clients if c.get('reply_posted', False))
                logger.info(f"{Fore.GREEN}✓ Posted {replies_in_subreddit} replies in r/{subreddit_name}{Style.RESET_ALL}")
            
            return potential_clients
            
        except Exception as e:
            logger.error(f"{Fore.RED}✗ Error scraping r/{subreddit_name}: {e}{Style.RESET_ALL}")
            return []
    
    def scrape_all_subreddits_with_replies(self) -> List[Dict]:
        """Scrape all configured subreddits and generate replies"""
        logger.info(f"{Fore.YELLOW}Starting enhanced scraping across {len(SUBREDDITS)} subreddits...{Style.RESET_ALL}")
        
        all_clients = []
        
        for subreddit in SUBREDDITS:
            try:
                clients = self.scrape_subreddit_with_replies(subreddit)
                all_clients.extend(clients)
                
                # Rate limiting between subreddits
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Failed to scrape r/{subreddit}: {e}")
                continue
        
        # Sort by final score
        all_clients.sort(key=lambda x: x['final_score'], reverse=True)
        
        logger.info(f"{Fore.GREEN}✓ Enhanced scraping complete! Found {len(all_clients)} total potential clients{Style.RESET_ALL}")
        if ENABLE_AUTO_REPLY:
            total_replies = sum(1 for c in all_clients if c.get('reply_posted', False))
            logger.info(f"{Fore.GREEN}✓ Posted {total_replies} total replies{Style.RESET_ALL}")
        
        return all_clients
    
    def generate_custom_text_report(self, clients: List[Dict]) -> str:
        """Generate custom text report with reply information"""
        if not clients:
            return "No potential clients found."
        
        report = []
        report.append("=" * 80)
        report.append("ENHANCED REDDIT CLIENT LEADS WITH INTELLIGENT REPLIES")
        report.append("=" * 80)
        report.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total leads found: {len(clients)}")
        report.append(f"AI analysis enabled: {bool(self.ai_analyzer)}")
        report.append(f"Auto-reply enabled: {ENABLE_AUTO_REPLY}")
        report.append(f"Replies posted: {sum(1 for c in clients if c.get('reply_posted', False))}")
        report.append("=" * 80)
        report.append("")
        
        for i, client in enumerate(clients, 1):
            report.append(f"LEAD #{i}")
            report.append("-" * 40)
            
            # What they want
            services = client.get('services_needed', [])
            if isinstance(services, list):
                services = ', '.join(services)
            report.append(f"What they want: {services}")
            
            # When it was posted
            post_date = client['created_utc'].strftime('%Y-%m-%d %H:%M:%S')
            report.append(f"When it was posted: {post_date}")
            
            # Username/name of the poster
            author = client.get('author', 'Unknown')
            report.append(f"Username/name of the poster: {author}")
            
            # Link to the post
            report.append(f"Link to the post: {client.get('url', 'N/A')}")
            
            # Other contact details
            contact_info = client.get('contact_info', {})
            contact_details = []
            if contact_info.get('email'):
                contact_details.append(f"Email: {contact_info['email']}")
            if contact_info.get('website'):
                contact_details.append(f"Website: {contact_info['website']}")
            if contact_info.get('phone'):
                contact_details.append(f"Phone: {contact_info['phone']}")
            
            if contact_details:
                report.append(f"Other contact details: {'; '.join(contact_details)}")
            else:
                report.append("Other contact details: None found")
            
            # Lead quality score
            score = client.get('final_score', 0)
            report.append(f"Lead quality score: {score}/100")
            
            # Reply information
            if client.get('reply_generated'):
                report.append(f"Reply generated: Yes")
                if client.get('reply_posted'):
                    report.append(f"Reply posted: Yes")
                else:
                    report.append(f"Reply posted: No (dry run mode)")
                report.append(f"Reply text: {client.get('reply_text', '')[:200]}...")
            else:
                report.append(f"Reply generated: No (didn't meet criteria)")
            
            # AI insights
            if client.get('ai_analysis'):
                ai_analysis = client['ai_analysis']
                budget_info = ai_analysis.get('budget_indicators', {})
                if budget_info.get('budget_range'):
                    report.append(f"Budget indication: {budget_info['budget_range']}")
                
                urgency = ai_analysis.get('urgency_level', 'Unknown')
                if urgency != 'Unknown':
                    report.append(f"Urgency level: {urgency}")
                
                insights = ai_analysis.get('key_insights', [])
                if insights:
                    report.append(f"Key insights: {'; '.join(insights[:2])}")
            
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
        
        # Reply statistics
        replies_generated = sum(1 for c in clients if c.get('reply_generated', False))
        replies_posted = sum(1 for c in clients if c.get('reply_posted', False))
        report.append(f"\nReply Statistics:")
        report.append(f"  • Replies generated: {replies_generated}")
        report.append(f"  • Replies posted: {replies_posted}")
        report.append(f"  • Reply success rate: {(replies_posted/replies_generated*100):.1f}%" if replies_generated > 0 else "  • Reply success rate: 0%")
        
        # High-priority leads
        high_priority = [c for c in clients if c.get('final_score', 0) > 70]
        report.append(f"\nHigh-priority leads (score > 70): {len(high_priority)}")
        
        # Leads with contact info
        with_contact = [c for c in clients if c.get('contact_info', {}).get('email') or c.get('contact_info', {}).get('website')]
        report.append(f"Leads with contact information: {len(with_contact)}")
        
        report.append("")
        report.append("=" * 80)
        report.append("END OF REPORT")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def save_results(self, clients: List[Dict]) -> tuple:
        """Save results to various formats"""
        if not clients:
            logger.warning("No client data to save")
            return None, None, None
        
        # Create output directory
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save custom text report
        report_content = self.generate_custom_text_report(clients)
        text_file = os.path.join(OUTPUT_DIR, f"enhanced_reddit_leads_{timestamp}.txt")
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        # Save CSV
        df = pd.DataFrame(clients)
        csv_file = os.path.join(OUTPUT_DIR, f"enhanced_reddit_leads_{timestamp}.csv")
        df.to_csv(csv_file, index=False)
        
        # Save Excel with multiple sheets
        excel_file = os.path.join(OUTPUT_DIR, f"enhanced_reddit_leads_{timestamp}.xlsx")
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='All Clients', index=False)
            
            # High-priority clients
            high_priority = df[df['final_score'] > 70].copy()
            if not high_priority.empty:
                high_priority.to_excel(writer, sheet_name='High Priority', index=False)
            
            # Clients with replies
            with_replies = df[df['reply_generated'] == True].copy()
            if not with_replies.empty:
                with_replies.to_excel(writer, sheet_name='With Replies', index=False)
            
            # Service-specific sheets
            for service in ['Digital Marketing', 'Website Development', 'Business Automation']:
                service_clients = df[df['services_needed'].str.contains(service, na=False)].copy()
                if not service_clients.empty:
                    service_clients.to_excel(writer, sheet_name=service.replace(' ', '_'), index=False)
        
        logger.info(f"{Fore.GREEN}✓ Results saved to:{Style.RESET_ALL}")
        logger.info(f"  📄 Text report: {text_file}")
        logger.info(f"  📊 CSV file: {csv_file}")
        logger.info(f"  📈 Excel file: {excel_file}")
        
        return text_file, csv_file, excel_file


def main():
    """Main function for enhanced Reddit scraper"""
    print(f"{Fore.CYAN}{'='*60}")
    print("🚀 ENHANCED REDDIT CLIENT SCRAPER")
    print("AI-powered client discovery with intelligent replies")
    print(f"{'='*60}{Style.RESET_ALL}\n")
    
    try:
        # Initialize enhanced scraper
        scraper = EnhancedRedditClientScraper()
        
        # Show configuration
        print(f"{Fore.CYAN}Configuration:{Style.RESET_ALL}")
        print(f"• AI Analysis: {'Enabled' if USE_AI_ANALYSIS else 'Disabled'}")
        print(f"• Auto-Reply: {'Enabled' if ENABLE_AUTO_REPLY else 'Disabled'}")
        print(f"• Dry Run Mode: {'Yes' if REPLY_DRY_RUN else 'No'}")
        print(f"• Max Replies: {MAX_REPLIES_PER_SESSION}")
        print()
        
        # Scrape all subreddits with replies
        clients = scraper.scrape_all_subreddits_with_replies()
        
        if clients:
            # Save results
            text_file, csv_file, excel_file = scraper.save_results(clients)
            
            print(f"\n{Fore.GREEN}✓ Enhanced scraping completed successfully!{Style.RESET_ALL}")
            print(f"📄 Main report: {text_file}")
            print(f"📊 CSV backup: {csv_file}")
            print(f"📈 Excel file: {excel_file}")
            
            # Display summary
            high_priority = [c for c in clients if c.get('final_score', 0) > 70]
            with_contact = [c for c in clients if c.get('contact_info', {}).get('email') or c.get('contact_info', {}).get('website')]
            replies_posted = sum(1 for c in clients if c.get('reply_posted', False))
            
            print(f"\n{Fore.CYAN}Quick Summary:{Style.RESET_ALL}")
            print(f"• Total leads found: {len(clients)}")
            print(f"• High-priority leads: {len(high_priority)}")
            print(f"• Leads with contact info: {len(with_contact)}")
            print(f"• Replies posted: {replies_posted}")
            print(f"• AI analysis enabled: {bool(scraper.ai_analyzer)}")
            
            # Show top 3 leads
            print(f"\n{Fore.YELLOW}Top 3 High-Priority Leads:{Style.RESET_ALL}")
            for i, client in enumerate(clients[:3], 1):
                print(f"\n{i}. {client['title'][:60]}...")
                print(f"   Score: {client['final_score']} | Services: {', '.join(client['services_needed'])}")
                if client.get('reply_posted'):
                    print(f"   ✅ Reply posted")
                elif client.get('reply_generated'):
                    print(f"   📝 Reply generated (dry run)")
                if client.get('contact_info', {}).get('email'):
                    print(f"   Email: {client['contact_info']['email']}")
                print(f"   URL: {client['url']}")
        
        else:
            print(f"{Fore.YELLOW}⚠ No potential clients found. Try adjusting the search criteria.{Style.RESET_ALL}")
    
    except Exception as e:
        logger.error(f"{Fore.RED}✗ Enhanced scraping failed: {e}{Style.RESET_ALL}")
        print(f"{Fore.RED}✗ Error: {e}{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
