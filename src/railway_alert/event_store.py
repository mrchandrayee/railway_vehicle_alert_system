import json
from pathlib import Path
from datetime import datetime, timezone

class EventStore:
    def __init__(self,directory):
        self.directory=Path(directory); self.directory.mkdir(parents=True,exist_ok=True)
        self.log_path=self.directory/"events.jsonl"

    def save_snapshot(self,event_id,frame):
        import cv2
        path=self.directory/f"{event_id}.jpg"
        cv2.imwrite(str(path),frame,[cv2.IMWRITE_JPEG_QUALITY,88])
        return path

    def append(self,event, camera_id, snapshot_path=None, clip_path=None):
        record={"event_id":event.event_type+"_"+str(event.track_id)+"_"+str(event.frame_index),
                "event":event.event_type,"timestamp":datetime.now(timezone.utc).isoformat(),
                "camera_id":camera_id,"track_id":event.track_id,"class":event.class_name,
                "confidence":round(float(event.confidence),4),"bbox":list(map(float,event.bbox)),
                "snapshot":str(snapshot_path) if snapshot_path else None,
                "clip":str(clip_path) if clip_path else None}
        with self.log_path.open("a",encoding="utf-8") as f:
            f.write(json.dumps(record)+"\n")
        return record
