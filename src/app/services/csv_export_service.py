from pathlib import Path
from typing import Sequence

import pandas as pd

from app.models.video_frame_metadata import VideoFrameMetadata


class CsvExportService:
    def export(self, frames: Sequence[VideoFrameMetadata], output_path: Path) -> None:
        """
        מקבל רשימת אובייקטים של VideoFrameMetadata ושומר אותם כ-CSV.
        """
        df = pd.DataFrame([f.model_dump() for f in frames])
        df.to_csv(output_path, index=False)
