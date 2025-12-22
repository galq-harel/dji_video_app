from typing import Optional
from pydantic import BaseModel


class VideoFrameMetadata(BaseModel):
    frame_index: int
    timestamp_ms: int
    timestamp_hms: str
    minute: int

    latitude: Optional[float] = None
    longitude: Optional[float] = None

    rel_alt: Optional[float] = None
    abs_alt: Optional[float] = None

    drone_yaw_deg: Optional[float] = None
    drone_pitch_deg: Optional[float] = None
    drone_roll_deg: Optional[float] = None

    gimbal_yaw_deg: Optional[float] = None
    gimbal_pitch_deg: Optional[float] = None
    gimbal_roll_deg: Optional[float] = None
