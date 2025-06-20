from flask import Flask, send_from_directory
import os
from config import Config
from routes.main_routes import main_bp
from routes.history_routes import history_bp
from routes.download_routes import download_bp
from routes.sync_routes import sync_bp
from utils.file_utils import ensure_upload_directory

app = Flask(__name__,
            static_folder='static',
            template_folder='templates')
app.config.from_object(Config)

# Create upload folder if it doesn't exist
ensure_upload_directory()

# Register blueprints
app.register_blueprint(main_bp)
app.register_blueprint(history_bp)
app.register_blueprint(download_bp)
app.register_blueprint(sync_bp,)

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'], host=app.config['HOST'], port=app.config['PORT'])