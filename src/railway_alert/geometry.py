import cv2
import numpy as np

def parse_points(points, width, height):
    return np.asarray([[int(round(float(x)*width)), int(round(float(y)*height))]
                       for x,y in points], dtype=np.int32)

def anchor_point(box, mode="bottom_center"):
    x1,y1,x2,y2=map(float,box)
    if mode=="center":
        return ((x1+x2)/2,(y1+y2)/2)
    return ((x1+x2)/2,y2)

def point_in_polygon(point, polygon):
    return cv2.pointPolygonTest(np.asarray(polygon,np.int32),
                                (float(point[0]),float(point[1])),False)>=0

def box_iou(a,b):
    ax1,ay1,ax2,ay2=a; bx1,by1,bx2,by2=b
    x1,y1,x2,y2=max(ax1,bx1),max(ay1,by1),min(ax2,bx2),min(ay2,by2)
    inter=max(0,x2-x1)*max(0,y2-y1)
    aa=max(0,ax2-ax1)*max(0,ay2-ay1)
    bb=max(0,bx2-bx1)*max(0,by2-by1)
    return inter/max(1e-9,aa+bb-inter)

def crop_object(frame, box, padding=0.08):
    h,w=frame.shape[:2]
    x1,y1,x2,y2=map(float,box)
    dx=(x2-x1)*padding; dy=(y2-y1)*padding
    x1=max(0,int(x1-dx)); y1=max(0,int(y1-dy))
    x2=min(w,int(x2+dx)); y2=min(h,int(y2+dy))
    if x2<=x1 or y2<=y1:
        return frame.copy()
    return frame[y1:y2,x1:x2].copy()
