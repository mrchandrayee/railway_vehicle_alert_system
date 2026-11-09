import cv2

def draw_overlay_text(frame,text,xy,color=(245,245,245),scale=.55):
    cv2.putText(frame,str(text),tuple(map(int,xy)),cv2.FONT_HERSHEY_SIMPLEX,
                scale,color,2,cv2.LINE_AA)

def draw_tracks(frame,tracks,show_labels=True,show_trails=True):
    for tr in tracks:
        x1,y1,x2,y2=map(int,tr.bbox)
        cv2.rectangle(frame,(x1,y1),(x2,y2),(255,70,220),2)
        if show_labels:
            draw_overlay_text(frame,f"{tr.class_name} #{tr.track_id} {tr.confidence:.2f}",
                              (x1,max(18,y1-6)),(255,110,220),.43)
        if show_trails and len(tr.trail)>1:
            pts=list(tr.trail)
            for a,b in zip(pts[:-1],pts[1:]):
                cv2.line(frame,a,b,(0,220,255),2,cv2.LINE_AA)
    return frame

def draw_zone(frame,polygon,name):
    overlay=frame.copy()
    cv2.fillPoly(overlay,[polygon],(20,30,230))
    cv2.addWeighted(overlay,.17,frame,.83,0,frame)
    cv2.polylines(frame,[polygon],True,(30,30,255),2,cv2.LINE_AA)
    x,y=polygon[0]
    draw_overlay_text(frame,name,(int(x),max(20,int(y)-8)),(80,80,255),.5)
    return frame

def draw_dashboard(frame,camera_id,track_count,events_count,armed=True):
    text=f"RAILWAY VEHICLE ALERT | {camera_id} | Tracks: {track_count} | Events: {events_count} | {'ARMED' if armed else 'DISARMED'}"
    cv2.rectangle(frame,(6,6),(min(frame.shape[1]-6,frame.shape[1]-6),38),(18,18,28),-1)
    draw_overlay_text(frame,text,(13,29),(245,245,245),.43)
    return frame
