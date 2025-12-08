from pathlib import Path
from typing import List

from app.models.video_frame_metadata import VideoFrameMetadata


class VideoMetadataService:
    """
    אחראי לחילוץ מידע מסרטון DJI.
    בשלב הבא נממש כאן:
    - קריאה ל-exiftool או קבצי SRT
    - פרסינג של הטלמטריה
    """

    def extract_from_video(self, video_path: Path) -> List[VideoFrameMetadata]:
        # TODO: מימוש אמיתי
        raise NotImplementedError("Video metadata extraction is not implemented yet.")
