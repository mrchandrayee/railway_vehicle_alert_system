from .geometry import parse_points, anchor_point, point_in_polygon
from .models import ZoneEvent

class ZoneMonitor:
    def __init__(self,cfg,width,height):
        self.name=cfg.get("name","restricted_zone")
        self.polygon=parse_points(cfg["polygon"],width,height)
        self.anchor_mode=cfg.get("anchor","bottom_center")
        self.trigger=cfg.get("trigger","enter")
        self.min_inside_frames=max(1,int(cfg.get("min_inside_frames",1)))
        self.min_confidence=float(cfg.get("min_confidence",0))
        self.inside_frames={}; self.states={}

    def update(self,tracks,frame_index):
        events=[]
        for tr in tracks:
            tid=tr.track_id
            if tr.confidence < self.min_confidence: continue
            anchor=anchor_point(tr.bbox,self.anchor_mode)
            inside=point_in_polygon(anchor,self.polygon)
            self.inside_frames[tid]=self.inside_frames.get(tid,0)+1 if inside else 0
            stable_inside=inside and self.inside_frames[tid]>=self.min_inside_frames
            was_inside=self.states.get(tid,False)
            if stable_inside and not was_inside:
                if self.trigger in ("enter","both"):
                    events.append(ZoneEvent("intrusion_enter",tid,tr.class_name,tr.confidence,tr.bbox,anchor,frame_index))
                self.states[tid]=True
            elif not inside and was_inside:
                if self.trigger in ("exit","both"):
                    events.append(ZoneEvent("intrusion_exit",tid,tr.class_name,tr.confidence,tr.bbox,anchor,frame_index))
                self.states[tid]=False
        active={t.track_id for t in tracks}
        # Keep recently missing tracks until tracker expires; clean up once absent for longer.
        for tid in list(self.states):
            if tid not in active:
                self.states.pop(tid,None); self.inside_frames.pop(tid,None)
        return events
