from flask import Flask, render_template, request, jsonify, url_for
import json
import os
from werkzeug.utils import secure_filename
from vision.layout_bodh_zila import layout_bodh, layout_zila

app = Flask(__name__)

# Configuration
op_dir = "layout_ouputs/images_samp"
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'})
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'})
        if file and allowed_file(file.filename):
            # Process the file here
            results = process_file(file)
            return jsonify(results)
    return render_template('index.html')

def process_file(filepath):
    layout_results = layout_bodh(True, filepath, op_dir, 0.005)

    with open(os.path.join('/home/zok/joker/vinyAsa_main/vinyAsa/layout_ouputs/json_samp','viny_.json'), 'w') as file:
        json_output = json.dump(layout_results, file, indent=2)
    with open(os.path.join('/home/zok/joker/vinyAsa_main/vinyAsa/layout_ouputs/json_samp','viny_.json'), 'r') as f:
        return json.load(f)

@app.route('/sample_document')
def sample_document():
    return jsonify({'message': 'Sample document loaded'})

if __name__ == '__main__':
    app.run(debug=True)