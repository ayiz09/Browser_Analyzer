from flask import Blueprint, request, jsonify, send_file, Response
import os
import csv
from config import Config
from services.storage import get_paginated_entries, file_exists, get_processed_data
from utils.file_utils import get_temp_file_path, get_csv_file_path, detect_browser_type
from services.history_processor import process_history_file

history_bp = Blueprint('history', __name__)

@history_bp.route('/get_page', methods=['GET'])
def get_page():
    """Get a page of history entries"""
    file_id = request.args.get('file_id')
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', Config.DEFAULT_PAGE_SIZE, type=int)
    
    if not file_id or not file_exists(file_id):
        return jsonify({'error': 'Invalid file ID'}), 400
    
    # Get paginated entries
    result = get_paginated_entries(file_id, page, page_size)
    
    return jsonify(result)

@history_bp.route('/export/<file_id>', methods=['GET'])
def export_csv(file_id):
    """Export history data to CSV"""
    # Add debugging info
    print(f"Export request for file_id: {file_id}")
    
    # Ensure the file_id is a string for comparison
    file_id_str = str(file_id)
    
    # If the file is not in memory, try to check if the file exists in the upload folder
    if not file_exists(file_id_str):
        temp_path = get_temp_file_path(file_id_str)
        
        if not os.path.exists(temp_path):
            return jsonify({'error': f"Invalid file ID: {file_id}"}), 400
        
        # Try to re-process the file if it exists but not in memory
        try:
            print(f"File found on disk but not in memory, attempting to re-process: {temp_path}")
            browser_type = detect_browser_type(temp_path)
            process_history_file(temp_path, browser_type, file_id_str, 1, Config.DEFAULT_PAGE_SIZE)
            
            if not file_exists(file_id_str):
                return jsonify({'error': 'Failed to re-process file'}), 500
        except Exception as e:
            print(f"Error re-processing file: {e}")
            return jsonify({'error': f"Error re-processing file: {str(e)}"}), 500
    
    # Get data for export
    data = get_processed_data(file_id_str)
    
    # Validate that entries exist
    if not data or 'entries' not in data or not data['entries']:
        return jsonify({'error': 'No entries available for export'}), 400
    
    # Create a temporary CSV file with an absolute path
    temp_csv = get_csv_file_path(file_id_str)
    abs_path = os.path.abspath(temp_csv)
    print(f"Creating CSV at absolute path: {abs_path}")
    
    # Ensure the directory exists
    dir_path = os.path.dirname(abs_path)
    os.makedirs(dir_path, exist_ok=True)
    print(f"Ensured directory exists: {dir_path} - Exists: {os.path.exists(dir_path)}")
    
    try:
        # Write data to CSV
        print(f"Starting to write data to file: {abs_path}")
        with open(abs_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['title', 'url', 'visit_time', 'domain', 'visit_count']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            entry_count = 0
            for entry in data['entries']:
                # Filter only needed fields and ensure all values are present
                row = {
                    'title': entry.get('title', ''),
                    'url': entry.get('url', ''),
                    'visit_time': entry.get('visit_time', ''),
                    'domain': entry.get('domain', ''),
                    'visit_count': entry.get('visit_count', 0)
                }
                writer.writerow(row)
                entry_count += 1
            
            print(f"Wrote {entry_count} entries to CSV file")
        
        # Check if file was created successfully
        if not os.path.exists(abs_path):
            print(f"ERROR: File was not created at {abs_path}")
            return jsonify({'error': 'Failed to create export file'}), 500
        else:
            file_size = os.path.getsize(abs_path)
            print(f"File successfully created at {abs_path}, size: {file_size} bytes")
            
            # For debugging, list the directory contents
            print(f"Directory contents of {dir_path}:")
            for file in os.listdir(dir_path):
                file_path = os.path.join(dir_path, file)
                print(f"  - {file} ({os.path.getsize(file_path)} bytes)")
            
        # Use Flask's send_file with careful error handling
        try:
            print(f"Attempting to send file: {abs_path}")
            response = send_file(
                abs_path,
                as_attachment=True,
                download_name=f'browser_history_{file_id}.csv',
                mimetype='text/csv'
            )
            print("send_file successful")
            return response
        except Exception as send_error:
            print(f"Error in send_file: {send_error}")
            # Try alternative method for older Flask versions
            try:
                print("Trying alternative send_file method")
                return send_file(
                    abs_path,
                    as_attachment=True,
                    attachment_filename=f'browser_history_{file_id}.csv',
                    mimetype='text/csv'
                )
            except Exception as alt_error:
                print(f"Alternative method also failed: {alt_error}")
                
                # Last resort - try to read the file and send the contents manually
                try:
                    print("Trying to read file and send manually")
                    with open(abs_path, 'r', encoding='utf-8') as f:
                        csv_content = f.read()
                    
                    response = Response(
                        csv_content,
                        mimetype='text/csv',
                        headers={
                            'Content-Disposition': f'attachment; filename=browser_history_{file_id}.csv'
                        }
                    )
                    return response
                except Exception as manual_error:
                    print(f"Manual method also failed: {manual_error}")
                    return jsonify({'error': f"Could not send file: {str(manual_error)}"}), 500
                
    except Exception as e:
        print(f"Error during export for {file_id}: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        print(f"Error details: {repr(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f"Export error: {str(e)}"}), 500