from flask import Blueprint, request, jsonify, send_file, Response
import os
import csv
from config import Config
from services.storage import get_processed_data, file_exists, update_sync_info
from utils.file_utils import get_temp_file_path, get_csv_file_path, detect_browser_type
from services.history_processor import process_history_file
from services.chrome_processor import extract_chrome_sync_info
from services.firefox_processor import extract_firefox_sync_info

sync_bp = Blueprint('sync', __name__)

@sync_bp.route('/get_sync_info', methods=['GET'])
def get_sync_info():
    """Get sync information from a browser history file"""
    file_id = request.args.get('file_id')
    
    if not file_id or not file_exists(file_id):
        return jsonify({'error': 'Invalid file ID'}), 400
    
    # Get data
    data = get_processed_data(file_id)
    
    # If sync info not already processed, try to extract it now
    if 'sync_info' not in data or not data['sync_info']:
        try:
            file_path = get_temp_file_path(file_id)
            browser_type = data['browser_type']
            
            # Extract sync information
            if browser_type == 'chrome':
                sync_info = extract_chrome_sync_info(file_path)
            else:
                sync_info = extract_firefox_sync_info(file_path)
                
            # Save to processed_files
            update_sync_info(file_id, sync_info)
            
            # Update local data copy
            data['sync_info'] = sync_info
        except Exception as e:
            print(f"Error extracting sync info: {e}")
            import traceback
            traceback.print_exc()
            sync_info = {}
    else:
        sync_info = data['sync_info']
    
    return jsonify({
        'file_id': file_id,
        'browser_type': data['browser_type'],
        'sync_info': sync_info
    })

@sync_bp.route('/export_sync_data/<file_id>', methods=['GET'])
def export_sync_data(file_id):
    """Export synchronized browser data to CSV"""
    print(f"Export sync data request for file_id: {file_id}")
    
    # Ensure the file_id is a string for comparison
    file_id_str = str(file_id)
    
    if not file_exists(file_id_str):
        return jsonify({'error': f"Invalid file ID: {file_id}"}), 400
    
    # Get data
    data = get_processed_data(file_id_str)
    
    if 'sync_info' not in data or not data['sync_info']:
        return jsonify({'error': 'No sync data available'}), 404
    
    # Create a temporary CSV file with an absolute path
    temp_csv = get_csv_file_path(file_id_str, "sync")
    abs_path = os.path.abspath(temp_csv)
    
    try:
        # Get synced visits if available
        synced_visits = data['sync_info'].get('synced_visits', [])
        
        if not synced_visits:
            return jsonify({'error': 'No synchronized visits available for export'}), 404
        
        # Write data to CSV
        with open(abs_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['title', 'url', 'visit_time', 'source', 'source_desc']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for visit in synced_visits:
                writer.writerow({
                    'title': visit.get('title', ''),
                    'url': visit.get('url', ''),
                    'visit_time': visit.get('visit_time', ''),
                    'source': visit.get('source', ''),
                    'source_desc': visit.get('source_desc', '')
                })
        
        # Send the file
        try:
            response = send_file(
                abs_path,
                as_attachment=True,
                download_name=f'browser_sync_data_{file_id}.csv',
                mimetype='text/csv'
            )
            return response
        except Exception as send_error:
            # Alternative methods for sending the file
            try:
                with open(abs_path, 'r', encoding='utf-8') as f:
                    csv_content = f.read()
                
                response = Response(
                    csv_content,
                    mimetype='text/csv',
                    headers={
                        'Content-Disposition': f'attachment; filename=browser_sync_data_{file_id}.csv'
                    }
                )
                return response
            except Exception as manual_error:
                return jsonify({'error': f"Could not send sync data file: {str(manual_error)}"}), 500
    
    except Exception as e:
        print(f"Error during sync data export: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f"Sync data export error: {str(e)}"}), 500