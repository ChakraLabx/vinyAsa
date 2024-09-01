import json
import os
import numpy as np
from PIL import Image
from seeit import draw_box
from ocr import OCR
from layout_recognizer import LayoutRecognizer
from recognizer import Recognizer
from file_utils import get_project_base_directory
from in_out import init_in_out

def layout_zila(image):
    ocr = OCR()
    bxs = ocr(np.array(image))
    bxs = [(line[0], line[1][0]) for line in bxs]
    bxs = [{
        "text": t,
        "bbox": [b[0][0], b[0][1], b[1][0], b[-1][1]],
        "x0": b[0][0],
        "x1": b[1][0],
        "top": b[0][1],
        "bottom": b[-1][1],
        "type": "ocr",
        "score": 1} for b, t in bxs if b[0][0] <= b[1][0] and b[0][1] <= b[-1][1]]
    
    return bxs

def layout_bodh(layout, images_path, output_path, threshold):
    images, outputs = init_in_out(images_path, output_path)
    if layout:
        labels = LayoutRecognizer.labels
        detr = LayoutRecognizer("layout")
        ocr_results = []
        # for img in images:
        #     ocr_result = layout_zila(img)
        #     ocr_results.append(ocr_result)
        # with open('ocr_results.json', 'w') as json_file:
        #     json.dump(ocr_results, json_file)

        # with open('ocr_results.json', 'r') as json_file:
        #     ocr_results = json.load(json_file)
        
        # ocr_res, page_layouts = detr(images, ocr_results, scale_factor=1, thr=float(threshold), batch_size=16)
        # with open('ocr_res.json', 'w') as json_file:
        #     json.dump(ocr_res, json_file)
        with open('ocr_res.json', 'r') as json_file:
            ocr_res = json.load(json_file)

        # with open('page_layouts.json', 'w') as json_file:
        #     json.dump(page_layouts, json_file)
        with open('page_layouts.json', 'r') as json_file:
            page_layouts = json.load(json_file)

        
        processed_items = {}
        layout_map = {}

        # Create layout_map
        for page_layout in page_layouts:
            for layout_item in page_layout:
                layout_type = layout_item['type']
                layout_page_num = layout_item['page_number']
                layoutno = layout_item.get('layoutno', f"{layout_type}-{layout_page_num}")
                key = (layout_type, layoutno, layout_page_num)
                if key not in layout_map:
                    layout_map[key] = []
                layout_map[key].append(layout_item)

        # Process OCR results
        for ocr_item in ocr_res:
            layout_type = ocr_item.get('layout_type')
            layoutno = ocr_item.get('layoutno')
            pageno = ocr_item.get('page_no')
            text = ocr_item.get('text')
            key = (layout_type, layoutno, pageno)

            if key not in processed_items:
                processed_items[key] = {
                    'layout_type': layout_type,
                    'layoutno': layoutno,
                    'page_no': pageno,
                    'text': text
                }
            else:
                processed_items[key]['text'] += " " + text

            # Add bounding box information from page_layouts
            if key in layout_map:
                matching_layout = layout_map[key][0]
                processed_items[key].update({
                    'x0': matching_layout['x0'],
                    'x1': matching_layout['x1'],
                    'top': matching_layout['top'],
                    'bottom': matching_layout['bottom'],
                    'score': matching_layout['score']
                })

        # Draw boxes and save images
        for i, img in enumerate(images):
            page_items = [item for item in processed_items.values() if item['page_no'] == i + 1]
            img_with_boxes = draw_box(img, page_items, labels, float(threshold))
            img_with_boxes.save(outputs[i], quality=95)
            print("save result to: " + outputs[i])

        return list(processed_items.values())

filename = "/home/zok/Pictures/Screenshots/samp.png"
# raw_text = layout_zila(filename)
layout_data = layout_bodh(True, filename, 'output_dir', 0.005)
print(layout_data)