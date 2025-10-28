# 🚀 Enhanced Reddit Client Scraper with Intelligent Replies

A powerful Python tool to discover potential clients on **Reddit** and generate intelligent, personalized replies to win business. This advanced scraper uses AI-powered analysis to identify high-quality leads and automatically craft lucrative responses for digital marketing, website development, and business process automation services.

## ✨ Features

### 🎯 **Intelligent Client Discovery**
- **AI-powered analysis** using Mistral AI for lead scoring
- **Keyword-based filtering** across 20+ relevant subreddits
- **Business context analysis** to identify genuine prospects
- **Intelligent relevance scoring** (0-100) to prioritize high-value leads
- **Contact information extraction** (emails, websites, phones)

### 💬 **Smart Reply Generation**
- **Personalized reply templates** for each service category
- **AI-powered customization** based on post content and context
- **Service-specific messaging** (marketing, web dev, automation)
- **Budget and urgency awareness** in reply content
- **Professional tone** with proven conversion strategies

### 🤖 **Automated Reply Posting**
- **Optional automatic posting** to Reddit posts
- **Dry run mode** for testing without posting
- **Rate limiting** to avoid spam detection
- **Reply quality filtering** (only high-potential leads)
- **Session limits** for responsible usage

### 📊 **Advanced Analytics**
- **Sentiment analysis** to gauge client urgency
- **Budget indicator detection** to identify spending capacity
- **Timeline analysis** to find urgent projects
- **Engagement metrics** for lead quality assessment
- **Reply success tracking** and performance metrics

### 🎯 **Service-Specific Targeting**
- **Digital Marketing**: SEO, PPC, social media, content marketing
- **Website Development**: Custom sites, e-commerce, WordPress, etc.
- **Business Automation**: Workflow automation, API integrations, process optimization

### 🎨 **Intuitive Interface**
- **Rich command-line interface** with beautiful formatting
- **Interactive menus** for easy navigation
- **Real-time progress tracking** with visual indicators
- **Configuration validation** and setup guidance
- **Results visualization** with formatted tables

### 📈 **Multiple Output Formats**
- **CSV export** for data analysis
- **Excel export** with multiple sheets and formatting
- **Custom text reports** in your requested format
- **Reply tracking** and performance metrics
- **High-priority client lists**

### ⏰ **Automation Options**
- **One-time scraping** for immediate results
- **Scheduled scraping** for continuous lead generation
- **Background processing** with progress tracking
- **Automated reply posting** with safety controls

## 🛠️ Installation

### Prerequisites
- Python 3.7 or higher
- Reddit API credentials
- Mistral AI API key (recommended for intelligent replies)

### Quick Setup

1. **Clone or download** this repository
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run setup script**:
   ```bash
   python setup.py
   ```

4. **Configure API credentials** (see Configuration section below)

5. (Optional) **Launch the older interactive launcher**:
   ```bash
   python launcher.py
   ```
   For direct execution, prefer:
   ```bash
   python run.py
   ```

## 📊 Dashboard (Visualization & Analytics)

An interactive Streamlit dashboard is included to explore sessions, leads, trends, and reply metrics.

### Launch

```bash
source .venv/bin/activate
python launch_dashboard.py
```

Then open `http://localhost:8501` in your browser.

### Features
- Overview KPIs: total sessions, leads, high‑priority leads, replies, reply rate
- Performance trends over time (leads, priority, replies, rate)
- Lead analysis by service category, score distributions, subreddit performance
- Detailed, filterable lead table and session filters

### Data Sources
- Reads from SQLite by default: `data/app.db`
- Falls back to `output/*.csv` and `output/*.txt` if the DB is missing

## 🗄️ Database (SQLite)

Lightweight SQLite is used for reliable dashboard performance.

Schema (auto‑created):
- `sessions(id, session_date, total_leads, high_priority_leads, leads_with_contact, replies_posted, ai_analysis_enabled)`
- `leads(id, session_id, title, content, author, subreddit, url, score, comments, service_category, client_score, decision_maker, contact_readiness, urgency_level, engagement_score, engagement_level, lead_quality_score, lead_priority, created_utc)`
- `replies(id, session_id, post_id, subreddit, author, reply_text, created_at)`

### Import historical data into DB

```bash
source .venv/bin/activate
python import_to_db.py
```

This parses `output/*.csv` and `output/*.txt` and populates `data/app.db`.

## 🔧 Configuration

### API Credentials Setup

#### 1. Reddit API
- Visit [Reddit App Preferences](https://www.reddit.com/prefs/apps)
- Create a new app (script type)
- Copy your `client_id` and `client_secret`

#### 2. Mistral AI (Recommended)
- Visit [Mistral AI Console](https://console.mistral.ai/)
- Sign up and get your API key

### Update `.env` File

```env
# Reddit API
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USER_AGENT=RedditScraper/1.0 by your_username

# Mistral AI
MISTRAL_API_KEY=your_mistral_api_key_here
USE_AI_ANALYSIS=true

# Auto-Reply Configuration
ENABLE_AUTO_REPLY=false
REPLY_DELAY_MIN=5
REPLY_DELAY_MAX=15
MAX_REPLIES_PER_SESSION=10
REPLY_DRY_RUN=true
```

### Customizing Search Parameters

Edit `config.py` to customize:

- **Subreddits to monitor** (entrepreneur, smallbusiness, startups, etc.)
- **Keywords for each service** (marketing, web dev, automation)
- **Reply templates** and personalization settings
- **Your business information** and experience
- **Filtering criteria** (minimum engagement, post age, etc.)
- **Output settings** (file names, directories)

## 🚀 Usage

### Intuitive Launcher (Recommended)

Launch the beautiful, interactive interface:

```bash
python launcher.py
```

This provides:
- ✅ Requirement checking
- ⚙️ Configuration validation
- 🎯 Scraper selection
- 📊 Results visualization
- ❓ Help and documentation

### Enhanced Reddit Scraper (Recommended)

Run the enhanced scraper with intelligent replies:

```bash
python enhanced_reddit_scraper.py
```

Features:
- 🎯 AI-powered client discovery
- 💬 Intelligent reply generation
- 🤖 Optional automated posting
- 📊 Comprehensive reporting

### Other Scrapers

#### Basic Reddit Scraper
```bash
python reddit_scraper.py
```

#### AI-Enhanced Reddit Scraper
```bash
python ai_enhanced_scraper.py
```

### Scheduled Scraping

Set up automated scraping that runs at regular intervals:

```bash
python scheduler.py
```

## 📊 Output Data

### CSV/Excel Columns

| Column | Description |
|--------|-------------|
| `subreddit` | Source subreddit |
| `title` | Post title |
| `content` | Post content (truncated) |
| `author` | Reddit username |
| `score` | Post upvotes |
| `comments` | Number of comments |
| `services_needed` | Detected service categories |
| `keywords_found` | Matching keywords |
| `relevance_score` | Calculated relevance (0-100+) |
| `email` | Extracted email address |
| `website` | Extracted website URL |
| `budget` | Detected budget information |
| `timeline` | Project timeline indicators |
| `urgency` | Urgency level (high/medium/low) |
| `sentiment_*` | Sentiment analysis scores |
| `url` | Direct link to Reddit post |

### Excel Sheets

- **All Clients**: Complete dataset
- **High Priority**: Clients with score > 50
- **Digital Marketing**: Marketing-related prospects
- **Website Development**: Web dev prospects
- **Business Automation**: Automation prospects
- **Summary**: Statistics and metrics

## 🎯 Target Subreddits

The scraper monitors these subreddits by default:

### Business & Entrepreneurship
- `r/entrepreneur` - Business owners and entrepreneurs
- `r/smallbusiness` - Small business discussions
- `r/startups` - Startup community
- `r/business` - General business topics
- `r/businessideas` - Business idea discussions

### Marketing & Growth
- `r/marketing` - Marketing professionals
- `r/digitalmarketing` - Digital marketing focus
- `r/entrepreneurridealong` - Business journey sharing

### Technology & Development
- `r/webdev` - Web developers
- `r/freelance` - Freelance opportunities
- `r/forhire` - Job postings
- `r/sideproject` - Side project discussions

### E-commerce & Automation
- `r/ecommerce` - E-commerce businesses
- `r/shopify` - Shopify store owners
- `r/woocommerce` - WooCommerce users
- `r/automation` - Automation discussions
- `r/productivity` - Productivity tools

## 🔍 Keyword Detection

### Digital Marketing Keywords
- Marketing help, strategy, social media marketing
- Google ads, Facebook ads, PPC, SEO
- Content marketing, email marketing
- Lead generation, conversion optimization

### Website Development Keywords
- Website development, web design, custom website
- E-commerce website, online store
- Landing page, website redesign
- WordPress, Shopify, WooCommerce

### Business Automation Keywords
- Business automation, workflow automation
- Process automation, Zapier
- API integration, data entry automation
- Operational efficiency, productivity tools

## 📈 Scoring System

The relevance score is calculated based on:

- **Keywords found** (10 points each)
- **Post engagement** (up to 30 points)
- **Comment activity** (up to 25 points)
- **Sentiment analysis** (up to 15 points)
- **Budget indicators** (20 points)
- **Timeline urgency** (up to 25 points)
- **Business context** (15 points)
- **Post recency** (5 points)

**Total possible score**: 100+ points

## 🚨 Important Notes

### Rate Limiting
- The scraper includes built-in rate limiting to respect Reddit's API limits
- Uses delays between requests to avoid being blocked
- Processes posts in batches to manage memory usage

### Reddit API Terms
- Follow Reddit's API terms of service
- Don't abuse the API with excessive requests
- Respect user privacy and data usage policies

### Data Privacy
- Only extracts publicly available information
- No private messages or user data accessed
- Contact information extracted only from public posts

## ⚙️ Configuration Notes

- Multi‑model Mistral AI rotation is configured in `config.py` (`MISTRAL_MODELS`).
- Auto‑reply safety: 30–120s delay between replies, 24h per‑user cooldown, non‑promotional templates.
- Max replies per session configurable via `.env` (`MAX_REPLIES_PER_SESSION`, default 100).

## 🧰 Scripts Quick Reference

- Run scraper: `python run.py`
- Launch dashboard: `python launch_dashboard.py`
- Import to DB: `python import_to_db.py`
- Process files cache: `python data_processor.py`

## 🛠️ Troubleshooting

### Common Issues

1. **API Connection Failed**
   - Verify your Reddit API credentials
   - Check internet connection
   - Ensure Reddit API is accessible

2. **No Results Found**
   - Adjust keyword lists in `config.py`
   - Lower minimum score/comment thresholds
   - Check if subreddits are active

3. **Rate Limiting Errors**
   - Increase delays between requests
   - Reduce the number of posts per subreddit
   - Use authenticated requests (username/password)

4. **Dashboard/DB Errors**
   - Rebuild DB from outputs: `python import_to_db.py`
   - Free dashboard port 8501 (macOS/Linux): `lsof -ti tcp:8501 | xargs kill -9`
   - Reinstall UI deps: `pip install -U streamlit plotly pyarrow jsonschema`

### Getting Help

- Check the log files for detailed error messages
- Verify your Reddit API app settings
- Ensure all dependencies are installed correctly

## 📝 Example Output

```
=== REDDIT CLIENT SCRAPING SUMMARY ===

Total Potential Clients Found: 47
High-Relevance Clients (Score > 50): 12

Services Needed Breakdown:
  • Digital Marketing: 23 clients
  • Website Development: 18 clients
  • Business Automation: 6 clients

Top Subreddits for Client Discovery:
  • r/entrepreneur: 15 clients
  • r/smallbusiness: 12 clients
  • r/startups: 8 clients

Top 5 High-Priority Prospects:
  1. Need help with Google Ads campaign for my e-commerce store... (Score: 85)
     r/entrepreneur | Digital Marketing
     Email: john@mystore.com
     URL: https://reddit.com/r/entrepreneur/comments/...

  2. Looking for web developer to build custom Shopify store... (Score: 78)
     r/smallbusiness | Website Development
     Budget: $5k
     URL: https://reddit.com/r/smallbusiness/comments/...
```

## 🎯 Pro Tips

### Maximizing Results

1. **Run regularly**: Set up scheduled scraping for continuous lead generation
2. **Customize keywords**: Add industry-specific terms to your keyword lists
3. **Monitor trends**: Track which subreddits yield the best prospects
4. **Follow up quickly**: High-relevance prospects often get multiple responses

### Best Practices

1. **Personalize outreach**: Use the post content to craft relevant messages
2. **Provide value**: Offer free advice or resources in your initial contact
3. **Build relationships**: Focus on helping rather than just selling
4. **Track results**: Monitor which leads convert to actual clients

## 📄 License

This project is for educational and business development purposes. Please respect Reddit's terms of service and use responsibly.

## 🤝 Contributing

Feel free to submit issues, feature requests, or pull requests to improve the scraper.

---

**Happy client hunting! 🎯💰**
