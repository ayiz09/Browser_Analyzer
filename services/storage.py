# In-memory storage for processed files
processed_files = {}

def store_processed_data(file_id, browser_type, entries, total_entries, downloads=None, download_sources=None, sync_info=None):
    """Store processed data in memory"""
    processed_files[file_id] = {
        'browser_type': browser_type,
        'total_entries': total_entries,
        'entries': entries,
        'downloads': downloads or [],
        'download_sources': download_sources or [],
        'sync_info': sync_info or {}
    }
    
    # Print processed files after update for debugging
    print(f"After storing, processed_files has keys: {list(processed_files.keys())}")

def get_processed_data(file_id):
    """Get processed data from memory"""
    return processed_files.get(file_id)

def update_sync_info(file_id, sync_info):
    """Update sync info for a file"""
    if file_id in processed_files:
        processed_files[file_id]['sync_info'] = sync_info

def file_exists(file_id):
    """Check if a file exists in memory"""
    return file_id in processed_files

def get_paginated_entries(file_id, page, page_size):
    """Get paginated entries for a file"""
    if file_id not in processed_files:
        return None
    
    # Calculate start and end indices
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    
    # Get entries for the requested page
    data = processed_files[file_id]
    entries = data['entries'][start_idx:end_idx]
    
    return {
        'file_id': file_id,
        'browser_type': data['browser_type'],
        'total_entries': data['total_entries'],
        'page': page,
        'page_size': page_size,
        'total_pages': (data['total_entries'] + page_size - 1) // page_size,
        'entries': entries,
        'downloads': data.get('downloads', []),
        'download_sources': data.get('download_sources', []),
        'sync_info': data.get('sync_info', {})
    }

def list_file_ids():
    """List all file IDs in storage"""
    return list(processed_files.keys())