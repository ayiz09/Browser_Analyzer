from flask import Blueprint, request, jsonify, send_file, Response
import os
import csv
from config import Config
from services.storage import get_processed_data, file_exists
from utils.file_utils import get_temp_file_path, get_csv_file_path, detect_browser_type
from services.history_processor import process_history_file

download_bp = Blueprint('download', __name__)

@download_bp.route('/get_downloads', methods=['GET'])
def get_downloads():
    """Get download information"""
    file_id = request.args.get('file_id')
    
    if not file_id or not file_exists(file_id):
        return jsonify({'error': 'Invalid file ID'}), 400
    
    # Get data
    data = get_processed_data(file_id)
    
    return jsonify({
        'file_id': file_id,
        'browser_type': data['browser_type'],
        'downloads': data.get('downloads', []),
        'download_sources': data.get('download_sources', [])
    })

@download_bp.route('/export_downloads/<file_id>', methods=['GET'])
def export_downloads_csv(file_id):
    """Export downloads data to CSV"""
    # Add debugging info
    print(f"Export downloads request for file_id: {file_id}")
    
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
    
    if 'downloads' not in data or not data['downloads']:
        return jsonify({'error': 'No download data available'}), 404
    
    # Create a temporary CSV file with an absolute path
    temp_csv = get_csv_file_path(file_id_str, "downloads")
    abs_path = os.path.abspath(temp_csv)
    print(f"Creating downloads CSV at absolute path: {abs_path}")
    
    # Ensure the directory exists
    dir_path = os.path.dirname(abs_path)
    os.makedirs(dir_path, exist_ok=True)
    
    try:
        # Write data to CSV
        print(f"Starting to write downloads data to file: {abs_path}")
        with open(abs_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['filename', 'url', 'referrer', 'download_time', 'file_size', 'mime_type', 'status']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            download_count = 0
            for download in data['downloads']:
                # Filter only needed fields
                row = {
                    'filename': download.get('filename', ''),
                    'url': download.get('url', ''),
                    'referrer': download.get('referrer', ''),
                    'download_time': download.get('download_time', ''),
                    'file_size': download.get('file_size', ''),
                    'mime_type': download.get('mime_type', ''),
                    'status': download.get('status', '')
                }
                writer.writerow(row)
                download_count += 1
            
            print(f"Wrote {download_count} downloads to CSV file")
        
        # Check if file was created successfully
        if not os.path.exists(abs_path):
            print(f"ERROR: Downloads file was not created at {abs_path}")
            return jsonify({'error': 'Failed to create downloads export file'}), 500
        
        # Use Flask's send_file with careful error handling
        try:
            print(f"Attempting to send downloads file: {abs_path}")
            response = send_file(
                abs_path,
                as_attachment=True,
                download_name=f'browser_downloads_{file_id}.csv',
                mimetype='text/csv'
            )
            print("send_file successful for downloads")
            return response
        except Exception as send_error:
            print(f"Error in send_file for downloads: {send_error}")
            # Try alternative method for older Flask versions
            try:
                print("Trying alternative send_file method for downloads")
                return send_file(
                    abs_path,
                    as_attachment=True,
                    attachment_filename=f'browser_downloads_{file_id}.csv',
                    mimetype='text/csv'
                )
            except Exception as alt_error:
                print(f"Alternative method also failed for downloads: {alt_error}")
                
                # Last resort - try to read the file and send the contents manually
                try:
                    print("Trying to read downloads file and send manually")
                    with open(abs_path, 'r', encoding='utf-8') as f:
                        csv_content = f.read()
                    
                    response = Response(
                        csv_content,
                        mimetype='text/csv',
                        headers={
                            'Content-Disposition': f'attachment; filename=browser_downloads_{file_id}.csv'
                        }
                    )
                    return response
                except Exception as manual_error:
                    print(f"Manual method also failed for downloads: {manual_error}")
                    return jsonify({'error': f"Could not send downloads file: {str(manual_error)}"}), 500
    
    except Exception as e:
        print(f"Error during downloads export for {file_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f"Downloads export error: {str(e)}"}), 500
    
@download_bp.route('/api/export', methods=['POST'])
def export_data():
    """
    Unified export API for browser history data
    """
    try:
        # Get request data
        request_data = request.get_json()
        
        if not request_data:
            return jsonify({'error': 'No data provided'}), 400
            
        # Extract parameters
        file_id = request_data.get('file_id')
        export_format = request_data.get('format', 'csv').lower()
        data_type = request_data.get('data_type', 'history').lower()
        filters = request_data.get('filters', {})
        
        if not file_id:
            return jsonify({'error': 'File ID is required'}), 400
            
        # Validate file exists
        file_id_str = str(file_id)
        if not file_exists(file_id_str):
            temp_path = get_temp_file_path(file_id_str)
            
            if not os.path.exists(temp_path):
                return jsonify({'error': f"Invalid file ID: {file_id}"}), 400
            
            # Try to re-process the file
            try:
                print(f"File found on disk but not in memory, attempting to re-process: {temp_path}")
                browser_type = detect_browser_type(temp_path)
                process_history_file(temp_path, browser_type, file_id_str, 1, Config.DEFAULT_PAGE_SIZE)
                
                if not file_exists(file_id_str):
                    return jsonify({'error': 'Failed to re-process file'}), 500
            except Exception as e:
                print(f"Error re-processing file: {e}")
                return jsonify({'error': f"Error re-processing file: {str(e)}"}), 500
        
        # Get data from storage
        processed_data = get_processed_data(file_id_str)
        
        if not processed_data:
            return jsonify({'error': 'No data available for export'}), 404
        
        # Extract the specific data type requested
        if data_type == 'history':
            export_items = processed_data.get('history', [])
            filename = f'browser_history_{file_id}'
            fields = ['url', 'title', 'visit_time', 'visit_count', 'last_visit_time', 'domain']
        elif data_type == 'domains':
            export_items = processed_data.get('domains', [])
            filename = f'browser_domains_{file_id}'
            fields = ['domain', 'visit_count', 'last_visit_time', 'frequency']
        elif data_type == 'downloads':
            export_items = processed_data.get('downloads', [])
            filename = f'browser_downloads_{file_id}'
            fields = ['filename', 'url', 'referrer', 'download_time', 'file_size', 'mime_type', 'status']
        elif data_type == 'timeline':
            export_items = processed_data.get('timeline', [])
            filename = f'browser_timeline_{file_id}'
            fields = ['date', 'visit_count', 'unique_urls', 'unique_domains']
        else:
            return jsonify({'error': f'Unsupported data type: {data_type}'}), 400
        
        # Check if we have data to export
        if not export_items:
            return jsonify({'error': f'No {data_type} data available for export'}), 404
        
        # Export based on format
        if export_format == 'csv':
            return export_as_csv(export_items, filename, fields)
        elif export_format == 'json':
            return export_as_json(export_items, filename)
        elif export_format == 'excel':
            # Need to check if pandas is installed
            try:
                import pandas as pd
                return export_as_excel(export_items, filename, fields)
            except ImportError:
                # Fallback to CSV if pandas not available
                print("Warning: pandas not installed, falling back to CSV export")
                return export_as_csv(export_items, filename, fields)
        else:
            return jsonify({'error': f'Unsupported export format: {export_format}'}), 400
            
    except Exception as e:
        print(f"Error during export: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f"Export error: {str(e)}"}), 500
    
def export_as_csv(data, filename, fields=None):
    """Export data as CSV file using StringIO"""
    from io import StringIO
    import csv
    
    try:
        # Create CSV in memory
        output = StringIO()
        
        # Determine fields if not provided
        if not fields and data:
            if isinstance(data[0], dict):
                fields = data[0].keys()
            else:
                # Try to get attributes if not a dict
                fields = vars(data[0]).keys() if hasattr(data[0], '__dict__') else None
        
        if not fields:
            return jsonify({'error': 'Could not determine fields for CSV export'}), 500
        
        writer = csv.DictWriter(output, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        
        # Write data
        for item in data:
            if isinstance(item, dict):
                # Filter to only include fields in fieldnames
                row = {k: v for k, v in item.items() if k in fields}
                writer.writerow(row)
            else:
                # Convert object to dict
                obj_dict = vars(item) if hasattr(item, '__dict__') else {}
                row = {k: v for k, v in obj_dict.items() if k in fields}
                writer.writerow(row)
        
        # Get the CSV content
        csv_content = output.getvalue()
        
        # Create a response
        response = Response(
            csv_content,
            mimetype='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename={filename}.csv'
            }
        )
        
        return response
    except Exception as e:
        print(f"CSV export error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

    """Export data as JSON file"""
    try:
        # Convert data to serializable format
        serializable_data = []
        
        for item in data:
            if isinstance(item, dict):
                serializable_data.append(item)
            else:
                # Convert object to dict
                obj_dict = vars(item) if hasattr(item, '__dict__') else {}
                serializable_data.append(obj_dict)
        
        # Create a custom encoder for dates
        class DateTimeEncoder(json.JSONEncoder):
            def default(self, obj):
                from datetime import datetime, date
                if isinstance(obj, (datetime, date)):
                    return obj.isoformat()
                return super().default(obj)
        
        # Convert to JSON
        json_data = json.dumps(serializable_data, cls=DateTimeEncoder, indent=2)
        
        # Create response
        response = Response(
            json_data,
            mimetype='application/json',
            headers={
                'Content-Disposition': f'attachment; filename={filename}.json'
            }
        )
        
        return response
    except Exception as e:
        print(f"JSON export error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

