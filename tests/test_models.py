"""
Tests for VideoFrameMetadata model
"""
import pytest
from pydantic import ValidationError
from app.models.video_frame_metadata import VideoFrameMetadata


class TestVideoFrameMetadata:
    """Test cases for VideoFrameMetadata model"""
    
    def test_create_valid_frame(self):
        """Test creating a valid frame with all fields"""
        frame = VideoFrameMetadata(
            comments="Test comment",
            video_name="test_video",
            altitude=150.5,
            longitude=34.567890,
            latitude=31.123456,
            time="00:00:00:000",
            date="2024-12-22"
        )
        
        assert frame.comments == "Test comment"
        assert frame.video_name == "test_video"
        assert frame.altitude == 150.5
        assert frame.longitude == 34.567890
        assert frame.latitude == 31.123456
        assert frame.time == "00:00:00:000"
        assert frame.date == "2024-12-22"
    
    def test_create_frame_with_defaults(self):
        """Test creating a frame with default values"""
        frame = VideoFrameMetadata()
        
        assert frame.comments == ""
        assert frame.video_name == ""
        assert frame.altitude is None
        assert frame.longitude is None
        assert frame.latitude is None
        assert frame.time == ""
        assert frame.date == ""
    
    def test_create_frame_with_none_values(self):
        """Test creating a frame with None values for optional fields"""
        frame = VideoFrameMetadata(
            video_name="test",
            altitude=None,
            longitude=None,
            latitude=None
        )
        
        assert frame.altitude is None
        assert frame.longitude is None
        assert frame.latitude is None
    
    def test_model_dump_with_aliases(self):
        """Test model_dump returns correct column names with aliases"""
        frame = VideoFrameMetadata(
            comments="Test",
            video_name="video1",
            altitude=100.0,
            longitude=34.5,
            latitude=31.2,
            time="00:00:01:000",
            date="2024-12-22"
        )
        
        # With aliases (uppercase column names for CSV)
        data = frame.model_dump(by_alias=True)
        assert "COMMENTS" in data
        assert "VIDEO NAME" in data
        assert "ALTITUDE" in data
        assert "LONGITUDE" in data
        assert "LATITUDE" in data
        assert "TIME" in data
        assert "DATE" in data
    
    def test_model_dump_without_aliases(self):
        """Test model_dump without aliases returns lowercase names"""
        frame = VideoFrameMetadata(video_name="test")
        
        data = frame.model_dump(by_alias=False)
        assert "comments" in data
        assert "video_name" in data
        assert "altitude" in data
    
    def test_numeric_validation(self):
        """Test that numeric fields accept valid float values"""
        frame = VideoFrameMetadata(
            altitude=150.123456,
            longitude=-180.0,
            latitude=90.0
        )
        
        assert frame.altitude == 150.123456
        assert frame.longitude == -180.0
        assert frame.latitude == 90.0
    
    def test_string_fields(self):
        """Test string field handling"""
        frame = VideoFrameMetadata(
            comments="Multi\nline\ncomment",
            video_name="video_with_underscores_123",
            time="12:34:56:789",
            date="2024-12-22"
        )
        
        assert "\n" in frame.comments
        assert "_" in frame.video_name
        assert ":" in frame.time
        assert "-" in frame.date
