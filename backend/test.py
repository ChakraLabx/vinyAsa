import easyocr

reader = easyocr.Reader(['en'])
result = reader.readtext('/home/zok/Pictures/09-7012530-003.jpg')

bxs = [{
    "text": line[1],
    "x0": min(line[0][0][0], line[0][3][0]),  
    "x1": max(line[0][1][0], line[0][2][0]),  
    "top": min(line[0][0][1], line[0][1][1]), 
    "bottom": max(line[0][2][1], line[0][3][1]), 
    "type": "ocr",
    "score": line[2]  
} for line in result if line[1].strip()]

print(bxs)