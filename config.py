"""
Configuration settings for Reddit scraper
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Reddit API Configuration
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'RedditScraper/1.0')
REDDIT_USERNAME = os.getenv('REDDIT_USERNAME')
REDDIT_PASSWORD = os.getenv('REDDIT_PASSWORD')

# AI Configuration - Multi-Mistral Model Support
MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY')
USE_AI_ANALYSIS = os.getenv('USE_AI_ANALYSIS', 'true').lower() == 'true'

# Multiple Mistral Models for Rate Limit Avoidance
MISTRAL_MODELS = [
    {
        'name': 'mistral-large-latest',
        'description': 'Most capable model for complex analysis',
        'priority': 1
    },
    {
        'name': 'mistral-medium-latest',
        'description': 'Balanced performance and speed',
        'priority': 2
    },
    {
        'name': 'mistral-small-latest',
        'description': 'Fast and efficient for quick analysis',
        'priority': 3
    },
    {
        'name': 'open-mistral-7b',
        'description': 'Open source model for basic analysis',
        'priority': 4
    }
]

# AI Model Configuration
AI_MODELS = [
    {
        'provider': 'mistral',
        'api_key': MISTRAL_API_KEY,
        'models': MISTRAL_MODELS,
        'enabled': bool(MISTRAL_API_KEY)
    }
]

# Reply Configuration
ENABLE_AUTO_REPLY = os.getenv('ENABLE_AUTO_REPLY', 'true').lower() == 'true'
REPLY_DELAY_MIN = int(os.getenv('REPLY_DELAY_MIN', '30'))  # Minimum delay between replies (30 seconds)
REPLY_DELAY_MAX = int(os.getenv('REPLY_DELAY_MAX', '120'))  # Maximum delay between replies (2 minutes)
MAX_REPLIES_PER_SESSION = int(os.getenv('MAX_REPLIES_PER_SESSION', '100'))  # Max replies per session
REPLY_DRY_RUN = os.getenv('REPLY_DRY_RUN', 'false').lower() == 'true'  # Real replies enabled

# Search Configuration
SUBREDDITS = [
    'entrepreneur',
    'smallbusiness',
    'startups',
    'marketing',
    'digitalmarketing',
    'webdev',
    'freelance',
    'forhire',
    'business',
    'ecommerce',
    'shopify',
    'woocommerce',
    'automation',
    'productivity',
    'saas',
    'sideproject',
    'indiehackers',
    'entrepreneurridealong',
    'businessideas',
    'marketing'
]

# Keywords for identifying potential clients
DIGITAL_MARKETING_KEYWORDS = [
    'marketing help', 'marketing strategy', 'social media marketing',
    'google ads', 'facebook ads', 'ppc', 'seo', 'content marketing',
    'email marketing', 'influencer marketing', 'brand awareness',
    'lead generation', 'conversion optimization', 'marketing budget',
    'marketing agency', 'marketing consultant', 'marketing services'
]

WEBSITE_DEVELOPMENT_KEYWORDS = [
    'website development', 'web design', 'website builder', 'custom website',
    'ecommerce website', 'online store', 'shopify store', 'woocommerce',
    'landing page', 'website redesign', 'mobile responsive', 'website maintenance',
    'web developer', 'frontend', 'backend', 'full stack', 'wordpress',
    'website hosting', 'domain', 'ssl certificate'
]

AUTOMATION_KEYWORDS = [
    'business automation', 'workflow automation', 'process automation',
    'zapier', 'automation tools', 'manual tasks', 'time consuming',
    'automate', 'streamline', 'efficiency', 'productivity tools',
    'api integration', 'data entry', 'repetitive tasks', 'workflow',
    'business process', 'operational efficiency'
]

# Business indicators
BUSINESS_INDICATORS = [
    'startup', 'small business', 'entrepreneur', 'founder', 'ceo',
    'business owner', 'company', 'brand', 'revenue', 'profit',
    'customers', 'clients', 'market', 'industry', 'competition',
    'growth', 'scaling', 'investment', 'funding', 'budget'
]

# Post filtering criteria
MIN_SCORE = 5  # Minimum upvotes
MIN_COMMENTS = 2  # Minimum comments
MAX_DAYS_OLD = 30  # Maximum age of posts in days
LIMIT_PER_SUBREDDIT = 100  # Maximum posts to fetch per subreddit

# Reply Templates and Personalization
REPLY_TEMPLATES = {
    'digital_marketing': {
        'opening': [
            "This is a common challenge many businesses face.",
            "I've seen similar situations before and there are some effective approaches.",
            "Your situation sounds familiar - many businesses struggle with this.",
            "This is definitely achievable with the right approach.",
            "I've worked on similar projects and can share some insights.",
            "This is a great question that comes up often in marketing.",
            "I've helped with similar challenges before."
        ],
        'value_prop': [
            "For {service}, I've found that {strategy} typically works well. The key is focusing on {metric} and measuring results consistently.",
            "In my experience with {business_type} in {industry}, {strategy} has been effective. The main thing is to start with clear goals and track {metric}.",
            "When working with {business_type} on {service}, I usually recommend {strategy}. It's important to focus on sustainable growth rather than quick wins.",
            "For {service}, {strategy} tends to work well. The key is being consistent and measuring {metric} to see what's working.",
            "In {industry}, {strategy} has proven effective for {business_type}. The main focus should be on {metric} and building long-term value."
        ],
        'closing': [
            "Happy to share more details about what's worked in similar situations if you're interested.",
            "I can provide more specific advice based on what's worked for other businesses in your situation.",
            "Feel free to ask if you'd like more details about any of these approaches.",
            "I'd be happy to elaborate on any of these strategies if you find them helpful.",
            "Let me know if you'd like me to expand on any of these points."
        ]
    },
    'website_development': {
        'opening': [
            "This is a great project idea!",
            "Your project sounds interesting and definitely doable.",
            "I've worked on similar {project_type} projects before.",
            "This is a common type of project that many businesses need.",
            "Your vision sounds solid - I've seen similar projects succeed.",
            "This is exactly the kind of project that can make a real impact.",
            "I've helped with similar {project_type} challenges before."
        ],
        'value_prop': [
            "For {project_type}, I usually recommend {technology} because it {result}. The key is focusing on user experience and performance.",
            "When building {project_type} for {business_type}, {technology} tends to work well. It's important to prioritize {business_impact}.",
            "In my experience with {project_type}, {technology} is effective because it {result}. The main focus should be on scalability and user experience.",
            "For {business_type} websites, {technology} typically works well. The key is ensuring fast load times and good user experience.",
            "When working on {project_type}, I focus on {technology} because it {result}. It's important to build for both current needs and future growth."
        ],
        'closing': [
            "Happy to share more technical details about the approach if you're interested.",
            "I can provide more specific advice about the technical implementation if you'd like.",
            "Feel free to ask if you'd like more details about the development process.",
            "I'd be happy to elaborate on any of these technical points if you find them helpful.",
            "Let me know if you'd like me to expand on any of these development approaches."
        ]
    },
    'business_automation': {
        'opening': [
            "This is a common challenge that many businesses face.",
            "I've seen similar automation needs before and there are some effective solutions.",
            "Your situation sounds familiar - many businesses struggle with manual processes.",
            "This is definitely something that can be automated effectively.",
            "I've worked on similar automation projects and can share some insights.",
            "This is a great question about streamlining business operations.",
            "I've helped with similar process optimization challenges before."
        ],
        'value_prop': [
            "For {business_type} automation, I usually recommend focusing on {process} first. The key is identifying repetitive tasks and building reliable workflows.",
            "When automating {workflow} for {business_type}, it's important to start with {process}. The main thing is to ensure the automation is maintainable and scalable.",
            "In my experience with {business_type} automation, {workflow} optimization works well. It's important to focus on reducing {manual_task} while maintaining quality.",
            "For {business_type}, automating {process} typically saves significant time. The key is building systems that can grow with your business.",
            "When working on {workflow} automation, I focus on {process} because it {result}. It's important to start simple and build complexity gradually."
        ],
        'closing': [
            "Happy to share more details about automation approaches if you're interested.",
            "I can provide more specific advice about process optimization if you'd like.",
            "Feel free to ask if you'd like more details about any of these automation strategies.",
            "I'd be happy to elaborate on any of these process improvement ideas if you find them helpful.",
            "Let me know if you'd like me to expand on any of these automation approaches."
        ]
    }
}

# Your Business Information
YOUR_SERVICES = {
    'digital_marketing': [
        'SEO optimization',
        'Google Ads management',
        'Social media marketing',
        'Content marketing',
        'Email marketing campaigns',
        'Conversion rate optimization'
    ],
    'website_development': [
        'Custom website development',
        'E-commerce solutions',
        'WordPress development',
        'Landing page optimization',
        'Mobile-responsive design',
        'Website performance optimization'
    ],
    'business_automation': [
        'Workflow automation',
        'API integrations',
        'Data processing automation',
        'CRM automation',
        'Email marketing automation',
        'Business process optimization'
    ]
}

YOUR_EXPERIENCE = {
    'years_experience': '7+',
    'industries': ['SaaS', 'E-commerce', 'Professional Services', 'Healthcare', 'Technology', 'Finance', 'Education', 'Retail'],
    'success_metrics': {
        'conversion_rate': '25-40%',
        'traffic_increase': '150-300%',
        'cost_reduction': '30-50%',
        'time_saved': '10-20 hours per week'
    },
    'certifications': ['Google Ads Certified', 'HubSpot Certified', 'Salesforce Certified'],
    'tools': ['Google Analytics', 'HubSpot', 'Salesforce', 'Zapier', 'WordPress', 'Shopify', 'Mailchimp'],
    'specialties': ['growth hacking', 'conversion optimization', 'scalable solutions', 'data-driven strategies', 'ROI-focused approaches']
}

# Output configuration
OUTPUT_DIR = 'output'
CSV_FILENAME = 'potential_clients.csv'
EXCEL_FILENAME = 'potential_clients.xlsx'
TEXT_FILENAME = 'client_leads_report.txt'
