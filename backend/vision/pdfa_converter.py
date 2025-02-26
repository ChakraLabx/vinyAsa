import sys
import os
import time
import subprocess
import ocrmypdf
import logging
import img2pdf

def convert_to_pdfa(input_path, output_path):
    start_time = time.time()
    logger = logging.getLogger(__name__)
    temp_pdfa2b = None
    _, ext = os.path.splitext(input_path)
    ext = ext.lower()
    
    if ext in ['.jpg', '.jpeg', '.png']:
        with open(output_path, "wb") as f:
            f.write(img2pdf.convert(input_path))
    
    try:
        # PDF/A-2B conversion
        temp_pdfa2b = f"{os.path.splitext(output_path)[0]}_pdfa2b.pdf"
        gs_command = [
            'gs',
            '-dPDFA=2',
            '-dBATCH',
            '-dNOPAUSE',
            '-dNOOUTERSAVE',
            '-sProcessColorModel=DeviceRGB',
            '-sDEVICE=pdfwrite',
            '-dPDFACompatibilityPolicy=2',
            '-sColorConversionStrategy=RGB',
            '-dCompatibilityLevel=1.7',
            f'-sOutputFile={temp_pdfa2b}',
            output_path
        ]
        
        subprocess.run(gs_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # OCR processing
        ocrmypdf.ocr(
            temp_pdfa2b, 
            output_path,
            force_ocr=True,
            output_type='pdfa',
            progress_bar=False
        )
        
        # Cleanup temporary file
        if os.path.exists(temp_pdfa2b):
            os.remove(temp_pdfa2b)
            
        return True
        
    except Exception as e:
        logger.error(f"Conversion failed: {str(e)}")
        if temp_pdfa2b and os.path.exists(temp_pdfa2b):
            os.remove(temp_pdfa2b)
        return False
