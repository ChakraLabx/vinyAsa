import json
import os
import io
import base64
import numpy as np
from PIL import Image
from copy import deepcopy

import easyocr
import pytesseract
from ultralytics import YOLO
from paddleocr import PaddleOCR
from mmocr.apis import MMOCRInferencer
from rapidocr_onnxruntime import RapidOCR
from surya.recognition import RecognitionPredictor
from surya.detection import DetectionPredictor

from vision.seeit import draw_box
from vision.ocr import OCR
from vision.file_utils import get_project_base_directory
from vision.in_out import init_in_out

class OCRLipi(OCR):
    def __init__(self):
        try:
            model_dir = os.path.join(
                    get_project_base_directory(),
                    "deepLekh")
            super().__init__(model_dir)
        except Exception as e:
            model_dir = snapshot_download(repo_id="InfiniFlow/deepdoc",
                                          local_dir=os.path.join(get_project_base_directory(), "deepLekh"),
                                          local_dir_use_symlinks=False)

            super().__init__(model_dir)

    def ragflow_OCR(self, images_path, output_path=None):
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

            if outputs:
                img_with_boxes = draw_box(images[i], bxs, ["ocr"])
                # img_with_boxes.save(outputs[i], quality=95)
                # Instead of saving, convert to base64
                buffered = io.BytesIO()
                img_with_boxes.save(buffered, format="JPEG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                img_list.append(img_str)

            bxs_list.append(bxs)

        return bxs_list, img_list if img_list else None

    def pytesseract_OCR(self, images_path, output_path=None):
        images, outputs = init_in_out(images_path, output_path)
        img_list = []
        bxs_list = []
        
        for i, img in enumerate(images):
            bxs = pytesseract.image_to_data(np.array(img), output_type=pytesseract.Output.DICT)
        
            bxs = [{
                "text": bxs['text'][j],
                "x0": bxs['left'][j],
                "x1": bxs['left'][j] + bxs['width'][j],
                "top": bxs['top'][j],
                "bottom": bxs['top'][j] + bxs['height'][j],
                "type": "ocr",
                "score": int(bxs['conf'][j]) / 100 
            } for j in range(len(bxs['text'])) 
            if bxs['text'][j].strip() and int(bxs['conf'][j]) > 60]
            
            if outputs:
                img_with_boxes = draw_box(images[i], bxs, ["ocr"])
                # img_with_boxes.save(outputs[i], quality=95)
                # Instead of saving, convert to base64
                buffered = io.BytesIO()
                img_with_boxes.save(buffered, format="JPEG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                img_list.append(img_str)

            bxs_list.append(bxs)

        return bxs_list, img_list if img_list else None

    def paddle_OCR(self, images_path, output_path=None):
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

            if outputs:
                img_with_boxes = draw_box(images[i], bxs, ["ocr"])
                buffered = io.BytesIO()
                img_with_boxes.save(buffered, format="JPEG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                img_list.append(img_str)

            bxs_list.append(bxs)

        return bxs_list, img_list if img_list else None

    def surya_OCR(self, images_path, output_path=None):
        images, outputs = init_in_out(images_path, output_path)

        bxs_list = []
        img_list = []
        langs = ["en"]
        for i, img in enumerate(images):
            recognition_predictor = RecognitionPredictor()
            detection_predictor = DetectionPredictor()

            predictions = recognition_predictor([img], [langs], detection_predictor)
            
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

            if outputs:
                img_with_boxes = draw_box(images[i], bxs, ["ocr"])
                # img_with_boxes.save(outputs[i], quality=95)
                # Instead of saving, convert to base64
                buffered = io.BytesIO()
                img_with_boxes.save(buffered, format="JPEG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                img_list.append(img_str)

            bxs_list.append(bxs)

        return bxs_list, img_list if img_list else None

    def easy_OCR(self, images_path, output_path=None):
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
            
            if outputs:
                img_with_boxes = draw_box(images[i], bxs, ["ocr"])
                # img_with_boxes.save(outputs[i], quality=95)
                # Instead of saving, convert to base64
                buffered = io.BytesIO()
                img_with_boxes.save(buffered, format="JPEG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                img_list.append(img_str)

            bxs_list.append(bxs)

        return bxs_list, img_list if img_list else None

    def rapidocr_OCR(self, images_path, output_path=None):
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
            
            if outputs:
                img_with_boxes = draw_box(images[i], bxs, ["ocr"])
                # img_with_boxes.save(outputs[i], quality=95)
                # Instead of saving, convert to base64
                buffered = io.BytesIO()
                img_with_boxes.save(buffered, format="JPEG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                img_list.append(img_str)

            bxs_list.append(bxs)

        return bxs_list, img_list if img_list else None

    def rapid_OCR(self, images_path, output_path=None):
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
            
            if outputs:
                img_with_boxes = draw_box(images[i], bxs, ["ocr"])
                # img_with_boxes.save(outputs[i], quality=95)
                # Instead of saving, convert to base64
                buffered = io.BytesIO()
                img_with_boxes.save(buffered, format="JPEG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                img_list.append(img_str)

            bxs_list.append(bxs)

        return bxs_list, img_list if img_list else None

    def __call__(self, filepath, model_name, output_path=None):
        if model_name=="RAGFLOW":
            return self.ragflow_OCR(filepath, output_path)
        elif model_name=="TESSERACT":
            return self.pytesseract_OCR(filepath, output_path)
        elif model_name=="PADDLE":
            return self.paddle_OCR(filepath, output_path)
        elif model_name=="SURYA":
            return self.surya_OCR(filepath, output_path)
        elif model_name=='EASY':
            return self.easy_OCR(filepath, output_path)
        elif model_name=='RAPID':
            return self.rapidocr_OCR(filepath, output_path)
        elif model_name=='MM':
            return self.rapid_OCR(filepath, output_path)
        else:
            return self.ragflow_OCR(filepath, output_path)