"""
Firefox browser history processor module.
"""
import sqlite3
import os
import re
import pandas as pd
from services.storage import store_processed_data
from utils.url_utils import extract_domain
from utils.file_utils import extract_filename
from services.common_utils import find_download_sources

def process_firefox_history(file_path, file_id, page=1, page_size=1000):
    """Process Firefox history database"""
    try:
        conn = sqlite3.connect(file_path)
        
        # Calculate total entries
        count_query = """
        SELECT COUNT(*) as total
        FROM moz_places p
        JOIN moz_historyvisits h ON p.id = h.place_id
        """
        
        count_df = pd.read_sql_query(count_query, conn)
        total_entries = int(count_df['total'].iloc[0])
        
        # Calculate start and end indices for pagination
        offset = (page - 1) * page_size
        
        # Query with pagination
        query = f"""
        SELECT 
            p.id, 
            p.url, 
            p.title, 
            p.visit_count, 
            datetime(h.visit_date/1000000, 'unixepoch') as visit_time
        FROM moz_places p
        JOIN moz_historyvisits h ON p.id = h.place_id
        ORDER BY h.visit_date DESC
        LIMIT {page_size} OFFSET {offset}
        """
        
        # Get all entries for memory storage (for export)
        full_query = """
        SELECT 
            p.id, 
            p.url, 
            p.title, 
            p.visit_count, 
            datetime(h.visit_date/1000000, 'unixepoch') as visit_time
        FROM moz_places p
        JOIN moz_historyvisits h ON p.id = h.place_id
        ORDER BY h.visit_date DESC
        """
        
        # Execute queries
        df = pd.read_sql_query(query, conn)
        full_df = pd.read_sql_query(full_query, conn)
        
        # Process data
        df['domain'] = df['url'].apply(extract_domain)
        full_df['domain'] = full_df['url'].apply(extract_domain)
        
        # Process downloads
        downloads, download_sources = process_firefox_downloads(conn, full_df)
        
        # Get sync information for Firefox
        try:
            sync_info = extract_firefox_sync_info(file_path)
        except Exception as e:
            print(f"Error extracting Firefox sync info: {e}")
            import traceback
            traceback.print_exc()
            sync_info = {}
        
        conn.close()
        
        # Convert to list of dictionaries
        result = df.to_dict('records')
        all_entries = full_df.to_dict('records')
        
        # Store in memory for pagination and export
        store_processed_data(
            file_id, 
            'firefox', 
            all_entries, 
            total_entries, 
            downloads, 
            download_sources,
            sync_info
        )
        
        return {
            'file_id': file_id,
            'browser_type': 'firefox',
            'total_entries': total_entries,
            'page': page,
            'page_size': page_size,
            'total_pages': (total_entries + page_size - 1) // page_size,
            'entries': result,
            'downloads': downloads,
            'download_sources': download_sources,
            'sync_info': sync_info
        }
    except Exception as e:
        print(f"Error processing Firefox history: {e}")
        import traceback
        traceback.print_exc()
        return {'error': f"Error processing Firefox history: {str(e)}"}

def process_firefox_downloads(conn, full_df):
    """Process Firefox downloads"""
    try:
        # Check if moz_anno_attributes table exists
        check_query = "SELECT name FROM sqlite_master WHERE type='table' AND name='moz_anno_attributes'"
        anno_tables = pd.read_sql_query(check_query, conn)
        
        # Print for debugging
        print(f"Found tables: {anno_tables['name'].tolist() if not anno_tables.empty else 'None'}")
        
        # First try the original method
        if not anno_tables.empty and 'moz_anno_attributes' in anno_tables['name'].values:
            download_query = """
            SELECT 
                a.content as filename,
                p.url as url,
                datetime(a.dateAdded/1000000, 'unixepoch') as download_time,
                '' as mime_type,
                0 as file_size
            FROM moz_annos a
            JOIN moz_places p ON a.place_id = p.id
            WHERE a.anno_attribute_id IN (
                SELECT id FROM moz_anno_attributes WHERE name LIKE '%download%'
            )
            ORDER BY a.dateAdded DESC
            """
        else:
            # Fallback to a direct query if moz_anno_attributes doesn't exist
            download_query = """
            SELECT 
                a.content as filename,
                p.url as url,
                datetime(a.dateAdded/1000000, 'unixepoch') as download_time,
                '' as mime_type,
                0 as file_size
            FROM moz_annos a
            JOIN moz_places p ON a.place_id = p.id
            ORDER BY a.dateAdded DESC
            """
        
        downloads_df = pd.read_sql_query(download_query, conn)
        
        # If no results, try an alternative approach
        if downloads_df.empty:
            print("No downloads found with standard query, trying alternative...")
            
            # Try to directly query the moz_annos table
            direct_query = """
            SELECT 
                a.content as filename,
                p.url as url,
                datetime(a.dateAdded/1000000, 'unixepoch') as download_time,
                a.type as file_type
            FROM moz_annos a
            JOIN moz_places p ON a.place_id = p.id
            ORDER BY a.dateAdded DESC
            """
            
            downloads_df = pd.read_sql_query(direct_query, conn)
            print(f"Direct query found {len(downloads_df)} potential downloads")
        
        # Process downloads data
        if not downloads_df.empty:
            # Clean up and process the data
            downloads_df['filename'] = downloads_df['filename'].apply(extract_filename)
            downloads_df['referrer'] = ''  # Firefox doesn't store referrer for downloads directly
            downloads_df['status'] = 'completed'  # Default status
            downloads_df['file_size'] = 0  # Default file size
            downloads_df['mime_type'] = ''  # Default mime type
            
            # Further cleaning - remove rows with empty filename or URL
            downloads_df = downloads_df.dropna(subset=['filename']).copy()
            downloads_df = downloads_df[downloads_df['filename'] != ''].copy()
            
            if not downloads_df.empty:
                downloads = downloads_df.to_dict('records')
                # Find download sources by correlating with history
                download_sources = find_download_sources(full_df, downloads)
            else:
                downloads = []
                download_sources = []
        else:
            downloads = []
            download_sources = []
    except Exception as e:
        print(f"Error processing Firefox downloads: {e}")
        import traceback
        traceback.print_exc()
        downloads = []
        download_sources = []
    
    return downloads, download_sources

def extract_firefox_sync_info(places_file_path):
    """
    Extract Firefox sync information from the places.sqlite file and/or prefs.js file
    """
    try:
        # For Firefox, we need to check for prefs.js file in the same directory
        profile_dir = os.path.dirname(places_file_path)
        prefs_path = os.path.join(profile_dir, 'prefs.js')
        
        sync_info = {}
        
        # If we found a prefs.js file, parse it for sync information
        if os.path.exists(prefs_path):
            print(f"Found Firefox prefs.js file at: {prefs_path}")
            
            # prefs.js is not JSON, so we need to parse it line by line
            try:
                account_info = {}
                sync_settings = {
                    'enabled': False,
                    'last_sync_time': '',
                    'first_sync_time': '',
                    'data_types': []
                }
                
                with open(prefs_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                
                # Look for sync-related preferences
                for line in lines:
                    line = line.strip()
                    
                    # Check for sync account information
                    if 'services.sync.username' in line:
                        # Extract the email/username
                        match = re.search(r'user_pref\("services\.sync\.username", "([^"]+)"\);', line)
                        if match:
                            account_info['email'] = match.group(1)
                    
                    # Check if sync is enabled
                    if 'services.sync.enabled' in line:
                        match = re.search(r'user_pref\("services\.sync\.enabled", (true|false)\);', line)
                        if match:
                            sync_settings['enabled'] = (match.group(1) == 'true')
                    
                    # Last sync time
                    if 'services.sync.lastSync' in line:
                        match = re.search(r'user_pref\("services\.sync\.lastSync", "([^"]+)"\);', line)
                        if match:
                            sync_settings['last_sync_time'] = match.group(1)
                    
                    # Firefox sync engine states for different data types
                    if 'services.sync.engine' in line:
                        # Check if the data type is enabled
                        match = re.search(r'user_pref\("services\.sync\.engine\.([^"]+)", (true|false)\);', line)
                        if match:
                            data_type = match.group(1)
                            enabled = (match.group(2) == 'true')
                            
                            # Add to data types list if not already present
                            data_type_exists = False
                            for dt in sync_settings['data_types']:
                                if dt['name'] == data_type:
                                    dt['enabled'] = enabled
                                    data_type_exists = True
                                    break
                            
                            if not data_type_exists:
                                sync_settings['data_types'].append({
                                    'name': data_type,
                                    'enabled': enabled
                                })
                
                # If an account email was found, assume the account is valid
                if account_info.get('email'):
                    account_info['name'] = account_info.get('email').split('@')[0]  # Use part before @ as name
                    account_info['account_type'] = 'Firefox Account'
                    account_info['last_sync_time'] = sync_settings.get('last_sync_time', '')
                
                sync_info = {
                    'account_info': account_info,
                    'sync_settings': sync_settings
                }
                
                print(f"Extracted Firefox sync info: {sync_info}")
                return sync_info
                
            except Exception as e:
                print(f"Error parsing Firefox prefs.js file: {e}")
                import traceback
                traceback.print_exc()
                return {'account_info': {}, 'sync_settings': {}}
        else:
            print(f"Firefox prefs.js file not found at: {prefs_path}")
            return {}
        
    except Exception as e:
        print(f"Error extracting Firefox sync info: {e}")
        import traceback
        traceback.print_exc()
        return {}