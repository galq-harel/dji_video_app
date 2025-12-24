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
        """המרת מילישניות לפורמט HH:MM:SS,mmm"""
        total_seconds = ms // 1000
        milliseconds = ms % 1000
        seconds = total_seconds % 60
        total_minutes = total_seconds // 60
        minutes = total_minutes % 60
        hours = total_minutes // 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"
    
    def _extract_float(self, pattern: re.Pattern, text: str) -> Optional[float]:
        """חילוץ ערך float מטקסט עם regex"""
        match = pattern.search(text)
        return float(match.group(1)) if match else None
    
    def _extract_string(self, pattern: re.Pattern, text: str) -> Optional[str]:
        """חילוץ string מטקסט עם regex"""
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
        
        # שם הסרטון מהנתיב
        video_name = srt_path.stem  # שם הקובץ ללא סיומת
        
        i = 0
        while i < len(lines):
            # חיפוש timecode
            time_match = self.TIME_RE.search(lines[i])
            if not time_match:
                i += 1
                continue

            h, m, s, ms = map(int, time_match.groups())

            # קריאת הבלוק הבא (עד 12 שורות)
            block_text = "".join(lines[i:i + 12])

            # חילוץ GPS
            latitude = self._extract_float(self.LAT_RE, block_text)
            longitude = self._extract_float(self.LON_RE, block_text)
            altitude = self._extract_float(self.ABS_ALT_RE, block_text)
            
            # אם אין GPS, דלג על הפריים
            if latitude is None or longitude is None:
                i += 1
                continue

            # חילוץ תאריך
            date_str = self._extract_string(self.DATE_RE, block_text)
            date_only = date_str.split()[0] if date_str else ""
            
            # חישוב TIME
            timestamp_ms = ((h * 60 + m) * 60 + s) * 1000 + ms
            time_str = self._ms_to_hms(timestamp_ms)

            # יצירת אובייקט עם כל המטאדאטה
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
            
            # לוג כל 1000 פריימים
            if len(frames) % 1000 == 0:
                logger.info(f"חולצו {len(frames)} פריימים עד כה...")

        logger.info(f"סיים חילוץ: {len(frames)} פריימים בסך הכל")
        return frames
