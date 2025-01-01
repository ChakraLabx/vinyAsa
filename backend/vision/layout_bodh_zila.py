import json
import os
import io
import base64
import numpy as np
from PIL import Image
from copy import deepcopy

import easyocr
import pytesseract
from paddleocr import PaddleOCR
from mmocr.apis import MMOCRInferencer
from rapidocr_onnxruntime import RapidOCR

from surya.ocr import run_ocr
from surya.model.detection.model import load_model as load_det_model, load_processor as load_det_processor
from surya.model.recognition.model import load_model as load_rec_model
from surya.model.recognition.processor import load_processor as load_rec_processor

from vision.seeit import draw_box
from vision.ocr import OCR
from vision.layout_recognizer import LayoutRecognizer
from vision.recognizer import Recognizer
from vision.file_utils import get_project_base_directory
from vision.in_out import init_in_out

class layout_zila(OCR):
    def __init__(self):
        try:
            model_dir = os.path.join(
                    get_project_base_directory(),
                    "deepdoc")
            super().__init__(model_dir)
        except Exception as e:
            model_dir = snapshot_download(repo_id="InfiniFlow/deepdoc",
                                          local_dir=os.path.join(get_project_base_directory(), "deepdoc"),
                                          local_dir_use_symlinks=False)

            super().__init__(model_dir)

    def ragflow_to_bxs(self, images_path, output_path=None):
        images, outputs = init_in_out(images_path, output_path)

        img_list = []
        bxs_list = []
        for i, img in enumerate(images):
            bxs = super().__call__(np.array(img))
            bxs = [(line[0], line[1][0]) for line in bxs]
            bxs = [{
                "text": t,
                "x0": b[0][0],
                "x1": b[1][0],
                "top": b[0][1],
                "bottom": b[-1][1],
                "type": "ocr",
                "score": 1} for b, t in bxs if b[0][0] <= b[1][0] and b[0][1] <= b[-1][1]]

            img_with_boxes = draw_box(images[i], bxs, ["ocr"], 1.)
            if outputs:
                img_with_boxes.save(outputs[i], quality=95)
            
            # Instead of saving, convert to base64
            buffered = io.BytesIO()
            img_with_boxes.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            img_list.append(img_str)
            bxs_list.append(bxs)

        return bxs_list, img_list

    def pytesseract_to_bxs(self, images_path, output_path=None):
        images, outputs = init_in_out(images_path, output_path)
        img_list = []
        bxs_list = []
        
        for i, img in enumerate(images):
            bxs = pytesseract.image_to_data(np.array(img), output_type=pytesseract.Output.DICT)
        
            bxs_filtered = [{
                "text": bxs['text'][j],
                "x0": bxs['left'][j],
                "x1": bxs['left'][j] + bxs['width'][j],
                "top": bxs['top'][j],
                "bottom": bxs['top'][j] + bxs['height'][j],
                "type": "ocr",
                "score": int(bxs['conf'][j]) / 100 
            } for j in range(len(bxs['text'])) 
            if bxs['text'][j].strip() and int(bxs['conf'][j]) > 60]
            
            img_with_boxes = draw_box(images[i], bxs_filtered, ["ocr"], 1.)
            
            if outputs:
                img_with_boxes.save(outputs[i], quality=95)
            
            # Convert to base64
            buffered = io.BytesIO()
            img_with_boxes.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            img_list.append(img_str)
            
            bxs_list.append(bxs_filtered)
        
        return bxs_list, img_list

    def paddleocr_to_bxs(self, images_path, output_path=None):
        images, outputs = init_in_out(images_path, output_path)

        bxs_list = []
        img_list = []
        for i, img in enumerate(images):
            ocr = PaddleOCR(use_angle_cls=True, lang='en')
            result = ocr.ocr(np.array(img), cls=True)

            bxs = [{
                "text": line[1][0], 
                "x0": line[0][0][0], 
                "x1": line[0][2][0],  
                "top": line[0][0][1],  
                "bottom": line[0][2][1],  
                "type": "ocr",
                "score": line[1][1]  
            } for line in result[0] if line[1][0].strip()]

            img_with_boxes = draw_box(images[i], bxs, ["ocr"], 1.)
                
            if outputs:
                img_with_boxes.save(outputs[i], quality=95)
            
            buffered = io.BytesIO()
            img_with_boxes.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            img_list.append(img_str)
            bxs_list.append(bxs)
        
        return bxs_list, img_list

    def surya_to_bxs(self, images_path, output_path=None):
        images, outputs = init_in_out(images_path, output_path)

        bxs_list = []
        img_list = []
        langs = ["en"]
        for i, img in enumerate(images):
            det_processor, det_model = load_det_processor(), load_det_model()
            rec_model, rec_processor = load_rec_model(), load_rec_processor()

            predictions = run_ocr([img], [langs], det_model, det_processor, rec_model, rec_processor, 512, 32)
            
            # Process Surya OCR predictions
            bxs = [{
                "text": line.text,
                "x0": line.bbox[0],  
                "x1": line.bbox[2], 
                "top": line.bbox[1],  
                "bottom": line.bbox[3], 
                "type": "ocr",
                "score": line.confidence
            } for line in predictions[0].text_lines if line.text.strip()]

            # Draw boxes on image
            img_with_boxes = draw_box(images[i], bxs, ["ocr"], 1.)

            if outputs:
                img_with_boxes.save(outputs[i], quality=95)
            
            # Convert to base64
            buffered = io.BytesIO()
            img_with_boxes.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            img_list.append(img_str)
            bxs_list.append(bxs)
        
        return bxs_list, img_list

    def easyocr_to_bxs(self, images_path, output_path=None):
        images, outputs = init_in_out(images_path, output_path)
        bxs_list = []
        img_list = []
        
        reader = easyocr.Reader(['en'])
        
        for i, img in enumerate(images):
            result = reader.readtext(np.array(img))
            
            bxs = [{
                "text": line[1],
                "x0": float(min(line[0][0][0], line[0][3][0])),  
                "x1": float(max(line[0][1][0], line[0][2][0])),  
                "top": float(min(line[0][0][1], line[0][1][1])), 
                "bottom": float(max(line[0][2][1], line[0][3][1])), 
                "type": "ocr",
                "score": float(line[2]) 
            } for line in result if line[1].strip()]
            
            # Draw boxes on image
            img_with_boxes = draw_box(images[i], bxs, ["ocr"], 1.)
            
            if outputs:
                img_with_boxes.save(outputs[i], quality=95)
                
            # Convert to base64
            buffered = io.BytesIO()
            img_with_boxes.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            img_list.append(img_str)
            bxs_list.append(bxs)
        
        return bxs_list, img_list

    def rapidocr_to_bxs(self, images_path, output_path=None):
        images, outputs = init_in_out(images_path, output_path)
        bxs_list = []
        img_list = []
        
        engine = RapidOCR()
        
        for i, img in enumerate(images):
            result, _ = engine(np.array(img))
            
            bxs = [{
                "text": line[1],
                "x0": min(line[0][0][0], line[0][3][0]),  
                "x1": max(line[0][1][0], line[0][2][0]),  
                "top": min(line[0][0][1], line[0][1][1]), 
                "bottom": max(line[0][2][1], line[0][3][1]), 
                "type": "ocr",
                "score": line[2]  # confidence score
            } for line in result if line[1].strip()]
            
            img_with_boxes = draw_box(images[i], bxs, ["ocr"], 1.)
            
            if outputs:
                img_with_boxes.save(outputs[i], quality=95)
                
            # Convert to base64
            buffered = io.BytesIO()
            img_with_boxes.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            img_list.append(img_str)
            bxs_list.append(bxs)
        
        return bxs_list, img_list

    def mmocr_to_bxs(self, images_path, output_path=None):
        images, outputs = init_in_out(images_path, output_path)
        bxs_list = []
        img_list = []
        
        ocr = MMOCRInferencer(det='DBNet', rec='SAR')
        
        for i, img in enumerate(images):
            result = ocr(np.array(img))

            predictions = result['predictions'][0]
            texts = predictions['rec_texts']
            scores = predictions['rec_scores']
            polygons = predictions['det_polygons']
            
            # Convert to standard box format
            bxs = [{
                "text": text,
                "x0": min(poly[0], poly[2], poly[4], poly[6]),  
                "x1": max(poly[0], poly[2], poly[4], poly[6]), 
                "top": min(poly[1], poly[3], poly[5], poly[7]),  
                "bottom": max(poly[1], poly[3], poly[5], poly[7]), 
                "type": "ocr",
                "score": score
            } for text, score, poly in zip(texts, scores, polygons) if text.strip()]
            
            img_with_boxes = draw_box(images[i], bxs, ["ocr"], 1.)
            
            if outputs:
                img_with_boxes.save(outputs[i], quality=95)
                
            buffered = io.BytesIO()
            img_with_boxes.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            img_list.append(img_str)
            bxs_list.append(bxs)
            
        return bxs_list, img_list

    def __call__(self, filepath, model_name: str="RAGLOW", output_path=None):
        if model_name=="RAGFLOW":
            return self.ragflow_to_bxs(filepath, output_path)
        elif model_name=="TESSERACT":
            return self.pytesseract_to_bxs(filepath, output_path)
        elif model_name=="PADDLE":
            return self.paddleocr_to_bxs(filepath, output_path)
        elif model_name=="SURYA":
            return self.surya_to_bxs(filepath, output_path)
        elif model_name=='EASY':
            return self.easyocr_to_bxs(filepath, output_path)
        elif model_name=='RAPID':
            return self.rapidocr_to_bxs(filepath, output_path)
        elif model_name=='MM':
            return self.mmocr_to_bxs(filepath, output_path)

class layout_bodh(LayoutRecognizer):
    def __init__(self, domain):
        super().__init__(domain)

    def notOverlapped(self, a, b):
        return any([a["x1"] < b["x0"],
                    a["x0"] > b["x1"],
                    a["bottom"] < b["top"],
                    a["top"] > b["bottom"]])

    def merge_boxes_sequential(self, boxes):
        merged_box = deepcopy(boxes[0])
        for box in boxes[1:]:
            merged_box["x0"] = min(merged_box["x0"], box["x0"])
            merged_box["x1"] = max(merged_box["x1"], box["x1"])
            merged_box["top"] = min(merged_box["top"], box["top"])
            merged_box["bottom"] = max(merged_box["bottom"], box["bottom"])
            merged_box["text"] += " " + box["text"]
            merged_box["score"] = merged_box.get("score", 0) + box.get("score", 0)
        return merged_box

    def merge_processed_items(self, processed_items, threshold=0.7):
        layouts = [item for item in processed_items if all(key in item for key in ['x0', 'x1', 'top', 'bottom'])]
        i = 0
        while i < len(layouts):
            overlapping_boxes = [layouts[i]]
            largest_box_index = i
            j = i + 1
            while j < len(layouts):
                if not self.notOverlapped(layouts[i], layouts[j]):
                    overlapping_boxes.append(layouts[j])
                    if (layouts[j]["x1"] - layouts[j]["x0"]) * (layouts[j]["bottom"] - layouts[j]["top"]) > \
                    (layouts[largest_box_index]["x1"] - layouts[largest_box_index]["x0"]) * (layouts[largest_box_index]["bottom"] - layouts[largest_box_index]["top"]):
                        largest_box_index = j
                j += 1
            
            if len(overlapping_boxes) > 1:
                merged_box = self.merge_boxes_sequential(overlapping_boxes)
                merged_box["layoutno"] = layouts[largest_box_index]["layoutno"]
                merged_box["type"] = layouts[largest_box_index]["type"]
                layouts[i] = merged_box
                for _ in range(len(overlapping_boxes) - 1):
                    layouts.pop(i + 1)
            else:
                i += 1
        
        return layouts

    def __call__(self, images_path, model_name, *, output_path=None, threshold):
        images, outputs = init_in_out(images_path, output_path)
        
        # OCR
        ocr_results = []
        lz = layout_zila()
        ocr_results, _ = lz(images_path, model_name, output_path=output_path)
        with open('ocr.json', 'w') as f:
            json.dump(ocr_results, f, indent=4)

         # LayoutRecognizer
        ocr_res, page_layouts = super().__call__(images, ocr_results, scale_factor=1, thr=float(threshold), batch_size=16)
        
        # Create layout_map
        layout_map = {}
        for page_layout in page_layouts:
            for layout_item in page_layout:
                layout_type = layout_item['type']
                layout_page_num = layout_item['page_number']
                layoutno = layout_item.get('layoutno', f"{layout_type}-{layout_page_num}")
                key = (layout_type, layoutno, layout_page_num)
                if key not in layout_map:
                    layout_map[key] = []
                layout_map[key].append(layout_item)

        processed_items = {}
        layout_list = []

        # Process OCR results
        for ocr_item in ocr_res:
            layout_type = ocr_item.get('layout_type')
            layoutno = ocr_item.get('layoutno')
            pageno = ocr_item.get('page_no')
            text = ocr_item.get('text')

            # Initialize list for new page number if it doesn't exist
            if pageno not in processed_items:
                processed_items[pageno] = []

            # Try to find existing item on this page with same layout type and number
            existing_item = None
            for item in processed_items[pageno]:
                if item['type'] == layout_type and item['layoutno'] == layoutno:
                    existing_item = item
                    break

            # If we found an existing item, append the new text to it
            if existing_item:
                existing_item['text'] += " " + text
            else:
                # Create new item if none exists
                new_item = {
                    'type': layout_type,
                    'layoutno': layoutno,
                    'text': text
                }
                
                # Add bounding box information if available
                key = (layout_type, layoutno, pageno)
                if key in layout_map:
                    matching_layout = layout_map[key][0]
                    new_item.update({
                        'x0': matching_layout['x0'],
                        'x1': matching_layout['x1'],
                        'top': matching_layout['top'],
                        'bottom': matching_layout['bottom'],
                        'score': matching_layout['score']
                    })
                
                processed_items[pageno].append(new_item)

        img_list = []
        # Convert dictionary to list of lists, sorted by page number
        for pageno in sorted(k for k in processed_items.keys() if k is not None):
            img_with_boxes = draw_box(images[pageno-1], list(processed_items[pageno]), self.labels, float(threshold))
            if outputs:
                img_with_boxes.save(outputs[pageno-1], quality=95)
            # Instead of saving, convert to base64
            buffered = io.BytesIO()
            img_with_boxes.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            img_list.append(img_str)

            layout_list.append(processed_items[pageno])

        with open('layout.json', 'w') as f:
            json.dump(layout_list, f, indent=4)
        # finale = self.merge_processed_items(layout_list)
    
        return layout_list, img_list

    # def paginate_ocr_data(raw_text):
#     # Group OCR data by page number
#     paginated_data = {}
#     for page_no, item in enumerate(raw_text):
#         if page_no not in paginated_data:
#             paginated_data[page_no] = []
#         paginated_data[page_no].append(item)
    
#     return paginated_data

# filename = "/home/zok/Pictures/Screenshots/samp.png"
# raw_text, labeled_images = lz(filename)
# paginated_raw_text = paginate_ocr_data(raw_text)
# layout_data = layout_bodh(True, filename, 'output_dir', 0.005)
# print(layout_data)

