import re
from pathlib import Path
from typing import List, Dict

from app.models.video_frame_metadata import VideoFrameMetadata


class VideoMetadataService:
    # --- Regex ---
    TIME_RE = re.compile(r"(\d+):(\d+):(\d+),(\d+)")
    FRAME_RE = re.compile(r"FrameCnt:\s*(\d+)")

    LAT_RE = re.compile(r"\[latitude:\s*([-\d.]+)\]")
    LON_RE = re.compile(r"\[longitude:\s*([-\d.]+)\]")
    REL_ALT_RE = re.compile(r"\[rel_alt:\s*([-\d.]+)")
    ABS_ALT_RE = re.compile(r"abs_alt:\s*([-\d.]+)")

    @staticmethod
    def _ms_to_hms(ms: int) -> str:
        total_seconds = ms // 1000
        milliseconds = ms % 1000
        seconds = total_seconds % 60
        total_minutes = total_seconds // 60
        minutes = total_minutes % 60
        hours = total_minutes // 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"

    def extract_from_video(self, video_path: Path) -> List[VideoFrameMetadata]:
        srt_path = video_path.with_suffix(".SRT")

        if not srt_path.exists():
            raise FileNotFoundError(f"SRT not found: {srt_path}")

        with srt_path.open("r", encoding="utf-8") as f:
            lines = f.readlines()

        per_minute: Dict[int, VideoFrameMetadata] = {}

        for i in range(len(lines)):
            # --- Timecode ---
            time_match = self.TIME_RE.search(lines[i])
            if not time_match:
                continue

            h, m, s, ms = map(int, time_match.groups())
            minute = h * 60 + m

            # פריים ראשון בלבד לכל דקה
            if minute in per_minute:
                continue

            block_text = "".join(lines[i:i + 8])

            lat_match = self.LAT_RE.search(block_text)
            lon_match = self.LON_RE.search(block_text)
            if not lat_match or not lon_match:
                continue

            frame_match = self.FRAME_RE.search(block_text)
            frame_index = int(frame_match.group(1)) if frame_match else 0

            timestamp_ms = ((h * 60 + m) * 60 + s) * 1000 + ms
            timestamp_hms = self._ms_to_hms(timestamp_ms)

            rel_alt = float(self.REL_ALT_RE.search(block_text).group(1)) if self.REL_ALT_RE.search(block_text) else None
            abs_alt = float(self.ABS_ALT_RE.search(block_text).group(1)) if self.ABS_ALT_RE.search(block_text) else None

            per_minute[minute] = VideoFrameMetadata(
                frame_index=frame_index,
                timestamp_ms=timestamp_ms,
                timestamp_hms=timestamp_hms,
                minute=minute,
                latitude=float(lat_match.group(1)),
                longitude=float(lon_match.group(1)),
                rel_alt=rel_alt,
                abs_alt=abs_alt,
            )

        return list(per_minute.values())
