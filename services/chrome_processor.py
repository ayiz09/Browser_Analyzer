"""
Chrome browser history processor module.
"""
import sqlite3
import os
import json
import pandas as pd
from services.storage import store_processed_data
from utils.url_utils import extract_domain
from utils.file_utils import extract_filename
from utils.time_utils import convert_download_state, map_chrome_visit_source, chrome_time_to_datetime
from services.common_utils import find_download_sources

def process_chrome_history(file_path, file_id, page=1, page_size=1000):
    """Process Chrome/Edge history database"""
    try:
        conn = sqlite3.connect(file_path)
        
        # Calculate total entries
        count_query = """
        SELECT COUNT(*) as total
        FROM urls u
        JOIN visits v ON u.id = v.url
        """
        
        count_df = pd.read_sql_query(count_query, conn)
        total_entries = int(count_df['total'].iloc[0])
        
        # Calculate start and end indices for pagination
        offset = (page - 1) * page_size
        
        # Query with pagination
        query = f"""
        SELECT 
            u.id, 
            u.url, 
            u.title, 
            u.visit_count, 
            datetime(v.visit_time/1000000-11644473600, 'unixepoch') as visit_time
        FROM urls u
        JOIN visits v ON u.id = v.url
        ORDER BY v.visit_time DESC
        LIMIT {page_size} OFFSET {offset}
        """
        
        # Get all entries for memory storage (for export)
        full_query = """
        SELECT 
            u.id, 
            u.url, 
            u.title, 
            u.visit_count, 
            datetime(v.visit_time/1000000-11644473600, 'unixepoch') as visit_time
        FROM urls u
        JOIN visits v ON u.id = v.url
        ORDER BY v.visit_time DESC
        """
        
        # Execute queries
        df = pd.read_sql_query(query, conn)
        full_df = pd.read_sql_query(full_query, conn)
        
        # Process data
        df['domain'] = df['url'].apply(extract_domain)
        full_df['domain'] = full_df['url'].apply(extract_domain)
        
        # Check if visit_source table exists - this is important for sync information
        sync_visits = []
        
        table_query = "SELECT name FROM sqlite_master WHERE type='table'"
        tables_df = pd.read_sql_query(table_query, conn)
        tables = tables_df['name'].tolist()
        print(f"Found tables in Chrome history: {tables}")
        
        # If visit_source exists, we can get information about synced visits
        if 'visit_source' in tables:
            try:
                # Get visits with their sources
                synced_visits_query = """
                SELECT 
                    u.url,
                    u.title,
                    datetime(v.visit_time/1000000-11644473600, 'unixepoch') as visit_time,
                    vs.source
                FROM urls u
                JOIN visits v ON u.id = v.url
                JOIN visit_source vs ON v.id = vs.id
                ORDER BY v.visit_time DESC
                LIMIT 1000
                """
                
                synced_df = pd.read_sql_query(synced_visits_query, conn)
                
                if not synced_df.empty:
                    # Map source codes to descriptions
                    synced_df['source_desc'] = synced_df['source'].apply(map_chrome_visit_source)
                    sync_visits = synced_df.to_dict('records')
            except Exception as e:
                print(f"Error getting synced visits: {e}")
        
        # Process downloads
        downloads, download_sources = process_chrome_downloads(conn, tables, full_df)
        
        # Get sync information
        sync_info = extract_chrome_sync_info(file_path)
        
        # Add synced visits to sync info
        if sync_visits:
            if not sync_info:
                sync_info = {}
            sync_info['synced_visits'] = sync_visits
        
        conn.close()
        
        # Convert to list of dictionaries
        result = df.to_dict('records')
        all_entries = full_df.to_dict('records')
        
        # Store in memory for pagination and export
        store_processed_data(
            file_id, 
            'chrome', 
            all_entries, 
            total_entries, 
            downloads, 
            download_sources,
            sync_info
        )
        
        return {
            'file_id': file_id,
            'browser_type': 'chrome',
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
        print(f"Error processing Chrome history: {e}")
        import traceback
        traceback.print_exc()
        return {'error': f"Error processing Chrome history: {str(e)}"}

def process_chrome_downloads(conn, tables, full_df):
    """Process Chrome downloads"""
    downloads = []
    download_sources = []
    
    if 'downloads' in tables:
        try:
            # Check the schema of downloads table to find the correct column names
            schema_query = "PRAGMA table_info(downloads);"
            schema_df = pd.read_sql_query(schema_query, conn)
            
            # Print schema for debugging
            print("Downloads table schema:", schema_df['name'].tolist())
            
            # Check if specific columns exist
            has_target_path = 'target_path' in schema_df['name'].values
            has_current_path = 'current_path' in schema_df['name'].values
            has_url_column = 'url' in schema_df['name'].values
            has_tab_url = 'tab_url' in schema_df['name'].values
            has_original_url = 'original_url' in schema_df['name'].values
            
            # Build a dynamic query based on the schema
            filename_col = 'target_path' if has_target_path else ('current_path' if has_current_path else 'id')
            url_col = 'url' if has_url_column else ('tab_url' if has_tab_url else ('original_url' if has_original_url else None))
            
            if url_col:
                download_query = f"""
                SELECT 
                    d.{filename_col} as filename,
                    d.{url_col} as url,
                    IFNULL(d.referrer, '') as referrer,
                    datetime(d.start_time/1000000-11644473600, 'unixepoch') as download_time,
                    IFNULL(d.mime_type, '') as mime_type,
                    IFNULL(d.received_bytes, 0) as file_size,
                    IFNULL(d.state, 0) as status
                FROM downloads d
                ORDER BY d.start_time DESC
                """
                
                downloads_df = pd.read_sql_query(download_query, conn)
                
                # Process downloads data
                if not downloads_df.empty:
                    # Extract just the filename from the full path
                    downloads_df['filename'] = downloads_df['filename'].apply(extract_filename)
                    
                    # Convert state codes to text
                    downloads_df['status'] = downloads_df['status'].apply(convert_download_state)
                    
                    downloads = downloads_df.to_dict('records')
                    
                    # Find download sources by correlating with history
                    download_sources = find_download_sources(full_df, downloads)
            else:
                print("Cannot find a suitable URL column in downloads table")
        except Exception as e:
            print(f"Error processing Chrome downloads: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("Downloads table not found in Chrome history")
        
        # Try an alternative approach - look for downloads in URLs
        try:
            # Look for URLs that might be downloads
            download_url_query = """
            SELECT 
                u.url as url,
                u.title as title,
                datetime(u.last_visit_time/1000000-11644473600, 'unixepoch') as download_time
            FROM urls u
            WHERE u.url LIKE '%/download%' 
               OR u.url LIKE '%.exe' 
               OR u.url LIKE '%.zip' 
               OR u.url LIKE '%.pdf'
               OR u.url LIKE '%.doc%'
               OR u.url LIKE '%.xls%'
               OR u.url LIKE '%.jpg'
               OR u.url LIKE '%.png'
               OR u.url LIKE '%.mp3'
               OR u.url LIKE '%.mp4'
            ORDER BY u.last_visit_time DESC
            LIMIT 100
            """
            
            downloads_df = pd.read_sql_query(download_url_query, conn)
            
            if not downloads_df.empty:
                # Extract filename from URL
                downloads_df['filename'] = downloads_df['url'].apply(lambda url: url.split('/')[-1])
                downloads_df['referrer'] = ''
                downloads_df['mime_type'] = ''
                downloads_df['file_size'] = 0
                downloads_df['status'] = 'completed'  # Assume completed
                
                downloads = downloads_df.to_dict('records')
                download_sources = find_download_sources(full_df, downloads)
        except Exception as e:
            print(f"Error with alternative download detection: {e}")
    
    return downloads, download_sources

def extract_chrome_sync_info(history_file_path):
    """
    Extract Chrome sync information from the history file and/or Preferences file
    """
    try:
        # For actual sync information, we need the Preferences file
        # Check if we can locate it in the same directory
        profile_dir = os.path.dirname(history_file_path)
        preferences_path = os.path.join(profile_dir, 'Preferences')
        
        sync_info = {}
        
        # If we found a Preferences file, parse it for sync information
        if os.path.exists(preferences_path):
            print(f"Found Chrome Preferences file at: {preferences_path}")
            
            try:
                with open(preferences_path, 'r', encoding='utf-8') as f:
                    prefs_data = json.load(f)
                
                # Extract account info
                account_info = {}
                if 'account_info' in prefs_data:
                    account_data = prefs_data['account_info']
                    
                    # Check if account_data is a list instead of a dictionary
                    if isinstance(account_data, list):
                        # Handle case where account_info is a list
                        if account_data and len(account_data) > 0:
                            # Use the first account in the list
                            first_account = account_data[0]
                            if isinstance(first_account, dict):
                                account_info = {
                                    'email': first_account.get('email', ''),
                                    'name': first_account.get('full_name', ''),
                                    'account_type': first_account.get('account_type', ''),
                                }
                            else:
                                account_info = {
                                    'email': '',
                                    'name': '',
                                    'account_type': '',
                                    'note': 'Unable to parse account data'
                                }
                    elif isinstance(account_data, dict):
                        # Original case - account_info is a dictionary
                        account_info = {
                            'email': account_data.get('email', ''),
                            'name': account_data.get('full_name', ''),
                            'account_type': account_data.get('account_type', ''),
                        }
                    else:
                        # Unknown type
                        account_info = {
                            'email': '',
                            'name': '',
                            'account_type': '',
                            'note': f'Unexpected account_info type: {type(account_data)}'
                        }
                
                # Extract sync settings
                sync_settings = {
                    'enabled': False,
                    'first_sync_time': '',
                    'last_sync_time': '',
                    'data_types': []
                }
                
                if 'sync' in prefs_data:
                    sync_data = prefs_data['sync']
                    
                    # Check if sync is enabled
                    if 'encryption' in sync_data and 'enabled' in sync_data['encryption']:
                        sync_settings['enabled'] = True
                    
                    # Get sync timestamps
                    if 'first_setup_complete' in sync_data:
                        sync_settings['first_sync_time'] = chrome_time_to_datetime(sync_data.get('first_setup_time', 0))
                    
                    if 'last_synced_time' in sync_data:
                        sync_settings['last_sync_time'] = chrome_time_to_datetime(sync_data.get('last_synced_time', 0))
                        account_info['last_sync_time'] = sync_settings['last_sync_time']
                    
                    # Extract sync data types
                    data_types = []
                    
                    # Check which data types are being synced
                    if 'preferred_data_types' in sync_data:
                        types_data = sync_data['preferred_data_types']
                        for data_type, value in types_data.items():
                            data_types.append({
                                'name': data_type,
                                'enabled': value
                            })
                    
                    sync_settings['data_types'] = data_types
                
                sync_info = {
                    'account_info': account_info,
                    'sync_settings': sync_settings
                }
                
                print(f"Extracted Chrome sync info: {sync_info}")
                return sync_info
                
            except Exception as e:
                print(f"Error parsing Chrome Preferences file: {e}")
                import traceback
                traceback.print_exc()
                return {'account_info': {}, 'sync_settings': {}}
        else:
            print(f"Chrome Preferences file not found at: {preferences_path}")
            # We can still return what we have from the history database
            return {}
        
    except Exception as e:
        print(f"Error extracting Chrome sync info: {e}")
        import traceback
        traceback.print_exc()
        return {}