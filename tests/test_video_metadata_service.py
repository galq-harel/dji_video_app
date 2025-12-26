"""
Tests for VideoMetadataService
"""
import pytest
from pathlib import Path
from app.services.video_metadata_service import VideoMetadataService


class TestVideoMetadataService:
    """Test cases for VideoMetadataService"""
    
    @pytest.fixture
    def service(self):
        """Create a VideoMetadataService instance"""
        return VideoMetadataService()
    
    def test_extract_from_valid_srt(self, service, sample_srt_path):
        """Test extracting metadata from a valid SRT file"""
        frames = service.extract_from_video(sample_srt_path)
        
        assert len(frames) == 3
        
        # Check first frame
        assert frames[0].latitude == pytest.approx(31.123456)
        assert frames[0].longitude == pytest.approx(34.567890)
        assert frames[0].altitude == pytest.approx(150.0)
        assert frames[0].video_name == "test_video"
        assert frames[0].date == "2024-12-22"
        assert frames[0].time == "00:00:00:000"
        
        # Check second frame
        assert frames[1].latitude == pytest.approx(31.123457)
        assert frames[1].longitude == pytest.approx(34.567891)
        assert frames[1].altitude == pytest.approx(150.1)
        assert frames[1].time == "00:00:00:033"
        
        # Check third frame
        assert frames[2].latitude == pytest.approx(31.123458)
        assert frames[2].longitude == pytest.approx(34.567892)
        assert frames[2].altitude == pytest.approx(150.2)
        assert frames[2].time == "00:00:00:066"
    
    def test_extract_from_nonexistent_file(self, service, tmp_path):
        """Test that FileNotFoundError is raised for nonexistent file"""
        nonexistent = tmp_path / "nonexistent.SRT"
        
        with pytest.raises(FileNotFoundError):
            service.extract_from_video(nonexistent)
    
    def test_extract_from_invalid_srt(self, service, invalid_srt_path):
        """Test extracting from SRT with no GPS data returns empty list"""
        frames = service.extract_from_video(invalid_srt_path)
        
        assert len(frames) == 0
    
    def test_extract_from_empty_srt(self, service, empty_srt_path):
        """Test extracting from empty SRT returns empty list"""
        frames = service.extract_from_video(empty_srt_path)
        
        assert len(frames) == 0
    
    def test_ms_to_hms_conversion(self, service):
        """Test milliseconds to HH:MM:SS:mmm conversion"""
        # Test 0 ms
        assert service._ms_to_hms(0) == "00:00:00:000"
        
        # Test 1 second
        assert service._ms_to_hms(1000) == "00:00:01:000"
        
        # Test 1 minute
        assert service._ms_to_hms(60000) == "00:01:00:000"
        
        # Test 1 hour
        assert service._ms_to_hms(3600000) == "01:00:00:000"
        
        # Test complex time: 1h 23m 45s 678ms
        assert service._ms_to_hms(5025678) == "01:23:45:678"
    
    def test_extract_float_from_text(self, service):
        """Test regex float extraction"""
        import re
        
        pattern = re.compile(r"value:\s*([-\d.]+)")
        
        # Positive float
        assert service._extract_float(pattern, "value: 123.456") == pytest.approx(123.456)
        
        # Negative float
        assert service._extract_float(pattern, "value: -45.67") == pytest.approx(-45.67)
        
        # Integer
        assert service._extract_float(pattern, "value: 100") == pytest.approx(100.0)
        
        # No match
        assert service._extract_float(pattern, "no value here") is None
    
    def test_extract_string_from_text(self, service):
        """Test regex string extraction"""
        import re
        
        pattern = re.compile(r"date:\s*(\d{4}-\d{2}-\d{2})")
        
        # Valid match
        assert service._extract_string(pattern, "date: 2024-12-22") == "2024-12-22"
        
        # No match
        assert service._extract_string(pattern, "no date here") is None
    
    def test_video_name_extraction(self, service, sample_srt_path):
        """Test that video name is correctly extracted from file path"""
        frames = service.extract_from_video(sample_srt_path)
        
        # Video name should be the filename without extension
        assert frames[0].video_name == "test_video"
