from pydantic import BaseModel
from typing import Optional


class VideoFrameMetadata(BaseModel):
    frame_index: int
    timestamp_ms: int

    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude_m: Optional[float] = None

    drone_yaw_deg: Optional[float] = None
    drone_pitch_deg: Optional[float] = None
    drone_roll_deg: Optional[float] = None

    gimbal_yaw_deg: Optional[float] = None
    gimbal_pitch_deg: Optional[float] = None
    gimbal_roll_deg: Optional[float] = None
