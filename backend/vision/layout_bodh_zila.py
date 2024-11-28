import json
import os
import io
import base64
import numpy as np
from PIL import Image
from copy import deepcopy
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

    def __call__(self, images_path, *, output_path=None):
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

    def __call__(self, images_path, *, output_path=None, threshold):
        images, outputs = init_in_out(images_path, output_path)

        # OCR
        ocr_results = []
        lz = layout_zila()
        ocr_results, _ = lz(images_path, output_path=output_path)

        # LayoutRecognizer
        ocr_res, page_layouts = super().__call__(images, ocr_results, scale_factor=1, thr=float(threshold), batch_size=16)
        
        # Create layout_map
        processed_items = {}
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

        # Process OCR results
        for ocr_item in ocr_res:
            layout_type = ocr_item.get('layout_type')
            layoutno = ocr_item.get('layoutno')
            pageno = ocr_item.get('page_no')
            text = ocr_item.get('text')
            key = (layout_type, layoutno, pageno)

            if key not in processed_items:
                processed_items[key] = {
                    'type': layout_type,
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
        
        finale = self.merge_processed_items(list(processed_items.values()))

        img_list = []
        # Draw boxes and further processing
        for i, img in enumerate(images):
            page_items = [item for item in processed_items.values() if item['page_no'] == i + 1]
            img_with_boxes = draw_box(img, page_items, self.labels, float(threshold))
            if outputs:
                img_with_boxes.save(outputs[i], quality=95)
            # Instead of saving, convert to base64
            buffered = io.BytesIO()
            img_with_boxes.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            img_list.append(img_str)
        
        return list(processed_items.values()), img_list

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