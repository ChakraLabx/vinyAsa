import io
import base64
import pytesseract
import numpy as np
from PIL import Image
from ultralytics import YOLO

from vision.ocr import OCR
from vision.in_out import init_in_out
from vision.seeit import draw_box

class FormJnaiskasa:
    def ragflow_OCR(self, img):
        ocr = OCR()
        boxes = ocr(np.array(img))
        bxs = [{
            "text": t[0],
            "x0": b[0][0],
            "x1": b[1][0],
            "top": b[0][1],
            "bottom": b[-1][1],
            "type": "ocr",
            "score": 1.0  
        } for b, t in boxes if b[0][0] <= b[1][0] and b[0][1] <= b[-1][1]]
        return bxs

    def viny_Form(self, images_path, output_path):
        images, outputs = init_in_out(images_path, output_path)
        model = YOLO("deepLekh/viny_FORM.pt")
        names = model.model.names
        
        res = []
        
        for i, img in enumerate(images):
            results = model.track(np.array(img), persist=True)

            page_form = []
            boxes = results[0].boxes.xyxy.cpu().numpy() 
            clss = results[0].boxes.cls.cpu().numpy()
            confidences = results[0].boxes.conf.cpu().numpy()
            
            detections = []
            for cls, bbox, conf in zip(clss, boxes, confidences):
                label = names.get(int(cls)) 
                x1, y1, x2, y2 = bbox
                detections.append({
                    'x0': float(min(x1, x2)), 
                    'x1': float(max(x1, x2)),
                    'top': float(min(y1, y2)),
                    'bottom': float(max(y1, y2)),
                    'type': label.lower(),
                    'score': float(conf)
                })

            detections = sorted(detections, key=lambda d: (d['top'], d['x0']))
            # print('det', detections)
            ocr_results = self.ragflow_OCR(img)
            for det in detections:
                det['text'] = "" 
                
                for ocr_item in ocr_results: 
                    ocr_x0, ocr_x1 = ocr_item['x0'], ocr_item['x1']
                    ocr_top, ocr_bottom = ocr_item['top'], ocr_item['bottom']
                    
                    if (det['x0'] <= ocr_x1 and det['x1'] >= ocr_x0 and
                        det['top'] <= ocr_bottom and det['bottom'] >= ocr_top):
                        det['text'] += " " + ocr_item['text']

                det['text'] = det['text'].strip() if det['text'] else 'N/A'
            
            # Pair keys and values
            key_value_pairs = []
            for j, current in enumerate(detections):
                if current['type'] == 'key' and j + 1 < len(detections):
                    next_det = detections[j + 1]
                    if next_det['type'] == 'value':
                        key_text = current['text']
                        value_text = next_det['text']
                        
                        key_value_pairs.append({
                            "key": [{
                                "key_text": key_text,
                                "x0": current['x0'],
                                "x1": current['x1'],
                                "top": current['top'],
                                "bottom": current['bottom'],
                                "type": current['type'],
                                "score": float(current['score'])
                            }],
                            "value": [{
                                "value_text": value_text,
                                "x0": next_det['x0'],
                                "x1": next_det['x1'],
                                "top": next_det['top'],
                                "bottom": next_det['bottom'],
                                "type": next_det['type'],
                                "score": float(next_det['score'])
                            }]
                        })
            
            res.append(key_value_pairs)

            if outputs:
                bxs = []
                img_list = []
                for pair in key_value_pairs:
                    k = pair["key"][0]
                    v = pair["value"][0]
                    bxs.append({
                        "text": k["key_text"],
                        "x0": k["x0"],
                        "x1": k["x1"],
                        "top": k["top"],
                        "bottom": k["bottom"],
                        "type": k["type"],
                        "score": k["score"]
                    })
                    bxs.append({
                        "text": v["value_text"],
                        "x0": v["x0"],
                        "x1": v["x1"],
                        "top": v["top"],
                        "bottom": v["bottom"],
                        "type": v["type"],
                        "score": v["score"]
                    })

                annotated_img = draw_box(images[i], bxs, ["key", "value"])

                # Convert annotated image to base64
                buffered = io.BytesIO()
                annotated_img.save(buffered, format="JPEG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                img_list.append(img_str)

        return res, img_list

    def __call__(self, images_path, model_name, output_path=None):
        if model_name == 'VINY':
            return self.viny_Form(images_path, output_path)
        else:
            raise ValueError(f"Unknown model name: {model_name}")