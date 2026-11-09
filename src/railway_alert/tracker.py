from collections import defaultdict, deque
from .models import Track
from .geometry import box_iou, anchor_point

class IoUTracker:
    """Small class-aware tracker for fixed-camera scenes; replace with ByteTrack for production."""
    def __init__(self,max_age=35,match_iou=.18,trail_length=24,anchor="bottom"):
        self.max_age=int(max_age); self.match_iou=float(match_iou)
        self.trail_length=int(trail_length); self.anchor=anchor
        self.tracks={}; self.next_id=1

    def update(self,detections):
        for tr in self.tracks.values(): tr.age+=1
        free=set(self.tracks)
        for det in detections:
            best_id=None; best=0.0
            for tid in free:
                tr=self.tracks[tid]
                if tr.class_id!=det.class_id: continue
                score=box_iou(det.bbox,tr.bbox)
                if score>best: best_id,best=tid,score
            if best_id is not None and best>=self.match_iou:
                tr=self.tracks[best_id]
                tr.bbox=det.bbox; tr.age=0; tr.confidence=det.confidence
                tr.class_name=det.class_name
                det.track_id=best_id
                free.remove(best_id)
            else:
                tid=self.next_id; self.next_id+=1
                tr=Track(tid,det.bbox,det.class_id,det.class_name,det.confidence,0,deque(maxlen=self.trail_length))
                self.tracks[tid]=tr; det.track_id=tid
            tr=self.tracks[det.track_id]
            tr.trail.append(tuple(map(int,anchor_point(det.bbox,"bottom_center"))))
        self.tracks={k:v for k,v in self.tracks.items() if v.age<=self.max_age}
        return detections, list(self.tracks.values())
