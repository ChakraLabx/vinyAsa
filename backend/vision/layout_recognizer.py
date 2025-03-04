import os
import re
from collections import Counter
from copy import deepcopy
import numpy as np
from huggingface_hub import snapshot_download

from vision.file_utils import get_project_base_directory
from vision.recognizer import Recognizer


class LayoutRecognizer(Recognizer):
    labels = [
        "_background_",
        "Text",
        "Title",
        "Figure",
        "Figure caption",
        "Table",
        "Table caption",
        "Header",
        "Footer",
        "Reference",
        "Equation",
        "Caption", 
        "Footnote", 
        "Formula", 
        "List-item", 
        "Page-footer", 
        "Page-header", 
        "Picture", 
        "Section-header", 
        "Form", 
        "Table-of-contents", 
        "Handwriting", 
        "Text-inline-math",
        "Plain Text", 
        "Abandon"
    ]

    def __init__(self, domain):
        try:
            model_dir = os.path.join(
                    get_project_base_directory(),
                    "deepLekh")
            super().__init__(self.labels, domain, model_dir)
        except Exception as e:
            model_dir = snapshot_download(repo_id="InfiniFlow/deepdoc",
                                          local_dir=os.path.join(get_project_base_directory(), "deepLekh"),
                                          local_dir_use_symlinks=False)
            super().__init__(self.labels, domain, model_dir)

        self.garbage_layouts = ["figure", "figure caption", "Picture"]

    def __call__(self, image_list, ocr_res, model= "RAGFLOW", scale_factor=1,
                thr=0.2, batch_size=16, drop=True):
        def __is_garbage(b):
            patt = [r"^•+$", r"\.{3,}", "^[0-9]{1,2} / ?[0-9]{1,2}$",
                    r"^[0-9]{1,2} of [0-9]{1,2}$", "^http://[^ ]{12,}",
                    "[0-9a-z._-]+@[a-z0-9-]+\\.[a-z]{2,3}",
                    r"\(cid *: *[0-9]+ *\)"
                    ]
            return any([re.search(p, b["text"]) for p in patt])

        if model == "RAGFLOW":
            layouts = super().__call__(image_list, thr, batch_size, model)
        elif model == "SURYA":
            layouts = super().__call__(image_list, thr, batch_size, model)
        elif model == "VINY":
            layouts = super().__call__(image_list, thr, batch_size, model)
        
        assert len(image_list) == len(ocr_res)
        boxes = []

        assert len(image_list) == len(layouts)
        garbages = {}
        page_layout = []
        
        for pn, lts in enumerate(layouts):
            bxs = ocr_res[pn]
            lts = [{"type": b["type"],
                    "score": float(b["score"]),
                    "x0": b["bbox"][0] / scale_factor, 
                    "x1": b["bbox"][2] / scale_factor,
                    "top": b["bbox"][1] / scale_factor, 
                    "bottom": b["bbox"][-1] / scale_factor,
                    "page_number": pn+1,
                    } for b in lts]
            
            lts = self.sort_Y_firstly(lts, np.mean(
                [l["bottom"] - l["top"] for l in lts]) / 2)
            lts = self.layouts_cleanup(bxs, lts, thr=0.7)
            page_layout.append(lts)

            def findLayout(ty):
                nonlocal bxs, lts, self
                lts_ = [lt for lt in lts if lt["type"] == ty]
                i = 0
                layout_count = 0
                while i < len(bxs):
                    if __is_garbage(bxs[i]):
                        bxs.pop(i)
                        continue

                    ii = self.find_overlapped_with_threshold(bxs[i], lts_, thr=0.4)
                    if ii is None:  
                        if layout_count < len(lts_):
                            lts_[layout_count]["visited"] = False
                            lts_[layout_count]["layoutno"] = f"{ty}-{layout_count}"
                            layout_count += 1
                        if not bxs[i].get("layout_type"):
                            bxs[i]["layout_type"] = ""
                        i += 1
                        continue
                    
                    lts_[ii]["visited"] = True
                    lts_[ii]["layoutno"] = f"{ty}-{ii}"
                    keep_feats = [
                        (lts_[ii]["type"] == "footer") and bxs[i]["bottom"] < image_list[pn].size[1] * 0.9 / scale_factor,
                        (lts_[ii]["type"] == "header") and bxs[i]["top"] > image_list[pn].size[1] * 0.1 / scale_factor,
                    ]
                    if drop and lts_[ii]["type"] in self.garbage_layouts and not any(keep_feats):
                        if lts_[ii]["type"] not in garbages:
                            garbages[lts_[ii]["type"]] = []
                        garbages[lts_[ii]["type"]].append(bxs[i]["text"])
                        bxs.pop(i)
                        continue

                    bxs[i]["layoutno"] = lts_[ii]["layoutno"]
                    bxs[i]["layout_type"] = lts_[ii]["type"]
                    bxs[i]["page_no"] = lts_[ii]["page_number"]
                    i += 1

            # Updated layout types to match the new labels
            layout_types = [
                "text", "title", "table",
                "table-of-contents", 
                "table caption", "header", "footer", "reference", 
                "equation", "page-footer", "page-header", "caption", "footnote", "formula", 
                "list-item", "picture", 
                "section-header", "form", 
                "handwriting", "text-inline-math", 
                "plain text", "abandon"
            ]
            
            for lt in layout_types:
                findLayout(lt)

            # add box to figure layouts which has not text box
            for i, lt in enumerate(
                    [lt for lt in lts if lt["type"] in ["figure", "equation", "picture"]]):
                if lt.get("visited"):
                    continue
                lt = deepcopy(lt)
                lt["text"] = ""
                lt["layout_type"] = lt["type"] 
                lt["layoutno"] = f"{lt['layout_type']}-{i}"
                bxs.append(lt)

            boxes.extend(bxs)

        ocr_res = boxes

        garbag_set = set()
        for k in garbages.keys():
            garbages[k] = Counter(garbages[k])
            for g, c in garbages[k].items():
                if c > 1:
                    garbag_set.add(g)

        ocr_res = [b for b in ocr_res if b["text"].strip() not in garbag_set]
        return ocr_res, page_layout