import os
import subprocess
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename

from vision.Query_Praśna import QueryPraśna
from vision.OCR_Lipi import OCRLipi  
from vision.Layout_Vyavastha import LayoutVyavastha  
from vision.Table_Kostaka import TableKostaka 
from vision.Form_Jnaiskasa import FormJnaiskasa 
from vision.Signature_Hastaakshara import SignatureHastaakshara
from vision.pdfa_converter import convert_to_pdfa

app = Flask(__name__)
cors = CORS(app, resources={r"/api/upload": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'

SAVE_FOLDER = 'data/output_ocr_dir'
UPLOAD_FOLDER = 'data/uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/upload', methods=['POST'])
@cross_origin()
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    tab = request.form.get('tab', 'Raw-text')
    file = request.files['file']
    model_name = request.form.get('model_name', 'RAGFLOW')
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        # Secure and construct file path
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        name, _ = os.path.splitext(filename)
        output_filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{name}.pdf")
        convert_to_pdfa(filepath, output_filepath)
        print(model_name)

        if tab == 'Raw-text':
            lz = OCRLipi()
            raw_text, labeled_images = lz(output_filepath, model_name, SAVE_FOLDER)
            if os.path.exists(filepath):
                os.remove(filepath)
            if os.path.exists(output_filepath):
                os.remove(output_filepath)
            return jsonify({
                'rawText': raw_text,
                'labeledImages': labeled_images
            })
        elif tab == 'Layout':
            lb = LayoutVyavastha("layout")
            layout_data, labeled_images = lb(
                output_filepath,
                model_name,
                **({"threshold": 0.005} if model_name == "RAGFLOW" else {}),
                output_path=SAVE_FOLDER
            )
            if os.path.exists(filepath):
                os.remove(filepath)
            if os.path.exists(output_filepath):
                os.remove(output_filepath)
            return jsonify({
                'layoutData': layout_data,
                'labeledImages': labeled_images
            })
        elif tab == 'Tables':
            tk = TableKostaka()
            table_html = tk(
                output_filepath,
                model_name,
                **({"threshold": 0.2} if model_name == "RAGFLOW" else {})
            )
            if os.path.exists(filepath):
                os.remove(filepath)
            if os.path.exists(output_filepath):
                os.remove(output_filepath)
            return jsonify({
                'tableHtml': table_html
            })
        elif tab == 'Forms':
            fj = FormJnaiskasa()
            key_val, labeled_images = fj(output_filepath, model_name, SAVE_FOLDER)
            if os.path.exists(filepath):
                os.remove(filepath)
            if os.path.exists(output_filepath):
                os.remove(output_filepath)

            print(key_val)
            return jsonify({
                    'formData': key_val,
                    'labeledImages': labeled_images
                })
        elif tab == 'Queries':
            query = request.form.get('query', '')
            if query:
                lb = LayoutVyavastha("layout")
                layout_data = lb(
                    output_filepath,
                    model_name,
                    **({"threshold": 0.005} if model_name == "RAGFLOW" else {})
                )
                layout_rag = QueryPraśna(layout_data)
                res = layout_rag(query)
                if os.path.exists(filepath):
                    os.remove(filepath)
                if os.path.exists(output_filepath):
                    os.remove(output_filepath)
                return jsonify({
                    'ragResponse': res
                })
        elif tab == 'Signatures':
            SH = SignatureHastaakshara()
            sig, labeled_images = SH(output_filepath, model_name, SAVE_FOLDER)
            if os.path.exists(filepath):
                os.remove(filepath)
            if os.path.exists(output_filepath):
                os.remove(output_filepath)
            return jsonify({
                    'signature': [sig],
                    'labeledImages': labeled_images
                })

    return jsonify({'error': 'Invalid file type'}), 400

# After each request, add the CORS headers explicitly
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, X-Requested-With, Authorization"
    return response

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(host='0.0.0.0', port=7001, debug=True)
