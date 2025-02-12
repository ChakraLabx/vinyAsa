from ultralytics import YOLO
from lipi import OCRLipi

class FormJnaiskasa:
    def viny_Form(image_list):
        model = YOLO("backend/deepLekh/viny_FORM.pt")
        names = model.model.names

        res = []
        for i, img in enumerate(image_list):
            results = model.track(img, persist=True)
            
            page_form = []
            boxes = results[0].boxes.xyxy.cpu().numpy() 
            clss = results[0].boxes.cls.cpu().numpy()
            confidences = results[0].boxes.conf.cpu().numpy()

            for cls, bbox, conf in zip(clss, boxes, confidences):
                label = names.get(int(cls)) 
                x1, y1, x2, y2 = box

                page_form.append({
                    'x0' : min(x1, x2),  
                    'x1' : max(x1, x2) ,   
                    'top': min(y1, y2),
                    'bottom' : max(y1, y2),
                    'type': label.lower(),
                    'score': float(conf) 
                })
            
            res.append(page_form)  

        return res