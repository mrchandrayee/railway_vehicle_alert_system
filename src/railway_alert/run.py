import argparse
from pathlib import Path
import cv2
from .config import load_config,parse_source
from .pipeline import RailwayAlertPipeline

def main():
    parser=argparse.ArgumentParser(description="Railway vehicle zone intrusion alert")
    parser.add_argument("--config",default="configs/railway_alert.yaml")
    parser.add_argument("--source",default=None,help="video path, webcam index, or RTSP URL")
    parser.add_argument("--output",default=None)
    parser.add_argument("--no-show",action="store_true")
    args=parser.parse_args()
    cfg=load_config(args.config); cam=cfg.get("camera",{})
    source=parse_source(args.source if args.source is not None else cam.get("source","0"))
    output=args.output or cam.get("output","runs/annotated_railway.mp4")
    show=bool(cam.get("show",True)) and not args.no_show
    cap=cv2.VideoCapture(source)
    if not cap.isOpened(): raise SystemExit(f"Could not open input: {source}")
    ok,first=cap.read()
    if not ok: raise SystemExit("Input opened but no frame could be read")
    max_width=int(cam.get("resize_width",960))
    scale=min(1.0,max_width/first.shape[1]) if max_width>0 else 1.0
    size=(int(first.shape[1]*scale),int(first.shape[0]*scale))
    first=cv2.resize(first,size) if scale!=1 else first
    fps=cap.get(cv2.CAP_PROP_FPS)
    if not 1<=fps<=120: fps=25.0
    pipeline=RailwayAlertPipeline(cfg,*size,fps)
    Path(output).parent.mkdir(parents=True,exist_ok=True)
    writer=cv2.VideoWriter(output,cv2.VideoWriter_fourcc(*"mp4v"),fps,size)
    frame=first
    try:
        while True:
            rendered,_=pipeline.process(frame)
            writer.write(rendered)
            if show:
                cv2.imshow("Railway Vehicle Alert - q to quit",rendered)
                if cv2.waitKey(1)&0xFF==ord("q"): break
            ok,raw=cap.read()
            if not ok: break
            frame=cv2.resize(raw,size) if scale!=1 else raw
    finally:
        cap.release(); writer.release()
        if show: cv2.destroyAllWindows()
    print("Annotated video:",output)
    print("Total alerts:",pipeline.event_count)
    print("Event records:",Path(cfg.get("events",{}).get("directory","runs/events"))/"events.jsonl")

if __name__=="__main__": main()
