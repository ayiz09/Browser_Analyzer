from flask import Blueprint, render_template, request, jsonify
import os
from utils.file_utils import generate_file_id, get_temp_file_path, detect_browser_type
from services.history_processor import process_history_file
from config import Config

main_bp = Blueprint('main', __name__, template_folder='templates')

@main_bp.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@main_bp.route('/upload', methods=['POST'])
def upload_file():
    """Upload and process a browser history file"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Get pagination parameters
    page = request.form.get('page', 1, type=int)
    page_size = request.form.get('page_size', Config.DEFAULT_PAGE_SIZE, type=int)
    
    # Create a unique file ID
    file_id = generate_file_id()
    
    # Create a temporary file
    temp_path = get_temp_file_path(file_id)
    file.save(temp_path)
    
    # Add debugging output
    print(f"File saved to: {temp_path}")
    
    try:
        # Determine file type based on name or content
        browser_type = detect_browser_type(file.filename)
        print(f"Detected browser type: {browser_type}")
        
        # Process the file
        result = process_history_file(temp_path, browser_type, file_id, page, page_size)
        print(f"Processing complete, result: {result.keys() if isinstance(result, dict) else 'Error'}")
        
        # Return the response
        response = jsonify(result)
        response.set_cookie('last_file_id', file_id, max_age=3600)
        return response
    except Exception as e:
        print(f"Error in upload_file: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500