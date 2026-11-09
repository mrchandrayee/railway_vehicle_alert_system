from collections import deque
from pathlib import Path
import cv2
from datetime import datetime

class PacketClipExporter:
    """Retains pre-event frames and writes a clip after post-event frames arrive."""
    def __init__(self,fps,size,directory,pre_seconds=3,post_seconds=5,max_clip_seconds=20):
        self.fps=max(1.0,float(fps)); self.size=tuple(size)
        self.pre_frames=max(0,int(pre_seconds*self.fps))
        self.post_frames=max(0,int(post_seconds*self.fps))
        self.max_frames=max(1,int(max_clip_seconds*self.fps))
        self.buffer=deque(maxlen=max(1,self.pre_frames))
        self.pending={}; self.directory=Path(directory); self.directory.mkdir(parents=True,exist_ok=True)

    def push(self,frame):
        self.buffer.append(frame.copy())
        finished=[]
        for tid,job in list(self.pending.items()):
            job["frames"].append(frame.copy()); job["remaining"]-=1
            if job["remaining"]<=0 or len(job["frames"])>=self.max_frames:
                finished.append(self._write(tid,job))
                del self.pending[tid]
        return finished

    def on_enter(self,track_id):
        if track_id in self.pending: return None
        stamp=datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        job={"path":self.directory/f"track{track_id}_{stamp}.mp4",
             "frames":[f.copy() for f in self.buffer],"remaining":self.post_frames}
        if self.post_frames<=0:
            return self._write(track_id,job)
        self.pending[track_id]=job
        return None

    def on_leave(self,track_id):
        job=self.pending.pop(track_id,None)
        return self._write(track_id,job) if job else None

    def _write(self,track_id,job):
        path=job["path"]
        writer=cv2.VideoWriter(str(path),cv2.VideoWriter_fourcc(*"mp4v"),self.fps,self.size)
        for frame in job["frames"][-self.max_frames:]:
            writer.write(frame)
        writer.release()
        return path
