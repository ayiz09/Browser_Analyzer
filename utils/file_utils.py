import os
import uuid
from config import Config

def ensure_upload_directory():
    """Create upload folder if it doesn't exist"""
    print(f"Setting upload folder to: {Config.UPLOAD_FOLDER}")
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    print(f"Created upload folder at: {Config.UPLOAD_FOLDER} - Exists: {os.path.exists(Config.UPLOAD_FOLDER)}")

def generate_file_id():
    """Generate a unique file ID"""
    file_id = str(uuid.uuid4())
    print(f"Created new file_id: {file_id}")
    return file_id

def get_temp_file_path(file_id):
    """Get the path to the temporary file"""
    return os.path.join(Config.UPLOAD_FOLDER, f"{file_id}.db")

def get_csv_file_path(file_id, type_suffix=""):
    """Get the path to a CSV file for export"""
    suffix = f"_{type_suffix}" if type_suffix else ""
    return os.path.join(Config.UPLOAD_FOLDER, f"{file_id}{suffix}.csv")

def detect_browser_type(filename):
    """Determine browser type based on file name"""
    filename = filename.lower()
    if 'places.sqlite' in filename or filename.endswith('.sqlite'):
        return 'firefox'
    else:
        return 'chrome'

def extract_filename(path):
    """Extract filename from a path"""
    try:
        if not path:
            return ""
        
        # Handle file:/// URLs
        if path.startswith('file:///'):
            path = path[8:]
        
        # Get the filename from the path
        return os.path.basename(path)
    except:
        return path