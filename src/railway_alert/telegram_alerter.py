import os
from pathlib import Path
import requests
import cv2

class TelegramAlerter:
    def __init__(self,cfg):
        self.enabled=bool(cfg.get("enabled",False))
        self.token=os.getenv("TELEGRAM_BOT_TOKEN") or cfg.get("bot_token","")
        self.chat_id=os.getenv("TELEGRAM_CHAT_ID") or cfg.get("chat_id","")
        self.send_photo_enabled=bool(cfg.get("send_photo",True))
        self.send_clip=bool(cfg.get("send_clip",True))
        self.jpeg_quality=int(cfg.get("photo_jpeg_quality",82))
        self.max_kb=int(cfg.get("photo_max_kb",900))

    def _request(self,method,data,files=None):
        if not self.enabled: return None
        if not self.token or not self.chat_id:
            raise RuntimeError("Telegram is enabled but bot token/chat ID is missing")
        url=f"https://api.telegram.org/bot{self.token}/{method}"
        response=requests.post(url,data=data,files=files,timeout=60)
        response.raise_for_status()
        payload=response.json()
        if not payload.get("ok"): raise RuntimeError(str(payload))
        return payload

    def send_text(self,text):
        if self.enabled:
            self._request("sendMessage",{"chat_id":self.chat_id,"text":text})

    def send_photo(self,path,caption):
        if not self.enabled or not self.send_photo_enabled: return
        path=Path(path)
        if not path.exists(): return
        # Re-encode a bounded JPEG for Telegram's photo upload limit.
        image=cv2.imread(str(path))
        if image is not None:
            quality=self.jpeg_quality
            while quality>=45:
                ok,buf=cv2.imencode(".jpg",image,[cv2.IMWRITE_JPEG_QUALITY,quality])
                if ok and len(buf)<=self.max_kb*1024: break
                quality-=7
            if ok:
                self._request("sendPhoto",{"chat_id":self.chat_id,"caption":caption},
                              {"photo":("alert.jpg",buf.tobytes(),"image/jpeg")})
                return
        with path.open("rb") as f:
            self._request("sendPhoto",{"chat_id":self.chat_id,"caption":caption},
                          {"photo":(path.name,f,"image/jpeg")})

    def send_video(self,path,caption="Railway vehicle intrusion clip"):
        if not self.enabled or not self.send_clip or not path or not Path(path).exists(): return
        with Path(path).open("rb") as f:
            self._request("sendVideo",{"chat_id":self.chat_id,"caption":caption},
                          {"video":(Path(path).name,f,"video/mp4")})
