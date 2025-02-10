from flask import Flask, request, send_from_directory, jsonify
import subprocess, os, uuid
from flask_cors import CORS  # For handling cross-domain requests

app = Flask(__name__)
# Allow CORS from your converter web app domain (adjust the URL as needed)
CORS(app, resources={r"/convert": {"origins": "https://your-fileconverter-domain.com"}})

@app.route('/convert', methods=['POST'])
def convert():
    # Ensure the file is in the request
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    target_format = request.form.get('target_format')  # e.g., "pdf", "odt", etc.
    if not target_format:
        return jsonify({'error': 'No target format provided'}), 400

    # Save the uploaded file to a temporary directory
    input_filename = os.path.join('/tmp', str(uuid.uuid4()) + "_" + file.filename)
    file.save(input_filename)

    # Use /tmp as the output directory (this directory is writable)
    output_dir = '/tmp'
    # Build the LibreOffice conversion command
    cmd = ['soffice', '--headless', '--convert-to', target_format, input_filename, '--outdir', output_dir]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    if result.returncode != 0:
        return jsonify({'error': 'Conversion failed', 'details': result.stderr.decode()}), 500

    # LibreOffice outputs a file with the same basename
    base, _ = os.path.splitext(os.path.basename(input_filename))
    output_file = os.path.join(output_dir, base + '.' + target_format)
    if not os.path.exists(output_file):
        return jsonify({'error': 'Output file not found'}), 500

    return send_from_directory(directory=output_dir, path=os.path.basename(output_file), as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
