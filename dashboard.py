"""
Reddit Scraper Dashboard
A comprehensive dashboard for visualizing and tracking Reddit scraping data
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import glob
from datetime import datetime, timedelta
import json
import re
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="Reddit Scraper Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-metric {
        border-left-color: #28a745;
    }
    .warning-metric {
        border-left-color: #ffc107;
    }
    .danger-metric {
        border-left-color: #dc3545;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

class RedditScraperDashboard:
    def __init__(self):
        self.output_dir = "output"
        self.data_files = self._get_data_files()
        
    def _get_data_files(self):
        """Get all CSV and TXT files from output directory"""
        if not os.path.exists(self.output_dir):
            return []
        
        csv_files = glob.glob(os.path.join(self.output_dir, "*.csv"))
        txt_files = glob.glob(os.path.join(self.output_dir, "*.txt"))
        
        # Sort by modification time (newest first)
        all_files = csv_files + txt_files
        all_files.sort(key=os.path.getmtime, reverse=True)
        
        return all_files
    
    def _parse_filename(self, filename):
        """Extract date and time from filename"""
        # Pattern: enhanced_reddit_leads_YYYYMMDD_HHMMSS.ext
        pattern = r'enhanced_reddit_leads_(\d{8})_(\d{6})\.(csv|txt)'
        match = re.search(pattern, os.path.basename(filename))
        
        if match:
            date_str = match.group(1)
            time_str = match.group(2)
            try:
                datetime_obj = datetime.strptime(f"{date_str}_{time_str}", "%Y%m%d_%H%M%S")
                return datetime_obj
            except:
                return None
        return None
    
    def load_csv_data(self, filepath):
        """Load and process CSV data"""
        try:
            df = pd.read_csv(filepath)
            
            # Add session info
            session_date = self._parse_filename(filepath)
            df['session_date'] = session_date
            df['session_id'] = os.path.basename(filepath).split('.')[0]
            
            # Process AI analysis data
            if 'ai_analysis' in df.columns:
                df['ai_analysis'] = df['ai_analysis'].fillna('{}')
                df['ai_analysis'] = df['ai_analysis'].apply(
                    lambda x: json.loads(x) if isinstance(x, str) and x != '{}' else {}
                )
                
                # Extract AI insights
                df['client_score'] = df['ai_analysis'].apply(
                    lambda x: x.get('client_potential_score', 0) if isinstance(x, dict) else 0
                )
                df['decision_maker'] = df['ai_analysis'].apply(
                    lambda x: x.get('decision_maker', False) if isinstance(x, dict) else False
                )
                df['contact_readiness'] = df['ai_analysis'].apply(
                    lambda x: x.get('contact_readiness', 'unknown') if isinstance(x, dict) else 'unknown'
                )
                df['urgency_level'] = df['ai_analysis'].apply(
                    lambda x: x.get('urgency_level', 'unknown') if isinstance(x, dict) else 'unknown'
                )
            
            return df
        except Exception as e:
            st.error(f"Error loading CSV file {filepath}: {e}")
            return pd.DataFrame()
    
    def load_txt_data(self, filepath):
        """Load and process TXT data for summary statistics"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract summary statistics
            session_date = self._parse_filename(filepath)
            
            # Parse summary section
            summary_pattern = r'Quick Summary:.*?• Total leads found: (\d+).*?• High-priority leads: (\d+).*?• Leads with contact info: (\d+).*?• Replies posted: (\d+)'
            match = re.search(summary_pattern, content, re.DOTALL)
            
            if match:
                return {
                    'session_date': session_date,
                    'session_id': os.path.basename(filepath).split('.')[0],
                    'total_leads': int(match.group(1)),
                    'high_priority_leads': int(match.group(2)),
                    'leads_with_contact': int(match.group(3)),
                    'replies_posted': int(match.group(4))
                }
            
            return None
        except Exception as e:
            st.error(f"Error loading TXT file {filepath}: {e}")
            return None
    
    def get_combined_data(self):
        """Get combined data from all sessions"""
        all_data = []
        session_summaries = []
        
        for filepath in self.data_files:
            if filepath.endswith('.csv'):
                df = self.load_csv_data(filepath)
                if not df.empty:
                    all_data.append(df)
            elif filepath.endswith('.txt'):
                summary = self.load_txt_data(filepath)
                if summary:
                    session_summaries.append(summary)
        
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
        else:
            combined_df = pd.DataFrame()
        
        if session_summaries:
            summary_df = pd.DataFrame(session_summaries)
        else:
            summary_df = pd.DataFrame()
        
        return combined_df, summary_df
    
    def render_header(self):
        """Render dashboard header"""
        st.markdown('<h1 class="main-header">🚀 Reddit Scraper Dashboard</h1>', unsafe_allow_html=True)
        st.markdown("---")
    
    def render_sidebar(self, combined_df, summary_df):
        """Render sidebar with filters and controls"""
        st.sidebar.title("📊 Dashboard Controls")
        
        # File selection
        if self.data_files:
            st.sidebar.subheader("📁 Data Files")
            selected_files = st.sidebar.multiselect(
                "Select sessions to analyze:",
                options=[os.path.basename(f) for f in self.data_files],
                default=[os.path.basename(f) for f in self.data_files[:5]]  # Show latest 5 by default
            )
        else:
            st.sidebar.warning("No data files found in output directory")
            selected_files = []
        
        # Date range filter
        if not combined_df.empty and 'session_date' in combined_df.columns:
            st.sidebar.subheader("📅 Date Range")
            min_date = combined_df['session_date'].min().date()
            max_date = combined_df['session_date'].max().date()
            
            date_range = st.sidebar.date_input(
                "Select date range:",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )
        
        # Service filter
        if not combined_df.empty and 'service_category' in combined_df.columns:
            st.sidebar.subheader("🎯 Service Filter")
            services = combined_df['service_category'].unique()
            selected_services = st.sidebar.multiselect(
                "Select services:",
                options=services,
                default=services
            )
        
        # Score filter
        if not combined_df.empty and 'client_score' in combined_df.columns:
            st.sidebar.subheader("⭐ Score Filter")
            min_score = st.sidebar.slider(
                "Minimum client score:",
                min_value=0,
                max_value=100,
                value=60
            )
        
        return {
            'selected_files': selected_files,
            'date_range': date_range if 'date_range' in locals() else None,
            'selected_services': selected_services if 'selected_services' in locals() else [],
            'min_score': min_score if 'min_score' in locals() else 0
        }
    
    def render_overview_metrics(self, summary_df, filters):
        """Render overview metrics"""
        st.subheader("📈 Overview Metrics")
        
        if summary_df.empty:
            st.warning("No session data available")
            return
        
        # Filter data based on selected files
        if filters['selected_files']:
            filtered_summary = summary_df[
                summary_df['session_id'].isin([f.split('.')[0] for f in filters['selected_files']])
            ]
        else:
            filtered_summary = summary_df
        
        # Calculate metrics
        total_sessions = len(filtered_summary)
        total_leads = filtered_summary['total_leads'].sum()
        total_high_priority = filtered_summary['high_priority_leads'].sum()
        total_replies = filtered_summary['replies_posted'].sum()
        avg_leads_per_session = filtered_summary['total_leads'].mean()
        
        # Create metrics columns
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                label="📊 Total Sessions",
                value=total_sessions,
                delta=f"{total_sessions} sessions"
            )
        
        with col2:
            st.metric(
                label="🎯 Total Leads",
                value=total_leads,
                delta=f"{avg_leads_per_session:.1f} avg/session"
            )
        
        with col3:
            st.metric(
                label="⭐ High Priority Leads",
                value=total_high_priority,
                delta=f"{(total_high_priority/total_leads*100):.1f}%" if total_leads > 0 else "0%"
            )
        
        with col4:
            st.metric(
                label="💬 Total Replies",
                value=total_replies,
                delta=f"{(total_replies/total_leads*100):.1f}%" if total_leads > 0 else "0%"
            )
        
        with col5:
            conversion_rate = (total_replies / total_leads * 100) if total_leads > 0 else 0
            st.metric(
                label="📈 Reply Rate",
                value=f"{conversion_rate:.1f}%",
                delta=f"{conversion_rate:.1f}%"
            )
    
    def render_trend_charts(self, summary_df, filters):
        """Render trend charts"""
        st.subheader("📊 Performance Trends")
        
        if summary_df.empty:
            st.warning("No trend data available")
            return
        
        # Filter data
        if filters['selected_files']:
            filtered_summary = summary_df[
                summary_df['session_id'].isin([f.split('.')[0] for f in filters['selected_files']])
            ]
        else:
            filtered_summary = summary_df
        
        # Sort by date
        filtered_summary = filtered_summary.sort_values('session_date')
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Leads Over Time', 'High Priority Leads', 'Replies Posted', 'Reply Rate'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Leads over time
        fig.add_trace(
            go.Scatter(
                x=filtered_summary['session_date'],
                y=filtered_summary['total_leads'],
                mode='lines+markers',
                name='Total Leads',
                line=dict(color='#1f77b4')
            ),
            row=1, col=1
        )
        
        # High priority leads
        fig.add_trace(
            go.Scatter(
                x=filtered_summary['session_date'],
                y=filtered_summary['high_priority_leads'],
                mode='lines+markers',
                name='High Priority',
                line=dict(color='#28a745')
            ),
            row=1, col=2
        )
        
        # Replies posted
        fig.add_trace(
            go.Scatter(
                x=filtered_summary['session_date'],
                y=filtered_summary['replies_posted'],
                mode='lines+markers',
                name='Replies Posted',
                line=dict(color='#ffc107')
            ),
            row=2, col=1
        )
        
        # Reply rate
        reply_rate = (filtered_summary['replies_posted'] / filtered_summary['total_leads'] * 100).fillna(0)
        fig.add_trace(
            go.Scatter(
                x=filtered_summary['session_date'],
                y=reply_rate,
                mode='lines+markers',
                name='Reply Rate %',
                line=dict(color='#dc3545')
            ),
            row=2, col=2
        )
        
        fig.update_layout(height=600, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    def render_lead_analysis(self, combined_df, filters):
        """Render lead analysis charts"""
        st.subheader("🎯 Lead Analysis")
        
        if combined_df.empty:
            st.warning("No lead data available")
            return
        
        # Apply filters
        filtered_df = combined_df.copy()
        
        if filters['selected_files']:
            filtered_df = filtered_df[
                filtered_df['session_id'].isin([f.split('.')[0] for f in filters['selected_files']])
            ]
        
        if filters['selected_services'] and 'service_category' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['service_category'].isin(filters['selected_services'])]
        
        if 'client_score' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['client_score'] >= filters['min_score']]
        
        # Create analysis charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Service distribution
            if 'service_category' in filtered_df.columns:
                service_counts = filtered_df['service_category'].value_counts()
                fig_service = px.pie(
                    values=service_counts.values,
                    names=service_counts.index,
                    title="Leads by Service Category"
                )
                st.plotly_chart(fig_service, use_container_width=True)
        
        with col2:
            # Score distribution
            if 'client_score' in filtered_df.columns:
                fig_score = px.histogram(
                    filtered_df,
                    x='client_score',
                    title="Client Score Distribution",
                    nbins=20
                )
                st.plotly_chart(fig_score, use_container_width=True)
        
        # Subreddit performance
        if 'subreddit' in filtered_df.columns:
            st.subheader("📊 Subreddit Performance")
            subreddit_stats = filtered_df.groupby('subreddit').agg({
                'client_score': ['count', 'mean'],
                'title': 'count'
            }).round(2)
            
            subreddit_stats.columns = ['Lead Count', 'Avg Score', 'Total Posts']
            subreddit_stats = subreddit_stats.sort_values('Lead Count', ascending=False)
            
            st.dataframe(subreddit_stats, use_container_width=True)
    
    def render_lead_table(self, combined_df, filters):
        """Render detailed lead table"""
        st.subheader("📋 Detailed Lead Data")
        
        if combined_df.empty:
            st.warning("No lead data available")
            return
        
        # Apply filters
        filtered_df = combined_df.copy()
        
        if filters['selected_files']:
            filtered_df = filtered_df[
                filtered_df['session_id'].isin([f.split('.')[0] for f in filters['selected_files']])
            ]
        
        if filters['selected_services'] and 'service_category' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['service_category'].isin(filters['selected_services'])]
        
        if 'client_score' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['client_score'] >= filters['min_score']]
        
        # Select columns to display
        display_columns = ['title', 'author', 'subreddit', 'score', 'comments', 'client_score', 'service_category']
        available_columns = [col for col in display_columns if col in filtered_df.columns]
        
        if available_columns:
            st.dataframe(
                filtered_df[available_columns],
                use_container_width=True,
                height=400
            )
        else:
            st.warning("No relevant columns found in the data")
    
    def run(self):
        """Run the dashboard"""
        self.render_header()
        
        # Load data
        combined_df, summary_df = self.get_combined_data()
        
        # Render sidebar and get filters
        filters = self.render_sidebar(combined_df, summary_df)
        
        # Render main content
        if not combined_df.empty or not summary_df.empty:
            self.render_overview_metrics(summary_df, filters)
            st.markdown("---")
            self.render_trend_charts(summary_df, filters)
            st.markdown("---")
            self.render_lead_analysis(combined_df, filters)
            st.markdown("---")
            self.render_lead_table(combined_df, filters)
        else:
            st.error("No data found. Please run the Reddit scraper first to generate data files.")
            st.info("""
            To generate data:
            1. Make sure your `.env` file is configured with Reddit API credentials
            2. Run: `python run.py`
            3. Check the `output/` directory for generated CSV and TXT files
            """)

if __name__ == "__main__":
    dashboard = RedditScraperDashboard()
    dashboard.run()
