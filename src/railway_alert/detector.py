from ultralytics import YOLO
from .models import Detection

class VehicleDetector:
    def __init__(self, model, confidence=.30, iou=.50, classes=None, device=None):
        self.model=YOLO(model)
        self.confidence=float(confidence); self.iou=float(iou)
        self.classes=classes; self.device=device

    def detect(self, frame):
        kwargs={"conf":self.confidence,"iou":self.iou,"classes":self.classes,"verbose":False}
        if self.device is not None:
            kwargs["device"]=self.device
        result=self.model.predict(frame,**kwargs)[0]
        detections=[]
        if result.boxes is None:
            return detections
        for b in result.boxes:
            cid=int(b.cls[0].item())
            detections.append(Detection(
                tuple(map(float,b.xyxy[0].cpu().numpy().tolist())),
                float(b.conf[0].item()),cid,str(result.names.get(cid,cid))))
        return detections
