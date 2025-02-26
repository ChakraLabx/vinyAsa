import re
import os, sys
import argparse
import numpy as np

from surya.table_rec import TableRecPredictor
from surya.recognition import RecognitionPredictor
from surya.detection import DetectionPredictor

from vision.seeit import draw_box
from vision.file_utils import get_project_base_directory
from vision.recognizer import Recognizer
from vision.layout_recognizer import LayoutRecognizer
from vision.table_structure_recognizer import TableStructureRecognizer
from vision.ocr import OCR
from vision.in_out import init_in_out

class TableKostaka(object):
    def surya_tables2html(self, images_path, output_path=None):
        # SURYA category: functions related to generating HTML from SURYA results.
        def generate_html_table(table_result, ocr_results):
            """
            Create an HTML table from table detection results and OCR data.
            """
            cells = table_result.cells
            if not cells:
                return ""

            # Determine grid dimensions.
            max_row = max((cell.row_id + cell.rowspan - 1 for cell in cells), default=0)
            max_col = max((cell.col_id + cell.colspan - 1 for cell in cells), default=0)

            # Initialize grid and occupancy tracker.
            grid = [[None for _ in range(max_col + 1)] for _ in range(max_row + 1)]
            fill = [[False for _ in range(max_col + 1)] for _ in range(max_row + 1)]

            # Place cells in the grid.
            for cell in cells:
                row_start = cell.row_id
                col_start = cell.col_id
                row_end = row_start + cell.rowspan
                col_end = col_start + cell.colspan

                for r in range(row_start, row_end):
                    for c in range(col_start, col_end):
                        if r <= max_row and c <= max_col:
                            fill[r][c] = True
                grid[row_start][col_start] = cell

            # Generate HTML rows.
            html_rows = []
            for r in range(max_row + 1):
                html_cells = []
                for c in range(max_col + 1):
                    if fill[r][c]:
                        # Only create the HTML cell if this cell is at the top-left of the spanning cell.
                        cell = grid[r][c] if (grid[r][c] and grid[r][c].row_id == r and grid[r][c].col_id == c) else None
                        if cell:
                            cell_texts = []
                            # Loop through OCR text lines and add text if the box lies within the cell.
                            for line in ocr_results[0].text_lines:
                                if (line.bbox[0] >= cell.bbox[0] and
                                    line.bbox[2] <= cell.bbox[2] and
                                    line.bbox[1] >= cell.bbox[1] and
                                    line.bbox[3] <= cell.bbox[3]):
                                    cell_texts.append(line.text)
                            content = ' '.join(cell_texts).strip()
                            tag = 'th' if cell.is_header else 'td'
                            rowspan = f' rowspan="{cell.rowspan}"' if cell.rowspan > 1 else ''
                            colspan = f' colspan="{cell.colspan}"' if cell.colspan > 1 else ''
                            html_cells.append(f'<{tag}{rowspan}{colspan}>{content}</{tag}>')
                        else:
                            continue  # Skip spanned cells.
                    else:
                        html_cells.append('<td></td>')
                if html_cells:
                    html_rows.append(f'<tr>{"".join(html_cells)}</tr>')
            return f'<table>{"".join(html_rows)}</table>'

        def get_table_html(surya_tables, ocr_results):
            """
            Wrap each table's HTML with styling for SURYA results.
            """
            styled_htmls = []
            for table in surya_tables:
                table_html = generate_html_table(table, ocr_results)
                styled_html = f"""
                <html>
                <head>
                <style>
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }}
                th {{
                    background-color: #6ac1ca;
                    color: white;
                }}
                tr:nth-child(even) {{ background-color: #f2f2f2; }}
                </style>
                </head>
                <body>
                {table_html}
                </body>
                </html>
                """
                styled_htmls.append(styled_html)
            return styled_htmls

        def table_2_html(images_path, output_path):
            """
            Process images with the SURYA model to produce HTML table representations.
            """
            ocr_list = []
            table_list = []
            images, outputs = init_in_out(images_path, output_path)
            langs = ["en"]
            for i, img in enumerate(images):
                # OCR processing.
                recognition_predictor = RecognitionPredictor()
                detection_predictor = DetectionPredictor()
                predictions = recognition_predictor([img], [langs], detection_predictor)
                ocr_list.append(predictions)

                # Table detection.
                table_rec_predictor = TableRecPredictor()
                table_predictions = table_rec_predictor([img])
                table_list.append(table_predictions)

            # with open('ocr_list.txt', 'w') as f:
            #     f.write(str(ocr_list))
            # with open('table_list.txt', 'w') as f:
            #     f.write(str(table_list))

            all_html = []
            for img_ocr, img_tables in zip(ocr_list, table_list):
                html_for_image = get_table_html(img_tables, img_ocr)
                all_html.extend(html_for_image)
            return all_html 

        return table_2_html(images_path, output_path)

    def ragflow_table2html(self, images_path, output_path, threshold):
        def get_table_html(img, tb_cpns, ocr):
            """
            Generate HTML for a table using RAGFLOW outputs.
            """
            boxes = ocr(np.array(img))
            boxes = Recognizer.sort_Y_firstly(
                [{"x0": b[0][0], "x1": b[1][0],
                  "top": b[0][1], "text": t[0],
                  "bottom": b[-1][1],
                  "layout_type": "table",
                  "page_number": 0} for b, t in boxes if b[0][0] <= b[1][0] and b[0][1] <= b[-1][1]],
                np.mean([b[-1][1] - b[0][1] for b, _ in boxes]) / 3
            )

            def gather(kwd, fzy=10, ption=0.6):
                nonlocal boxes
                eles = Recognizer.sort_Y_firstly(
                    [r for r in tb_cpns if re.match(kwd, r["label"])], fzy)
                eles = Recognizer.layouts_cleanup(boxes, eles, 5, ption)
                return Recognizer.sort_Y_firstly(eles, 0)

            headers = gather(r".*header$")
            rows = gather(r".* (row|header)")
            spans = gather(r".*spanning")
            clmns = sorted([r for r in tb_cpns if re.match(r"table column$", r["label"])],
                           key=lambda x: x["x0"])
            clmns = Recognizer.layouts_cleanup(boxes, clmns, 5, 0.5)

            for b in boxes:
                ii = Recognizer.find_overlapped_with_threshold(b, rows, thr=0.3)
                if ii is not None:
                    b["R"] = ii
                    b["R_top"] = rows[ii]["top"]
                    b["R_bott"] = rows[ii]["bottom"]

                ii = Recognizer.find_overlapped_with_threshold(b, headers, thr=0.3)
                if ii is not None:
                    b["H_top"] = headers[ii]["top"]
                    b["H_bott"] = headers[ii]["bottom"]
                    b["H_left"] = headers[ii]["x0"]
                    b["H_right"] = headers[ii]["x1"]
                    b["H"] = ii

                ii = Recognizer.find_horizontally_tightest_fit(b, clmns)
                if ii is not None:
                    b["C"] = ii
                    b["C_left"] = clmns[ii]["x0"]
                    b["C_right"] = clmns[ii]["x1"]

                ii = Recognizer.find_overlapped_with_threshold(b, spans, thr=0.3)
                if ii is not None:
                    b["H_top"] = spans[ii]["top"]
                    b["H_bott"] = spans[ii]["bottom"]
                    b["H_left"] = spans[ii]["x0"]
                    b["H_right"] = spans[ii]["x1"]
                    b["SP"] = ii

            html = """
            <html>
            <head>
            <style>
            ._table_1nkzy_11 {
                margin: auto;
                width: 70%%;
                padding: 10px;
            }
            ._table_1nkzy_11 p {
                margin-bottom: 50px;
                border: 1px solid #e1e1e1;
            }
            caption {
                color: #6ac1ca;
                font-size: 20px;
                height: 50px;
                line-height: 50px;
                font-weight: 600;
                margin-bottom: 10px;
            }
            ._table_1nkzy_11 table {
                width: 100%%;
                border-collapse: collapse;
            }
            th {
                color: #fff;
                background-color: #6ac1ca;
            }
            td:hover {
                background: #c1e8e8;
            }
            tr:nth-child(even) {
                background-color: #f2f2f2;
            }
            ._table_1nkzy_11 th,
            ._table_1nkzy_11 td {
                text-align: center;
                border: 1px solid #ddd;
                padding: 8px;
            }
            </style>
            </head>
            <body>
            %s
            </body>
            </html>
            """ % TableStructureRecognizer.construct_table(boxes, html=True)
            return html

        def table_2_html(images_path, output_path, threshold):
            """
            Process images with the RAGFLOW model to produce HTML table representations.
            """
            images, outputs = init_in_out(images_path, output_path)
            detr = TableStructureRecognizer()
            ocr = OCR()

            html_list = []
            layouts = detr(images, float(threshold))
            for i, lyt in enumerate(layouts):
                html = get_table_html(images[i], lyt, ocr)
                html_list.append(html)
            return html_list

        return table_2_html(images_path, output_path, threshold)

    def __call__(self, images_path, model_name, threshold: float=0.2, output_path=None):
        if model_name == 'SURYA':
            return self.surya_tables2html(images_path, output_path)
        elif model_name == 'RAGFLOW':
            return self.ragflow_table2html(images_path, output_path, threshold)
        else:
            raise ValueError(f"Unknown model name: {model_name}")