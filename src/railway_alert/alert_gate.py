import time
from collections import defaultdict

class AlertGate:
    def __init__(self,cooldown_seconds=30,per_track=True):
        self.cooldown=float(cooldown_seconds); self.per_track=bool(per_track)
        self.last_global=0.0; self.last_track=defaultdict(float); self.armed=True

    def allow(self,track_id=None,now=None):
        if not self.armed: return False
        now=time.time() if now is None else float(now)
        if self.per_track and track_id is not None:
            if now-self.last_track[track_id] < self.cooldown: return False
            self.last_track[track_id]=now
            return True
        if now-self.last_global < self.cooldown: return False
        self.last_global=now
        return True
