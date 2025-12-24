from pathlib import Path
from typing import Sequence
import logging

import pandas as pd

from app.models.video_frame_metadata import VideoFrameMetadata

logger = logging.getLogger(__name__)


class CsvExportService:
    def export(self, frames: Sequence[VideoFrameMetadata], output_path: Path) -> None:
        logger.info(f"מתחיל יצוא CSV: {len(frames)} פריימים")
        
        if not frames:
            logger.error("אין פריימים ליצוא")
            raise ValueError("No frames to export")

        logger.info("ממיר פריימים ל-DataFrame")
        # שימוש ב-by_alias=True כדי לקבל את שמות העמודות הנכונים (UPPERCASE)
        df = pd.DataFrame([f.model_dump(by_alias=True) for f in frames])

        logger.info(f"שומר CSV לקובץ: {output_path}")
        df.to_csv(output_path, index=False)
        logger.info(f"קובץ CSV נשמר בהצלחה: {output_path}")
