"""
Setup script for Reddit Client Scraper
"""

import os
import sys
from pathlib import Path

def create_env_file():
    """Create .env file from template"""
    env_content = """# Reddit API Credentials
# Get these from https://www.reddit.com/prefs/apps
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USER_AGENT=RedditScraper/1.0 by your_username

# Optional: Reddit username and password (for authenticated requests)
REDDIT_USERNAME=your_username
REDDIT_PASSWORD=your_password

# Mistral AI Configuration
# Get your API key from https://console.mistral.ai/
MISTRAL_API_KEY=your_mistral_api_key_here
MISTRAL_MODEL=mistral-large-latest
USE_AI_ANALYSIS=true
"""
    
    env_file = Path('.env')
    if not env_file.exists():
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✓ Created .env file - please update with your Reddit API credentials")
    else:
        print("✓ .env file already exists")

def create_directories():
    """Create necessary directories"""
    directories = ['output', 'logs']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Created {directory}/ directory")

def check_requirements():
    """Check if required packages are installed"""
    try:
        import praw
        import pandas
        import openpyxl
        print("✓ All required packages are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing required package: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Reddit Client Scraper...")
    print("=" * 50)
    
    # Create directories
    create_directories()
    
    # Create .env file
    create_env_file()
    
    # Check requirements
    if check_requirements():
        print("\n✅ Setup complete!")
        print("\nNext steps:")
        print("1. Update .env file with your Reddit API credentials")
        print("2. Get Reddit API credentials from: https://www.reddit.com/prefs/apps")
        print("3. Run: python reddit_scraper.py")
    else:
        print("\n❌ Setup incomplete. Please install requirements first.")

if __name__ == "__main__":
    main()
