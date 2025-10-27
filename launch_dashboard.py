#!/usr/bin/env python3
"""
Dashboard Launcher
Simple script to launch the Reddit Scraper Dashboard
"""

import subprocess
import sys
import os

def main():
    """Launch the dashboard"""
    print("🚀 Starting Reddit Scraper Dashboard...")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("dashboard.py"):
        print("❌ Error: dashboard.py not found!")
        print("Please run this script from the reddit-scrapper directory.")
        sys.exit(1)
    
    # Check if output directory exists
    if not os.path.exists("output"):
        print("⚠️  Warning: No output directory found.")
        print("Run the scraper first to generate data files.")
        os.makedirs("output", exist_ok=True)
    
    try:
        # Launch Streamlit dashboard
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "dashboard.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error launching dashboard: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
