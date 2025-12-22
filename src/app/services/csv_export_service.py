from pathlib import Path
from typing import Sequence

import pandas as pd

from app.models.video_frame_metadata import VideoFrameMetadata


class CsvExportService:
    def export(self, frames: Sequence[VideoFrameMetadata], output_path: Path) -> None:
        if not frames:
            raise ValueError("No frames to export")

        df = pd.DataFrame([f.model_dump() for f in frames])

        # מיון בטוח לפי עמודה קיימת
        if "timestamp_ms" in df.columns:
            df.sort_values("timestamp_ms", inplace=True)
        elif "frame_index" in df.columns:
            df.sort_values("frame_index", inplace=True)

        df.to_csv(output_path, index=False)
