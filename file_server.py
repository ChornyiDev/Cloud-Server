from flask import Flask, request, send_file, jsonify, url_for
import os
from datetime import datetime
import uuid

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def generate_unique_filename(original_filename):
    # Split filename into name and extension
    name, ext = os.path.splitext(original_filename)
    # Generate unique identifier using timestamp and UUID
    unique_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
    # Combine everything into a new filename
    return f"{name}_{unique_id}{ext}"

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Generate unique filename
    original_filename = file.filename
    unique_filename = generate_unique_filename(original_filename)
    
    # Save the file with unique name
    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
    file.save(file_path)
    
    # Generate download URL
    download_url = request.host_url.rstrip('/') + url_for('download_file', filename=unique_filename)
    
    return jsonify({
        'message': 'File uploaded successfully',
        'original_filename': original_filename,
        'stored_filename': unique_filename,
        'download_url': download_url
    }), 200

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    try:
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        return send_file(file_path, as_attachment=True)
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000) 