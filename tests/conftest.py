"""
Pytest configuration and shared fixtures
"""
import pytest
from pathlib import Path
from typing import List
from app.models.video_frame_metadata import VideoFrameMetadata


@pytest.fixture
def sample_srt_path(tmp_path: Path) -> Path:
    """Create a temporary sample SRT file for testing"""
    srt_content = """1
00:00:00,000 --> 00:00:00,033
<font size="28">FrameCnt: 1, DiffTime: 33ms
2024-12-22 15:08:01.000
[latitude: 31.123456] [longitude: 34.567890] [rel_alt: 50.000 abs_alt: 150.000] 
</font>

2
00:00:00,033 --> 00:00:00,066
<font size="28">FrameCnt: 2, DiffTime: 33ms
2024-12-22 15:08:01.033
[latitude: 31.123457] [longitude: 34.567891] [rel_alt: 50.100 abs_alt: 150.100] 
</font>

3
00:00:00,066 --> 00:00:00,099
<font size="28">FrameCnt: 3, DiffTime: 33ms
2024-12-22 15:08:01.066
[latitude: 31.123458] [longitude: 34.567892] [rel_alt: 50.200 abs_alt: 150.200] 
</font>
"""
    srt_file = tmp_path / "test_video.SRT"
    srt_file.write_text(srt_content, encoding="utf-8")
    return srt_file


@pytest.fixture
def empty_srt_path(tmp_path: Path) -> Path:
    """Create an empty SRT file for testing error handling"""
    srt_file = tmp_path / "empty.SRT"
    srt_file.write_text("", encoding="utf-8")
    return srt_file


@pytest.fixture
def invalid_srt_path(tmp_path: Path) -> Path:
    """Create an invalid SRT file (no GPS data) for testing"""
    srt_content = """1
00:00:00,000 --> 00:00:00,033
No GPS data here
"""
    srt_file = tmp_path / "invalid.SRT"
    srt_file.write_text(srt_content, encoding="utf-8")
    return srt_file


@pytest.fixture
def sample_frames() -> List[VideoFrameMetadata]:
    """Create sample video frame metadata for testing"""
    return [
        VideoFrameMetadata(
            comments="",
            video_name="test_video",
            altitude=150.0,
            longitude=34.567890,
            latitude=31.123456,
            time="00:00:00:000",
            date="2024-12-22"
        ),
        VideoFrameMetadata(
            comments="",
            video_name="test_video",
            altitude=150.1,
            longitude=34.567891,
            latitude=31.123457,
            time="00:00:00:033",
            date="2024-12-22"
        ),
        VideoFrameMetadata(
            comments="",
            video_name="test_video",
            altitude=150.2,
            longitude=34.567892,
            latitude=31.123458,
            time="00:00:00:066",
            date="2024-12-22"
        ),
    ]


@pytest.fixture
def csv_output_path(tmp_path: Path) -> Path:
    """Create a temporary CSV output path for testing"""
    return tmp_path / "output.csv"
