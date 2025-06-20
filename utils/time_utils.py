from datetime import datetime

def chrome_time_to_datetime(chrome_time):
    """
    Convert Chrome's timestamp format (microseconds since 1601-01-01) to a readable date string
    """
    try:
        if not chrome_time:
            return ""
        
        # Chrome time is microseconds since 1601-01-01
        # First convert to seconds
        chrome_time_seconds = int(chrome_time) / 1000000
        
        # Adjust for epoch difference (seconds between 1601-01-01 and 1970-01-01)
        epoch_adjust = 11644473600
        unix_time = chrome_time_seconds - epoch_adjust
        
        # Convert to datetime
        dt = datetime.fromtimestamp(unix_time)
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        print(f"Error converting Chrome time: {e}")
        return ""

def convert_download_state(state):
    """Convert Chrome download state code to text"""
    # Chrome download states
    states = {
        0: 'in_progress',
        1: 'completed',
        2: 'canceled',
        3: 'failed',
        4: 'interrupted'
    }
    
    return states.get(state, 'unknown')

def map_chrome_visit_source(source_code):
    """
    Map Chrome's visit_source integer codes to human-readable descriptions
    """
    sources = {
        0: 'Synchronised from another device',
        1: 'User browsed',
        2: 'Added by an extension',
        3: 'Imported from Firefox',
        4: 'Imported from IE',
        5: 'Imported from Safari'
    }
    
    return sources.get(source_code, f'Unknown source ({source_code})')