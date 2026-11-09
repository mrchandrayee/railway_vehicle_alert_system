from dataclasses import dataclass, field
from typing import Tuple

@dataclass
class Detection:
    bbox: Tuple[float,float,float,float]
    confidence: float
    class_id: int
    class_name: str
    track_id: int = -1

@dataclass
class Track:
    track_id: int
    bbox: Tuple[float,float,float,float]
    class_id: int
    class_name: str
    confidence: float
    age: int = 0
    trail: list = field(default_factory=list)

@dataclass
class ZoneEvent:
    event_type: str
    track_id: int
    class_name: str
    confidence: float
    bbox: tuple
    anchor: tuple
    frame_index: int
