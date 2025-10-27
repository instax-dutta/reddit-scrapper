# 🚀 Reddit Scraper Dashboard

A comprehensive web-based dashboard for visualizing and tracking Reddit scraping data, lead analysis, and conversion metrics.

## ✨ Features

### 📊 **Overview Metrics**
- **Total Sessions**: Track all scraping sessions
- **Total Leads**: Count of all discovered leads
- **High Priority Leads**: AI-scored high-potential clients
- **Total Replies**: Number of replies posted
- **Reply Rate**: Conversion percentage

### 📈 **Performance Trends**
- **Leads Over Time**: Track lead discovery trends
- **High Priority Leads**: Monitor quality improvements
- **Replies Posted**: Track engagement activity
- **Reply Rate**: Monitor conversion efficiency

### 🎯 **Lead Analysis**
- **Service Distribution**: Pie chart of leads by service category
- **Score Distribution**: Histogram of client potential scores
- **Subreddit Performance**: Performance metrics by subreddit
- **Lead Quality Scoring**: AI-powered lead prioritization

### 📋 **Detailed Data**
- **Interactive Lead Table**: Sortable and filterable lead data
- **Session Filtering**: Analyze specific time periods
- **Service Filtering**: Focus on specific service categories
- **Score Filtering**: Filter by minimum client scores

## 🚀 Quick Start

### 1. **Install Dependencies**
```bash
# Activate virtual environment
source .venv/bin/activate

# Install dashboard dependencies
pip install streamlit plotly
```

### 2. **Launch Dashboard**
```bash
# Method 1: Using the launcher script
python launch_dashboard.py

# Method 2: Direct Streamlit command
streamlit run dashboard.py
```

### 3. **Access Dashboard**
- Open your browser to: `http://localhost:8501`
- The dashboard will automatically load all your scraping data

## 📁 Data Processing

The dashboard automatically processes:
- **CSV Files**: Detailed lead data with AI analysis
- **TXT Files**: Session summaries and statistics
- **Enhanced Metrics**: Lead quality scores and engagement metrics

### Data Sources
- `output/*.csv` - Individual session lead data
- `output/*.txt` - Session summary reports
- `output/processed/` - Cached processed data for faster loading

## 🎛️ Dashboard Controls

### **Sidebar Filters**
- **📁 Data Files**: Select specific sessions to analyze
- **📅 Date Range**: Filter by date range
- **🎯 Service Filter**: Focus on specific services
- **⭐ Score Filter**: Set minimum client scores

### **Interactive Features**
- **Clickable Charts**: Zoom and explore data
- **Sortable Tables**: Sort by any column
- **Real-time Filtering**: Instant data updates
- **Export Options**: Download filtered data

## 📊 Key Metrics Explained

### **Lead Quality Score**
Combines multiple factors:
- **AI Analysis Score** (40%): Client potential from AI
- **Engagement Score** (30%): Reddit post engagement
- **Decision Maker Bonus** (15%): Is poster a decision maker?
- **Contact Readiness** (10%): How ready to be contacted
- **Urgency Level** (5%): Project urgency

### **Engagement Score**
- **Reddit Score** (70%): Post upvotes
- **Comments** (30%): Comment count
- **Result**: 0-100 engagement rating

### **Lead Priority**
- **High**: Quality score ≥ 80
- **Medium**: Quality score 60-79
- **Low**: Quality score < 60

## 🔧 Customization

### **Adding New Metrics**
Edit `data_processor.py` to add custom calculations:

```python
def _add_custom_metric(self, df: pd.DataFrame) -> pd.DataFrame:
    # Your custom metric calculation
    df['custom_score'] = df['score'] * 0.5 + df['comments'] * 0.5
    return df
```

### **Modifying Charts**
Edit `dashboard.py` to customize visualizations:

```python
def render_custom_chart(self, df):
    fig = px.bar(df, x='category', y='value')
    st.plotly_chart(fig)
```

## 📈 Performance Tips

### **Faster Loading**
- Processed data is cached in `output/processed/`
- Re-run `python data_processor.py` to refresh cache
- Use filters to reduce data load

### **Memory Optimization**
- Filter by date range for large datasets
- Use service filters to focus analysis
- Close unused browser tabs

## 🛠️ Troubleshooting

### **No Data Showing**
1. Check if `output/` directory exists
2. Run scraper first: `python run.py`
3. Verify CSV/TXT files are generated
4. Run data processor: `python data_processor.py`

### **Dashboard Won't Load**
1. Check if Streamlit is installed: `pip install streamlit`
2. Verify port 8501 is available
3. Try different port: `streamlit run dashboard.py --server.port 8502`

### **Charts Not Displaying**
1. Check if Plotly is installed: `pip install plotly`
2. Verify data has required columns
3. Check browser console for errors

## 📱 Mobile Support

The dashboard is responsive and works on:
- **Desktop**: Full feature set
- **Tablet**: Optimized layout
- **Mobile**: Simplified view

## 🔒 Security Notes

- Dashboard runs locally only (`localhost`)
- No data is sent to external servers
- All processing happens on your machine
- Reddit API credentials stay secure

## 📊 Sample Dashboard Views

### **Overview Page**
- Key metrics cards
- Performance trends
- Quick insights

### **Lead Analysis**
- Service distribution
- Score analysis
- Subreddit performance

### **Detailed Data**
- Sortable lead table
- Filtered views
- Export options

## 🚀 Next Steps

1. **Run Scraper**: Generate fresh data
2. **Launch Dashboard**: Visualize results
3. **Analyze Trends**: Identify patterns
4. **Optimize Strategy**: Improve targeting
5. **Track Conversions**: Monitor success

---

**Happy Scraping! 🎯**

The dashboard helps you turn raw Reddit data into actionable business insights. Use it to optimize your outreach strategy and maximize your conversion rates!
