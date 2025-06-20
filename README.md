# Browser History Analyzer

A Flask-based web application for analyzing and visualizing browser history data from Chrome and Firefox browsers. This tool allows you to upload browser history files and provides detailed insights through interactive dashboards.

## Features

- **Multi-Browser Support**: Analyze history from Chrome and Firefox browsers
- **Interactive Dashboard**: View history data through multiple panels:
  - Timeline view with pagination
  - Downloads analysis
  - Domain statistics
  - Sync data visualization
- **Data Export**: Export analyzed data
- **Real-time Processing**: Upload and analyze history files instantly

## Project Structure

```
browser_history_analyzer/
├── app.py                      # Main Flask application
├── config.py                   # Configuration settings
├── models/                     # Data models
│   ├── __init__.py
│   └── data_models.py
├── routes/                     # Flask route blueprints
│   ├── __init__.py
│   ├── main_routes.py         # Main upload and processing routes
│   ├── history_routes.py      # History data API routes
│   ├── download_routes.py     # Data export routes
│   └── sync_routes.py         # Sync data routes
├── services/                   # Core processing services
│   ├── __init__.py
│   ├── chrome_processor.py    # Chrome history processing
│   ├── firefox_processor.py   # Firefox history processing
│   ├── history_processor.py   # Main processor coordinator
│   ├── common_utils.py        # Shared utilities
│   └── storage.py             # Data storage management
├── utils/                      # Utility modules
│   ├── __init__.py
│   ├── file_utils.py          # File handling utilities
│   ├── time_utils.py          # Time/date utilities
│   └── url_utils.py           # URL processing utilities
├── static/                     # Static web assets
│   ├── css/                   # Stylesheets
│   └── js/                    # JavaScript files
├── templates/                  # HTML templates
│   ├── layout/                # Base templates
│   ├── components/            # Reusable components
│   └── panels/                # Dashboard panels
└── temp_uploads/              # Temporary file storage (auto-created)
```

## Requirements

### Python Dependencies

The application requires the following Python packages:

- **Flask** - Web framework
- **pandas** - Data analysis and manipulation
- **sqlite3** - Database operations (built-in with Python)
- **os, json, re** - Standard library modules

### System Requirements

- Python 3.7 or higher
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Minimum 512MB RAM
- 100MB free disk space

## Installation

### 1. Clone or Download the Project

```bash
# If using git
git clone <repository-url>
cd browser_history_analyzer

# Or download and extract the ZIP file
```

### 2. Set Up Python Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install flask pandas
```

### 4. Verify Installation

Check that all required files are present:
- `app.py` (main application file)
- `config.py` (configuration)
- All folders: `models/`, `routes/`, `services/`, `utils/`, `static/`, `templates/`

## Configuration

### Environment Variables (Optional)

You can customize the application behavior using environment variables:

```bash
# Flask settings
export FLASK_DEBUG=True          # Enable debug mode (default: True)
export FLASK_HOST=0.0.0.0        # Host address (default: 0.0.0.0)
export FLASK_PORT=5002           # Port number (default: 5002)
```

### Default Configuration

If no environment variables are set, the application uses these defaults:
- **Debug Mode**: Enabled
- **Host**: 0.0.0.0 (accessible from any network interface)
- **Port**: 5002
- **Upload Folder**: `temp_uploads/` (auto-created)
- **Page Size**: 1000 records per page

## Usage

### 1. Start the Application

```bash
python app.py
```

You should see output similar to:
```
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5002
 * Running on http://[your-ip]:5002
```

### 2. Access the Web Interface

Open your web browser and navigate to:
- **Local access**: http://localhost:5002
- **Network access**: http://[your-ip-address]:5002

### 3. Upload Browser History Files

#### For Chrome:
1. Close Chrome completely
2. Navigate to Chrome's user data directory:
   - **Windows**: `C:\Users\[username]\AppData\Local\Google\Chrome\User Data\Default\`
   - **macOS**: `~/Library/Application Support/Google/Chrome/Default/`
   - **Linux**: `~/.config/google-chrome/Default/`
3. Copy the `History` file (no extension)
4. Upload this file through the web interface

#### For Firefox:
1. Close Firefox completely
2. Navigate to Firefox's profile directory:
   - **Windows**: `C:\Users\[username]\AppData\Roaming\Mozilla\Firefox\Profiles\[profile-name]\`
   - **macOS**: `~/Library/Application Support/Firefox/Profiles/[profile-name]/`
   - **Linux**: `~/.mozilla/firefox/[profile-name]/`
3. Copy the `places.sqlite` file
4. Upload this file through the web interface

### 4. Analyze Your Data

Once uploaded, the application will process your history file and display:

- **Timeline Panel**: Chronological view of browsing history with search and pagination
- **Downloads Panel**: Analysis of downloaded files and their sources
- **Domains Panel**: Statistics showing most visited domains and time spent
- **Sync Panel**: Synchronization data and cross-device activity

### 5. Export Data

Use the export functionality to download your analyzed data in various formats:
- CSV files for spreadsheet analysis
- JSON for programmatic access
- Filtered exports based on date ranges or domains

## API Endpoints

The application provides several API endpoints for programmatic access:

- `POST /upload` - Upload and process history files
- `GET /history/<file_id>` - Retrieve processed history data
- `GET /downloads/<file_id>` - Get download history
- `GET /domains/<file_id>` - Get domain statistics
- `GET /sync/<file_id>` - Get sync data
- `GET /export/<file_id>` - Export data in various formats

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```
   Error: [Errno 48] Address already in use
   ```
   Solution: Change the port in `config.py` or set `FLASK_PORT` environment variable

2. **File Upload Errors**
   - Ensure the browser is completely closed before copying history files
   - Check file permissions and ensure the file isn't locked
   - Verify you're uploading the correct history file format

3. **Database Locked Errors**
   - Make sure the browser is completely closed
   - Try copying the history file to a different location first

4. **Memory Issues with Large Files**
   - Large history files may require more RAM
   - Consider reducing the page size in configuration

### Debug Mode

Enable debug mode for detailed error information:
```bash
export FLASK_DEBUG=True
python app.py
```

### Logs

Check the console output for detailed processing information and error messages.

## Security Notes

- **Local Use Only**: This application is designed for local analysis of your own browser history
- **Temporary Files**: Uploaded files are stored temporarily and should be cleaned periodically
- **Data Privacy**: No data is sent to external servers; all processing happens locally
- **File Access**: Ensure proper file permissions when accessing browser history files

## Browser Compatibility

### Supported Browsers for History Analysis:
- Google Chrome (all versions)
- Mozilla Firefox (all versions)
- Chromium-based browsers (Edge, Brave, Opera, etc.)

### Supported Browsers for Web Interface:
- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

## Performance Tips

- **Large Files**: For history files larger than 100MB, processing may take several minutes
- **Pagination**: Use smaller page sizes (500-1000) for better performance with large datasets
- **Memory**: Close other applications if processing very large history files
- **Storage**: Regularly clean the `temp_uploads/` directory

## Development

### Running in Development Mode

```bash
export FLASK_DEBUG=True
python app.py
```

### File Structure for Development

- Modify templates in `templates/` for UI changes
- Update styles in `static/css/`
- Add JavaScript functionality in `static/js/`
- Extend processing logic in `services/`
- Add new routes in `routes/`

## License

This project is for educational and personal use. Please respect browser data privacy and only analyze your own browsing history.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review console logs for error details
3. Ensure all dependencies are properly installed
4. Verify browser history file formats and accessibility

---

**Note**: This application processes sensitive browsing data. Always ensure you have proper authorization before analyzing any browser history files, and use this tool responsibly and in compliance with applicable privacy laws.
