from flask import Flask, request, send_from_directory, render_template_string, send_file
import os, zipfile

app = Flask(__name__)

# Directory where uploaded files will be stored
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# HTML template for file upload & listing
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>File Server</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; margin: 20px; }
        h1, h2 { color: #333; }
        form { margin-bottom: 20px; }
        ul { list-style-type: none; padding: 0; }
        li { margin: 5px 0; }
        a { text-decoration: none; color: blue; }
        button { background-color: #4CAF50; color: white; padding: 10px; border: none; cursor: pointer; }
        button:hover { background-color: #45a049; }
    </style>
</head>
<body>
    <h1>Upload Files</h1>
    <form action="/upload" method="post" enctype="multipart/form-data">
        <input type="file" name="files" multiple required>
        <button type="submit">Upload</button>
    </form>
    
    <h2>Available Files:</h2>
    <form action="/download_selected" method="post">
        <ul>
            {% for file in files %}
                <li>
                    <input type="checkbox" name="selected_files" value="{{ file }}"> 
                    <a href="/download/{{ file }}">{{ file }}</a>
                </li>
            {% endfor %}
        </ul>
        <button type="submit">Download Selected</button>
    </form>
    <br>
    <a href="/download_all"><button>Download All</button></a>
</body>
</html>
"""

@app.route("/")
def index():
    """Render the main page with file list."""
    files = os.listdir(UPLOAD_FOLDER)
    return render_template_string(HTML_TEMPLATE, files=files)

@app.route("/upload", methods=["POST"])
def upload_file():
    """Handles multiple file uploads."""
    if "files" not in request.files:
        return "No files provided", 400
    
    files = request.files.getlist("files")
    if not files or all(file.filename == "" for file in files):
        return "No selected files", 400
    
    for file in files:
        if file.filename:
            file.save(os.path.join(UPLOAD_FOLDER, file.filename))
    
    return "Files uploaded successfully!"

@app.route("/download/<filename>")
def download_file(filename):
    """Serve files for download."""
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

@app.route("/download_all")
def download_all():
    """Creates and serves a zip of all files."""
    zip_path = os.path.join(UPLOAD_FOLDER, "all_files.zip")
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for file in os.listdir(UPLOAD_FOLDER):
            if file != "all_files.zip":
                zipf.write(os.path.join(UPLOAD_FOLDER, file), file)
    return send_file(zip_path, as_attachment=True)

@app.route("/download_selected", methods=["POST"])
def download_selected():
    """Creates and serves a zip of selected files."""
    selected_files = request.form.getlist("selected_files")
    if not selected_files:
        return "No files selected", 400
    
    zip_path = os.path.join(UPLOAD_FOLDER, "selected_files.zip")
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for file in selected_files:
            zipf.write(os.path.join(UPLOAD_FOLDER, file), file)
    
    return send_file(zip_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001)
