"""
Common utilities used by multiple processor modules.
Created to break circular import dependencies.
"""

import os
import pandas as pd
from utils.url_utils import extract_domain

def find_download_sources(history_df, downloads):
    """
    Find possible sources for downloads by looking at history entries
    before the download occurred
    """
    download_sources = []
    
    for download in downloads:
        filename = download.get('filename', '')
        download_url = download.get('url', '')
        download_time = download.get('download_time', '')
        
        if not download_time or not download_url:
            continue
        
        # Convert to datetime for comparison
        try:
            download_time = pd.to_datetime(download_time)
        except Exception as e:
            print(f"Error parsing download time '{download_time}': {e}")
            continue
        
        # Get domain of the download
        download_domain = extract_domain(download_url)
        
        try:
            # Create a copy of the dataframe to avoid modifying the original
            history_copy = history_df.copy()
            
            # Convert visit_time to datetime
            history_copy['visit_time_dt'] = pd.to_datetime(history_copy['visit_time'], errors='coerce')
            
            # Filter to remove rows with invalid datetime (NaT)
            history_copy = history_copy.dropna(subset=['visit_time_dt'])
            
            # Filter history to entries before the download but within 1 hour
            one_hour_before = download_time - pd.Timedelta(hours=1)
            potential_sources = history_copy[
                (history_copy['visit_time_dt'] <= download_time) & 
                (history_copy['visit_time_dt'] >= one_hour_before)
            ]
            
            # Sort by time (most recent first)
            potential_sources = potential_sources.sort_values('visit_time_dt', ascending=False)
            
            # Look for:
            # 1. Same domain as download
            # 2. URLs containing similar file patterns
            # 3. URLs that might be referring pages
            
            sources = []
            
            # Check for same domain
            if download_domain:
                same_domain_sources = potential_sources[potential_sources['domain'] == download_domain]
                if not same_domain_sources.empty:
                    for _, source in same_domain_sources.head(3).iterrows():
                        sources.append({
                            'url': source['url'],
                            'title': source['title'],
                            'time': source['visit_time'],
                            'match_type': 'same_domain'
                        })
            
            # Check for file extension in URL
            file_ext = os.path.splitext(filename)[1].lower()
            if file_ext:
                # Use str accessor only on string columns
                if 'url' in potential_sources.columns and potential_sources['url'].dtype == 'object':
                    file_pattern_sources = potential_sources[potential_sources['url'].str.contains(file_ext, case=False, na=False)]
                    if not file_pattern_sources.empty:
                        for _, source in file_pattern_sources.head(2).iterrows():
                            if source['url'] not in [s['url'] for s in sources]:
                                sources.append({
                                    'url': source['url'],
                                    'title': source['title'],
                                    'time': source['visit_time'],
                                    'match_type': 'file_pattern'
                                })
            
            # Add remaining potential sources if we have fewer than 5
            if len(sources) < 5:
                for _, source in potential_sources.head(5 - len(sources)).iterrows():
                    if source['url'] not in [s['url'] for s in sources]:
                        sources.append({
                            'url': source['url'],
                            'title': source['title'],
                            'time': source['visit_time'],
                            'match_type': 'temporal'
                        })
            
            download_sources.append({
                'filename': filename,
                'download_url': download_url,
                'download_time': download_time.isoformat(),
                'sources': sources
            })
        except Exception as e:
            print(f"Error finding sources for download '{filename}': {e}")
            # Still add the download, but without sources
            download_sources.append({
                'filename': filename,
                'download_url': download_url,
                'download_time': download_time.isoformat(),
                'sources': []
            })
    
    return download_sources