# Flask File Upload and Download API

This project is a simple Flask-based API that allows users to upload files to a server and download them using generated unique URLs. It features endpoint routes for file upload and file download, and generates unique filenames to avoid collisions.

## Features
- **File Upload**: Upload files to the server, which are saved with a unique filename to avoid collisions.
- **File Download**: Download uploaded files using a generated download URL.

## Prerequisites
- Python 3.x
- Flask (`pip install Flask`)
- Gunicorn (`pip install gunicorn`)

## Getting Started

### Installation
1. **Clone the repository**:
   ```sh
   git clone https://github.com/ChornyiDev/Cloud-Server.git
   ```

2. **Navigate to the project directory**:
   ```sh
   cd Cloud-Server
   ```

3. **Set Up a Virtual Environment**:
   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Install dependencies**:
   ```sh
   pip install -r requirements.txt
   ```

### Running the App

#### Development Mode
To run the Flask application locally:
1. Make sure you're in the project directory.
2. Run the Flask application:
   ```sh
   python file_server.py
   ```
3. The server will start on `http://localhost:5000` by default.

#### Production Mode
To run the application in production mode using Gunicorn:
1. Make sure you're in the project directory and your virtual environment is activated.
2. Run the application with Gunicorn:
   ```sh
   gunicorn -b 0.0.0.0:5000 file_server:app
   ```
3. The server will be accessible from any IP address on port 5000.

### Running as a System Service

To run the Flask app as a system service, follow these steps:

1. **Create a service file**:
   ```sh
   sudo nano /etc/systemd/system/file_server.service
   ```

   Add the following content to the file:
   ```ini
   [Unit]
   Description=Flask File Upload and Download API
   After=network.target

   [Service]
   User=<your-username>
   WorkingDirectory=/path/to/Cloud-Server
   Environment="PATH=/path/to/Cloud-Server/venv/bin"
   ExecStart=/path/to/Cloud-Server/venv/bin/gunicorn -b 0.0.0.0:5000 file_server:app

   [Install]
   WantedBy=multi-user.target
   ```

   Replace `<your-username>` and `/path/to/Cloud-Server` with your actual username and project path.

2. **Reload systemd** to recognize the new service:
   ```sh
   sudo systemctl daemon-reload
   ```

3. **Start the service**:
   ```sh
   sudo systemctl start file_server
   ```

4. **Enable the service** to start on boot:
   ```sh
   sudo systemctl enable file_server
   ```

### API Endpoints

#### 1. Upload File
- **URL**: `/upload`
- **Method**: `POST`
- **Description**: Uploads a file to the server, and saves it with a unique filename.
- **Request Body**: The request should include a file under the `file` key (using `multipart/form-data`).
- **Response**: A JSON object containing the original filename, stored filename, and a URL to download the file.

  **Example Request** (using `curl`):
  ```sh
  curl -F "file=@yourfile.txt" http://localhost:5000/upload
  ```

  **Example Response**:
  ```json
  {
    "message": "File uploaded successfully",
    "original_filename": "yourfile.txt",
    "stored_filename": "yourfile_20231115_123456_abc12345.txt",
    "download_url": "http://localhost:5000/download/yourfile_20231115_123456_abc12345.txt"
  }
  ```

#### 2. Download File
- **URL**: `/download/<filename>`
- **Method**: `GET`
- **Description**: Downloads the specified file from the server.
- **Response**: The requested file will be sent as an attachment.

  **Example Request** (using `curl`):
  ```sh
  curl -O http://127.0.0.1:5000/download/yourfile_20231115_123456_abc12345.txt
  ```

### Directory Structure
```
<project-directory>/
  ├── app.py           # Main Flask application
  ├── uploads/         # Directory where uploaded files are stored
  └── README.md        # Documentation (this file)
```

### Notes
- All uploaded files are saved in the `uploads` folder.
- Filenames are saved with unique identifiers to avoid name collisions.
- This script runs on port `5000` by default, but you can change it in the `app.run()` function.

### Error Handling
- If the `file` key is not present in the request, the server will respond with `400 Bad Request` and an error message.
- If a requested file does not exist, the server will respond with `404 Not Found`.

### Security Considerations
When running the server with public access, consider implementing:
- SSL/TLS encryption (HTTPS)
- Authentication system
- Rate limiting
- File size restrictions
- Allowed file types validation

### Accessing the Server
- Local access: `http://localhost:5000`
- Public access: `http://<your-server-ip>:5000`
- If using a domain: `http://<your-domain>:5000`

### Troubleshooting
- Make sure port 5000 is open in your firewall
- Check server logs using: `sudo journalctl -u file_server`
- Verify the service status: `sudo systemctl status file_server`
