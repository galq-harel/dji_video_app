from typing import Optional
from pydantic import BaseModel, Field


class VideoFrameMetadata(BaseModel):
    comments: Optional[str] = Field(default="", alias="COMMENTS")
    video_name: Optional[str] = Field(default="", alias="VIDEO NAME")
    altitude: Optional[float] = Field(default=None, alias="ALTITUDE")
    longitude: Optional[float] = Field(default=None, alias="LONGITUDE")
    latitude: Optional[float] = Field(default=None, alias="LATITUDE")
    time: Optional[str] = Field(default="", alias="TIME")
    date: Optional[str] = Field(default="", alias="DATE")
    
    class Config:
        populate_by_name = True
