import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

from vision.praśna import QueryPraśna
from vision.lipi import OCRLipi  
from vision.vyavastha import LayoutVyavastha  
from vision.kostaka import TableKostaka  

app = Flask(__name__)
CORS(app) 

UPLOAD_FOLDER = 'data/uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    tab = request.form.get('tab', 'Raw-text')
    file = request.files['file']
    model_name = request.form.get('model_name', 'RAGFLOW')
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        print(model_name)
        if tab == 'Raw-text':
            lz = OCRLipi()
            raw_text, labeled_images = lz(filepath, model_name, "data/output_ocr_dir")
            # print(raw_text)
            # paginated_raw_text = paginate_data(raw_text)
            return jsonify({
                'rawText': raw_text,
                'labeledImages': labeled_images
            })
        elif tab == 'Layout':
            lb = LayoutVyavastha("layout")
            layout_data, labeled_images = lb(filepath, model_name, **({"threshold": 0.005} if model_name == "RAGFLOW" else {}), output_path="data/output_layout_dir")
            # print(layout_data)
            # paginated_layout_text = paginate_data(layout_data)
            return jsonify({
                'layoutData': layout_data,
                'labeledImages': labeled_images
            })
        elif tab == 'Tables':
            tk = TableKostaka()
            table_html = tk(filepath, model_name, **({"threshold": 0.2} if model_name == "RAGFLOW" else {}))
            print(table_html)
            return jsonify({
                'tableHtml': table_html
            })
        elif tab == 'Queries':
            query = request.form.get('query', '')
            if query:
                lb = LayoutVyavastha("layout")
                layout_data = lb(filepath, model_name, **({"threshold": 0.005} if model_name == "RAGFLOW" else {}))
                layout_rag = QueryPraśna(layout_data)
                res = layout_rag(query)
                return jsonify({
                    'ragResponse': res
                })
            
    return jsonify({'error': 'Invalid file type'}), 400

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(port=8000, debug=True)