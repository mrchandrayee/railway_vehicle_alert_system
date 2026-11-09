from pathlib import Path
from .detector import VehicleDetector
from .tracker import IoUTracker
from .zone import ZoneMonitor
from .alert_gate import AlertGate
from .event_store import EventStore
from .clip_exporter import PacketClipExporter
from .telegram_alerter import TelegramAlerter
from .geometry import crop_object
from .visualization import draw_tracks,draw_zone,draw_dashboard

class RailwayAlertPipeline:
    def __init__(self,cfg,width,height,fps):
        d=cfg.get("detector",{}); t=cfg.get("tracker",{}); z=cfg.get("zone",{})
        self.detector=VehicleDetector(d.get("model","yolo11n.pt"),d.get("confidence",.3),
                                      d.get("iou",.5),d.get("classes",[2,3,5,7]),d.get("device"))
        self.tracker=IoUTracker(t.get("max_age",35),t.get("match_iou",.18),
                                t.get("trail_length",24),t.get("anchor","bottom"))
        self.zone=ZoneMonitor(z,width,height)
        e=cfg.get("events",{}); tg=cfg.get("telegram",{})
        self.store=EventStore(e.get("directory","runs/events"))
        self.clips=PacketClipExporter(fps,(width,height),e.get("directory","runs/events"),
                                      e.get("pre_seconds",3),e.get("post_seconds",5),
                                      e.get("max_clip_seconds",20))
        self.alerter=TelegramAlerter(tg)
        self.gate=AlertGate(tg.get("alert_cooldown_s",30),tg.get("per_track_cooldown",True))
        self.camera_id=cfg.get("camera",{}).get("camera_id","railway_cam")
        self.save_snapshot=e.get("save_snapshot",True)
        self.crop_padding=float(e.get("crop_padding",.08))
        vis=cfg.get("visualization",{})
        self.show_labels=vis.get("draw_labels",True); self.show_trails=vis.get("draw_trails",True)
        self.frame_index=0; self.event_count=0
        self.pending_event_records={}

    def process(self,frame):
        detections=self.detector.detect(frame)
        _,tracks=self.tracker.update(detections)
        events=self.zone.update(tracks,self.frame_index)
        completed_clips=self.clips.push(frame)
        # Send any clips whose post-event window has just completed.
        for clip_path in completed_clips:
            try: self.alerter.send_video(clip_path)
            except Exception as exc: print(f"Telegram clip upload failed: {exc}")

        rendered=frame.copy()
        draw_zone(rendered,self.zone.polygon,self.zone.name)
        draw_tracks(rendered,tracks,self.show_labels,self.show_trails)
        for event in events:
            if not self.gate.allow(event.track_id): continue
            self.event_count+=1
            event_id=f"{self.camera_id}_{event.event_type}_track{event.track_id}_frame{self.frame_index}"
            snapshot=None
            if self.save_snapshot:
                # Snapshot includes full scene; crop helper is used for optional target crop asset.
                snapshot=self.store.save_snapshot(event_id,rendered)
                crop=crop_object(frame,event.bbox,self.crop_padding)
                import cv2
                cv2.imwrite(str(self.store.directory/f"{event_id}_crop.jpg"),crop)
            clip_path=self.clips.on_enter(event.track_id) if event.event_type=="intrusion_enter" else self.clips.on_leave(event.track_id)
            record=self.store.append(event,self.camera_id,snapshot,clip_path)
            caption=(f"🚨 RAILWAY VEHICLE ALERT\nEvent: {event.event_type}\n"
                     f"Camera: {self.camera_id}\nObject: {event.class_name}\n"
                     f"Track ID: {event.track_id}\nConfidence: {event.confidence:.2f}")
            try:
                if snapshot: self.alerter.send_photo(snapshot,caption)
                else: self.alerter.send_text(caption)
                if clip_path: self.alerter.send_video(clip_path)
            except Exception as exc:
                print(f"Telegram alert failed: {exc}")
            print(f"[ALERT] {record}")
        draw_dashboard(rendered,self.camera_id,len(tracks),self.event_count,self.gate.armed)
        self.frame_index+=1
        return rendered,events
