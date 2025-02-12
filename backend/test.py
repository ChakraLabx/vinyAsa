from vision.in_out import init_in_out

from surya.recognition import RecognitionPredictor
from surya.detection import DetectionPredictor
from surya.table_rec import TableRecPredictor

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

    def __call__(self, images_path, model_name, threshold: float=0.2, output_path=None):
        if model_name == 'SURYA':
            return self.surya_tables2html(images_path, output_path)
        elif model_name == 'RAGFLOW':
            return self.ragflow_table2html(images_path, output_path, threshold)
        else:
            raise ValueError(f"Unknown model name: {model_name}")

filepath = '/home/zok/Downloads/Complete Blood Count and ESR(CBC and ESR_f51ac205-717b-408c-8065-a7c1de904b4b_removed.pdf'
model_name = 'SURYA'

tk = TableKostaka()
table_html = tk(filepath, model_name, threshold = 0.2)
print(table_html)

