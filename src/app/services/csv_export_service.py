from pathlib import Path
from typing import Sequence
import logging

import pandas as pd

from app.models.video_frame_metadata import VideoFrameMetadata

logger = logging.getLogger(__name__)


class CsvExportService:
    def export(self, frames: Sequence[VideoFrameMetadata], output_path: Path) -> None:
        logger.info(f"Starting CSV export: {len(frames)} frames")
        
        if not frames:
            logger.error("No frames to export")
            raise ValueError("No frames to export")

        logger.info("Converting frames to DataFrame")
        # Use by_alias=True to get correct column names (UPPERCASE)
        df = pd.DataFrame([f.model_dump(by_alias=True) for f in frames])

        logger.info(f"Saving CSV to file: {output_path}")
        df.to_csv(output_path, index=False)
        logger.info(f"CSV file saved successfully: {output_path}")
