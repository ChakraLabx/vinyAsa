import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from vision.layout_bodh_zila import layout_zila, layout_bodh

app = Flask(__name__)
CORS(app) 

UPLOAD_FOLDER = 'data/uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def paginate_ocr_data(raw_text):
    # Group OCR data by page number
    paginated_data = {}
    for page_no, item in enumerate(raw_text, start=1):
        if page_no not in paginated_data:
            paginated_data[page_no] = []
        paginated_data[page_no].append(item)
    
    return paginated_data

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    tab = request.form['tab']
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        if tab == 'Raw-text':
            lz = layout_zila()
            raw_text, labeled_images = lz(filepath, output_path="data/output_ocr_dir")
            paginated_raw_text = paginate_ocr_data(raw_text)
            return jsonify({
                'rawText': paginated_raw_text,
                'labeledImages': labeled_images
            })
        elif tab == 'Layout':
            lb = layout_bodh("layout")
            layout_data, labeled_images = lb(filepath, output_path="data/output_layout_dir",threshold=0.005)
            return jsonify({
                'layoutData': layout_data,
                'labeledImages': labeled_images
            })
        
    return jsonify({'error': 'Invalid file type'}), 400

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)