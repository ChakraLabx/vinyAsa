from flask import Flask, request, jsonify
from vision.layout_bodh_zila import layout_bodh, layout_zila
import os

app = Flask(__name__)

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)
        
        # Process the file using AI code
        raw_text = layout_zila(filename)
        layout_data = layout_bodh(True, filename, 'output_dir', 0.005)
        
        return jsonify({
            'rawText': raw_text,
            'layoutData': layout_data
        })
    
    return jsonify({'error': 'Invalid file type'}), 400