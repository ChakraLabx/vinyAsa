import json
import os
import io
import base64
import numpy as np
from PIL import Image
from copy import deepcopy

from vision.seeit import draw_box
from vision.in_out import init_in_out
from vision.file_utils import get_project_base_directory
from vision.OCR_Lipi import OCRLipi
from vision.layout_recognizer import LayoutRecognizer


class LayoutVyavastha(LayoutRecognizer):
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

    def layout_mapping(self, ocr_res, page_layouts, images, outputs, threshold=0.005):
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
            if outputs:
                img_with_boxes = draw_box(images[pageno-1], list(processed_items[pageno]), self.labels, float(threshold))
                # img_with_boxes.save(outputs[pageno-1], quality=95)
                # Instead of saving, convert to base64
                buffered = io.BytesIO()
                img_with_boxes.save(buffered, format="JPEG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                img_list.append(img_str)

            layout_list.append(processed_items[pageno])

        # with open('layout.json', 'w') as f:
        #     json.dump(layout_list, f, indent=4)
        # finale = self.merge_processed_items(layout_list)
    
        return layout_list, img_list if img_list else None

    def ragflow_Layout(self, images_path, output_path, model_name, threshold):
        images, outputs = init_in_out(images_path, output_path)
        
        # OCR
        lz = OCRLipi()
        ocr_results = lz(images_path, model_name)
        # with open('ocr.json', 'w') as f:
        #     json.dump(ocr_results, f, indent=4)

        # LayoutRecognizer
        ocr_res, page_layouts = super().__call__(images, ocr_results[0], model_name, scale_factor=1, thr=float(threshold), batch_size=16)
        return self.layout_mapping(ocr_res, page_layouts, images, outputs, threshold)

    def surya_Layout(self, images_path, output_path, model_name):
        images, outputs = init_in_out(images_path, output_path)

        # OCR
        lz = OCRLipi()
        ocr_results = lz(images_path, model_name)

        # LayoutRecognizer
        ocr_res, page_layouts = super().__call__(images, ocr_results[0], model_name, scale_factor=1, batch_size=4)
        return self.layout_mapping(ocr_res, page_layouts, images, output_path)

    def viny_Layout(self, images_path, output_path, model_name):
        images, outputs = init_in_out(images_path, output_path)

        # OCR
        lz = OCRLipi()
        ocr_results = lz(images_path, model_name)

        # LayoutRecognizer
        ocr_res, page_layouts = super().__call__(images, ocr_results[0], model_name, scale_factor=1, batch_size=4)
        return self.layout_mapping(ocr_res, page_layouts, images, output_path)

    def __call__(self, filepath, model_name, threshold=0.005, output_path=None):
        if model_name=="RAGFLOW":
            return self.ragflow_Layout(filepath, output_path, model_name, threshold)
        elif model_name=="SURYA":
            return self.surya_Layout(filepath, output_path, model_name)
        elif model_name=="VINY":
            return self.viny_Layout(filepath, output_path, model_name)