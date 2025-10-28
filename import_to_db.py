"""
Import existing output CSV/TXT into SQLite DB
"""

import os
import json
import re
import glob
from datetime import datetime
import pandas as pd

from db import init_schema, upsert_many
from data_processor import DataProcessor


def parse_session_id_from_path(path: str) -> str:
    return os.path.basename(path).split(".")[0]


def parse_session_date_from_name(name: str) -> str:
    m = re.search(r"(\d{8})_(\d{6})", name)
    if not m:
        return datetime.now().isoformat()
    try:
        dt = datetime.strptime(m.group(1) + m.group(2), "%Y%m%d%H%M%S")
        return dt.isoformat()
    except Exception:
        return datetime.now().isoformat()


def extract_summary_from_txt(txt_path: str) -> dict:
    try:
        content = open(txt_path, "r", encoding="utf-8").read()
    except Exception:
        return {}
    patterns = {
        'total_leads': r'• Total leads found: (\d+)',
        'high_priority_leads': r'• High-priority leads: (\d+)',
        'leads_with_contact': r'• Leads with contact info: (\d+)',
        'replies_posted': r'• Replies posted: (\d+)',
        'ai_analysis_enabled': r'• AI analysis enabled: (True|False)'
    }
    data = {}
    for k, pat in patterns.items():
        m = re.search(pat, content)
        if not m:
            data[k] = False if k == 'ai_analysis_enabled' else 0
        else:
            data[k] = (m.group(1) == 'True') if k == 'ai_analysis_enabled' else int(m.group(1))
    return data


def run_import(output_dir: str = "output") -> None:
    init_schema()
    processor = DataProcessor(output_dir)

    csv_files = sorted(glob.glob(os.path.join(output_dir, "*.csv")))
    txt_files = sorted(glob.glob(os.path.join(output_dir, "*.txt")))

    # Import sessions from TXT summaries first
    session_rows = []
    for txt in txt_files:
        sid = parse_session_id_from_path(txt)
        session_rows.append({
            'id': sid,
            'session_date': parse_session_date_from_name(sid),
            **extract_summary_from_txt(txt)
        })
    upsert_many('sessions', session_rows)

    # Import leads from CSVs
    lead_rows = []
    for csv in csv_files:
        df = processor.process_csv_file(csv)
        if df.empty:
            continue
        # Expect a post id column named one of these
        post_id_col = None
        for cand in ['post_id', 'id', 'reddit_id']:
            if cand in df.columns:
                post_id_col = cand
                break
        if post_id_col is None:
            # synthesize an id
            df['__gen_id'] = df.apply(lambda r: f"{parse_session_id_from_path(csv)}_{hash(r.get('url',''))}", axis=1)
            post_id_col = '__gen_id'

        for _, row in df.iterrows():
            lead_rows.append({
                'id': str(row.get(post_id_col)),
                'session_id': parse_session_id_from_path(csv),
                'title': row.get('title'),
                'content': row.get('content'),
                'author': row.get('author'),
                'subreddit': row.get('subreddit'),
                'url': row.get('url'),
                'score': int(row.get('score', 0)) if pd.notna(row.get('score')) else 0,
                'comments': int(row.get('comments', 0)) if pd.notna(row.get('comments')) else 0,
                'service_category': row.get('service_category'),
                'client_score': int(row.get('client_potential_score', row.get('client_score', 0))) if pd.notna(row.get('client_potential_score', row.get('client_score', 0))) else 0,
                'decision_maker': 1 if str(row.get('decision_maker', 'False')).lower() == 'true' else 0,
                'contact_readiness': row.get('contact_readiness'),
                'urgency_level': row.get('urgency_level'),
                'engagement_score': float(row.get('engagement_score', 0)) if pd.notna(row.get('engagement_score', 0)) else 0.0,
                'engagement_level': row.get('engagement_level'),
                'lead_quality_score': float(row.get('lead_quality_score', 0)) if pd.notna(row.get('lead_quality_score', 0)) else 0.0,
                'lead_priority': row.get('lead_priority'),
                'created_utc': str(row.get('created_utc')) if row.get('created_utc') is not None else None,
            })

    upsert_many('leads', lead_rows)
    print(f"✓ Imported {len(session_rows)} sessions and {len(lead_rows)} leads into SQLite")


if __name__ == "__main__":
    run_import()


