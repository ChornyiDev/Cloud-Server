from flask import Flask, request, send_file, jsonify, url_for
from dotenv import load_dotenv
import os
from datetime import datetime
import uuid
import mimetypes
import requests
from urllib.parse import urlparse

# Load environment variables
load_dotenv()
BASE_URL = os.getenv('BASE_URL', 'https://storage.magicboxpremium.com')
HOST_URL = os.getenv('HOST_URL', 'https://storage.magicboxpremium.com')

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def generate_unique_filename(original_filename):
    name, ext = os.path.splitext(original_filename)
    unique_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
    return f"{name}_{unique_id}{ext}"

def download_file_from_url(url):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Get filename from URL or Content-Disposition header
        content_disposition = response.headers.get('Content-Disposition')
        if content_disposition and 'filename=' in content_disposition:
            filename = content_disposition.split('filename=')[1].strip('"')
        else:
            filename = os.path.basename(urlparse(url).path)
            if not filename:
                filename = 'downloaded_file'
        
        # Get file extension from Content-Type if filename doesn't have one
        if not os.path.splitext(filename)[1]:
            content_type = response.headers.get('Content-Type', '').split(';')[0]
            ext = mimetypes.guess_extension(content_type)
            if ext:
                filename += ext
        
        return response.content, filename
    except requests.RequestException as e:
        return None, str(e)

@app.route('/upload', methods=['POST'])
def upload_file():
    file_url = request.form.get('file_url')
    
    if file_url:
        # Try to download file from URL
        content, filename = download_file_from_url(file_url)
        if content is None:
            return jsonify({'error': f'Failed to download file from URL: {filename}'}), 400
        
        unique_filename = generate_unique_filename(filename)
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        with open(file_path, 'wb') as f:
            f.write(content)
    else:
        # Handle regular file upload
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        filename = file.filename
        unique_filename = generate_unique_filename(filename)
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(file_path)
    
    base_url = BASE_URL.rstrip('/')
    download_url = f"{base_url}{url_for('download_file', filename=unique_filename)}"
    preview_url = f"{base_url}{url_for('preview_file', filename=unique_filename)}"
    host_url = f"{HOST_URL}/uploads/{unique_filename}"
    
    # Get file size in bytes
    file_size = os.path.getsize(file_path)
    
    return jsonify({
        'message': 'File uploaded successfully',
        'original_filename': filename,
        'stored_filename': unique_filename,
        'download_url': download_url,
        'preview_url': preview_url,
        'host_url': host_url,
        'file_size': file_size
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
        
        # Перевіряємо, чи це зображення, відео або аудіо файл
        if mime_type and (
            mime_type.startswith('video/') or 
            mime_type.startswith('audio/') or 
            mime_type.startswith('image/')
        ):
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
    app.run(debug=True, host='0.0.0.0', port=5005) 