from flask import Flask, request, send_file, jsonify, url_for
from dotenv import load_dotenv
import os
from datetime import datetime
import uuid
import mimetypes

# Load environment variables
load_dotenv()
BASE_URL = os.getenv('BASE_URL', 'http://localhost:5000')

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def generate_unique_filename(original_filename):
    name, ext = os.path.splitext(original_filename)
    unique_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
    return f"{name}_{unique_id}{ext}"

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    original_filename = file.filename
    unique_filename = generate_unique_filename(original_filename)
    
    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
    file.save(file_path)
    
    base_url = BASE_URL.rstrip('/')
    download_url = f"{base_url}{url_for('download_file', filename=unique_filename)}"
    preview_url = f"{base_url}{url_for('preview_file', filename=unique_filename)}"
    
    return jsonify({
        'message': 'File uploaded successfully',
        'original_filename': original_filename,
        'stored_filename': unique_filename,
        'download_url': download_url,
        'preview_url': preview_url
    }), 200

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    try:
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        return send_file(file_path, as_attachment=True)
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404

@app.route('/preview/<filename>', methods=['GET'])
def preview_file(filename):
    try:
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        mime_type, _ = mimetypes.guess_type(filename)
        
        # Перевіряємо, чи це відео або аудіо файл
        if mime_type and (mime_type.startswith('video/') or mime_type.startswith('audio/')):
            return send_file(
                file_path,
                mimetype=mime_type,
                as_attachment=False,
                download_name=filename
            )
        else:
            return jsonify({'error': 'File type not supported for preview'}), 400
            
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 