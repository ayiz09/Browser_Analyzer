"""
Main history processor module that coordinates browser-specific processors.
"""
import os
from utils.file_utils import detect_browser_type

def process_history_file(file_path, browser_type, file_id, page=1, page_size=1000):
    """Process history file based on browser type"""
    try:
        # Dynamic import to avoid circular dependencies
        if browser_type == 'firefox':
            from services.firefox_processor import process_firefox_history
            return process_firefox_history(file_path, file_id, page, page_size)
        else:
            from services.chrome_processor import process_chrome_history
            return process_chrome_history(file_path, file_id, page, page_size)
    except Exception as e:
        print(f"Error processing {browser_type} history: {e}")
        import traceback
        traceback.print_exc()
        return {'error': f"Error processing {browser_type} history: {str(e)}"}