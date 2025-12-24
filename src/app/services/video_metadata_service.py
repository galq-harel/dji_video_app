import re
from pathlib import Path
from typing import List, Optional
import logging

from app.models.video_frame_metadata import VideoFrameMetadata

logger = logging.getLogger(__name__)


class VideoMetadataService:
    # --- Regex patterns ---
    TIME_RE = re.compile(r"(\d+):(\d+):(\d+),(\d+)")
    DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+)")
    
    # GPS
    LAT_RE = re.compile(r"\[latitude:\s*([-\d.]+)\]")
    LON_RE = re.compile(r"\[longitude:\s*([-\d.]+)\]")
    ABS_ALT_RE = re.compile(r"abs_alt:\s*([-\d.]+)")

    @staticmethod
    def _ms_to_hms(ms: int) -> str:
        """Convert milliseconds to HH:MM:SS,mmm format"""
        total_seconds = ms // 1000
        milliseconds = ms % 1000
        seconds = total_seconds % 60
        total_minutes = total_seconds // 60
        minutes = total_minutes % 60
        hours = total_minutes // 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"
    
    def _extract_float(self, pattern: re.Pattern, text: str) -> Optional[float]:
        """Extract float value from text using regex"""
        match = pattern.search(text)
        return float(match.group(1)) if match else None
    
    def _extract_string(self, pattern: re.Pattern, text: str) -> Optional[str]:
        """Extract string from text using regex"""
        match = pattern.search(text)
        return match.group(1) if match else None

    def extract_from_video(self, video_path: Path) -> List[VideoFrameMetadata]:
        logger.info(f"מתחיל חילוץ מטאדאטה מ: {video_path}")
        srt_path = video_path.with_suffix(".SRT")

        if not srt_path.exists():
            logger.error(f"קובץ SRT לא נמצא: {srt_path}")
            raise FileNotFoundError(f"SRT not found: {srt_path}")

        logger.info(f"קורא קובץ SRT: {srt_path}")
        with srt_path.open("r", encoding="utf-8") as f:
            lines = f.readlines()

        logger.info(f"נקראו {len(lines)} שורות מקובץ SRT")
        frames: List[VideoFrameMetadata] = []
        
        # Extract video name from path
        video_name = srt_path.stem
        
        i = 0
        while i < len(lines):
            # Search for timecode
            time_match = self.TIME_RE.search(lines[i])
            if not time_match:
                i += 1
                continue

            h, m, s, ms = map(int, time_match.groups())

            # Read next block (up to 12 lines)
            block_text = "".join(lines[i:i + 12])

            # Extract GPS data
            latitude = self._extract_float(self.LAT_RE, block_text)
            longitude = self._extract_float(self.LON_RE, block_text)
            altitude = self._extract_float(self.ABS_ALT_RE, block_text)
            
            # Skip frame if no GPS data
            if latitude is None or longitude is None:
                i += 1
                continue

            # Extract date
            date_str = self._extract_string(self.DATE_RE, block_text)
            date_only = date_str.split()[0] if date_str else ""
            
            # Calculate TIME
            timestamp_ms = ((h * 60 + m) * 60 + s) * 1000 + ms
            time_str = self._ms_to_hms(timestamp_ms)

            # Create object with all metadata
            frame = VideoFrameMetadata(
                comments="",
                video_name=video_name,
                altitude=altitude,
                longitude=longitude,
                latitude=latitude,
                time=time_str,
                date=date_only,
            )
            
            frames.append(frame)
            i += 1
            
            # Log every 1000 frames
            if len(frames) % 1000 == 0:
                logger.info(f"חולצו {len(frames)} פריימים עד כה...")

        logger.info(f"סיים חילוץ: {len(frames)} פריימים בסך הכל")
        return frames
