"""
Data Processor Utility
Processes and enhances Reddit scraping data for dashboard visualization
"""

import pandas as pd
import json
import os
import re
from datetime import datetime
from typing import Dict, List, Optional

class DataProcessor:
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
    
    def process_csv_file(self, filepath: str) -> pd.DataFrame:
        """Process a CSV file and enhance it with additional metrics"""
        try:
            df = pd.read_csv(filepath)
            
            # Add session metadata
            session_info = self._extract_session_info(filepath)
            df['session_date'] = session_info['date']
            df['session_id'] = session_info['id']
            df['file_path'] = filepath
            
            # Process AI analysis column
            if 'ai_analysis' in df.columns:
                df = self._process_ai_analysis(df)
            
            # Add engagement metrics
            df = self._add_engagement_metrics(df)
            
            # Add lead quality score
            df = self._add_lead_quality_score(df)
            
            return df
            
        except Exception as e:
            print(f"Error processing CSV file {filepath}: {e}")
            return pd.DataFrame()
    
    def _extract_session_info(self, filepath: str) -> Dict:
        """Extract session information from filename"""
        filename = os.path.basename(filepath)
        pattern = r'enhanced_reddit_leads_(\d{8})_(\d{6})\.csv'
        match = re.search(pattern, filename)
        
        if match:
            date_str = match.group(1)
            time_str = match.group(2)
            try:
                date_obj = datetime.strptime(f"{date_str}_{time_str}", "%Y%m%d_%H%M%S")
                return {
                    'date': date_obj,
                    'id': filename.split('.')[0]
                }
            except:
                pass
        
        return {
            'date': datetime.now(),
            'id': filename.split('.')[0]
        }
    
    def _process_ai_analysis(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process AI analysis column and extract structured data"""
        def parse_ai_analysis(analysis_str):
            if pd.isna(analysis_str) or analysis_str == '{}':
                return {}
            
            try:
                if isinstance(analysis_str, str):
                    return json.loads(analysis_str)
                return analysis_str
            except:
                return {}
        
        df['ai_analysis_parsed'] = df['ai_analysis'].apply(parse_ai_analysis)
        
        # Extract specific fields
        df['client_potential_score'] = df['ai_analysis_parsed'].apply(
            lambda x: x.get('client_potential_score', 0) if isinstance(x, dict) else 0
        )
        
        df['decision_maker'] = df['ai_analysis_parsed'].apply(
            lambda x: x.get('decision_maker', False) if isinstance(x, dict) else False
        )
        
        df['contact_readiness'] = df['ai_analysis_parsed'].apply(
            lambda x: x.get('contact_readiness', 'unknown') if isinstance(x, dict) else 'unknown'
        )
        
        df['urgency_level'] = df['ai_analysis_parsed'].apply(
            lambda x: x.get('urgency_level', 'unknown') if isinstance(x, dict) else 'unknown'
        )
        
        df['business_maturity'] = df['ai_analysis_parsed'].apply(
            lambda x: x.get('business_maturity', 'unknown') if isinstance(x, dict) else 'unknown'
        )
        
        df['industry'] = df['ai_analysis_parsed'].apply(
            lambda x: x.get('industry', 'unknown') if isinstance(x, dict) else 'unknown'
        )
        
        return df
    
    def _add_engagement_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add engagement metrics based on post data"""
        # Engagement score (combination of score and comments)
        df['engagement_score'] = (
            (df['score'].fillna(0) * 0.7) + 
            (df['comments'].fillna(0) * 0.3)
        ).round(2)
        
        # Engagement level
        df['engagement_level'] = df['engagement_score'].apply(
            lambda x: 'High' if x > 50 else 'Medium' if x > 20 else 'Low'
        )
        
        # Days since posted
        if 'created_utc' in df.columns:
            try:
                # Try parsing as timestamp first
                df['days_since_posted'] = (
                    datetime.now() - pd.to_datetime(df['created_utc'], unit='s')
                ).dt.days
            except:
                try:
                    # Try parsing as datetime string
                    df['days_since_posted'] = (
                        datetime.now() - pd.to_datetime(df['created_utc'])
                    ).dt.days
                except:
                    # If both fail, set to 0
                    df['days_since_posted'] = 0
        
        return df
    
    def _add_lead_quality_score(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate overall lead quality score"""
        def calculate_quality_score(row):
            score = 0
            
            # Base score from AI analysis
            if 'client_potential_score' in row:
                score += row['client_potential_score'] * 0.4
            
            # Engagement bonus
            if 'engagement_score' in row:
                score += min(row['engagement_score'] * 0.3, 30)
            
            # Decision maker bonus
            if row.get('decision_maker', False):
                score += 15
            
            # Contact readiness bonus
            contact_readiness = row.get('contact_readiness', 'unknown')
            if contact_readiness == 'high':
                score += 10
            elif contact_readiness == 'medium':
                score += 5
            
            # Urgency bonus
            urgency = row.get('urgency_level', 'unknown')
            if urgency == 'high':
                score += 10
            elif urgency == 'medium':
                score += 5
            
            return min(score, 100)  # Cap at 100
        
        df['lead_quality_score'] = df.apply(calculate_quality_score, axis=1)
        
        # Lead priority
        df['lead_priority'] = df['lead_quality_score'].apply(
            lambda x: 'High' if x >= 80 else 'Medium' if x >= 60 else 'Low'
        )
        
        return df
    
    def process_txt_file(self, filepath: str) -> Dict:
        """Process a TXT file and extract summary statistics"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            session_info = self._extract_session_info(filepath)
            
            # Extract summary statistics
            summary_data = {
                'session_date': session_info['date'],
                'session_id': session_info['id'],
                'file_path': filepath
            }
            
            # Parse summary section
            patterns = {
                'total_leads': r'• Total leads found: (\d+)',
                'high_priority_leads': r'• High-priority leads: (\d+)',
                'leads_with_contact': r'• Leads with contact info: (\d+)',
                'replies_posted': r'• Replies posted: (\d+)',
                'ai_analysis_enabled': r'• AI analysis enabled: (True|False)'
            }
            
            for key, pattern in patterns.items():
                match = re.search(pattern, content)
                if match:
                    if key == 'ai_analysis_enabled':
                        summary_data[key] = match.group(1) == 'True'
                    else:
                        summary_data[key] = int(match.group(1))
                else:
                    summary_data[key] = 0 if key != 'ai_analysis_enabled' else False
            
            # Extract top leads
            top_leads_pattern = r'Top \d+ High-Priority Leads:.*?(?=\n\n|\Z)'
            top_leads_match = re.search(top_leads_pattern, content, re.DOTALL)
            
            if top_leads_match:
                top_leads_text = top_leads_match.group(0)
                # Parse individual leads
                lead_pattern = r'(\d+)\.\s+(.+?)\s+Score: (\d+).*?URL: (https://[^\s]+)'
                leads = re.findall(lead_pattern, top_leads_text)
                summary_data['top_leads'] = [
                    {
                        'rank': int(lead[0]),
                        'title': lead[1].strip(),
                        'score': int(lead[2]),
                        'url': lead[3]
                    }
                    for lead in leads
                ]
            else:
                summary_data['top_leads'] = []
            
            return summary_data
            
        except Exception as e:
            print(f"Error processing TXT file {filepath}: {e}")
            return {}
    
    def get_all_data(self) -> tuple:
        """Get all processed data from output directory"""
        csv_files = [f for f in os.listdir(self.output_dir) if f.endswith('.csv')]
        txt_files = [f for f in os.listdir(self.output_dir) if f.endswith('.txt')]
        
        # Process CSV files
        all_csv_data = []
        for csv_file in csv_files:
            filepath = os.path.join(self.output_dir, csv_file)
            df = self.process_csv_file(filepath)
            if not df.empty:
                all_csv_data.append(df)
        
        # Process TXT files
        all_txt_data = []
        for txt_file in txt_files:
            filepath = os.path.join(self.output_dir, txt_file)
            summary = self.process_txt_file(filepath)
            if summary:
                all_txt_data.append(summary)
        
        # Combine data
        combined_df = pd.concat(all_csv_data, ignore_index=True) if all_csv_data else pd.DataFrame()
        summary_df = pd.DataFrame(all_txt_data) if all_txt_data else pd.DataFrame()
        
        return combined_df, summary_df
    
    def save_processed_data(self, combined_df: pd.DataFrame, summary_df: pd.DataFrame):
        """Save processed data for faster dashboard loading"""
        processed_dir = os.path.join(self.output_dir, "processed")
        os.makedirs(processed_dir, exist_ok=True)
        
        # Save combined data
        if not combined_df.empty:
            combined_df.to_csv(
                os.path.join(processed_dir, "combined_leads.csv"),
                index=False
            )
        
        # Save summary data
        if not summary_df.empty:
            summary_df.to_csv(
                os.path.join(processed_dir, "session_summaries.csv"),
                index=False
            )
        
        print(f"✅ Processed data saved to {processed_dir}")

if __name__ == "__main__":
    processor = DataProcessor()
    combined_df, summary_df = processor.get_all_data()
    
    print(f"📊 Processed {len(combined_df)} leads from {len(summary_df)} sessions")
    
    if not combined_df.empty:
        print(f"📈 Average lead quality score: {combined_df['lead_quality_score'].mean():.1f}")
        print(f"🎯 High priority leads: {len(combined_df[combined_df['lead_priority'] == 'High'])}")
    
    processor.save_processed_data(combined_df, summary_df)
