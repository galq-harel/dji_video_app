"""
Tests for CsvExportService
"""
import pytest
import csv
from pathlib import Path
from app.services.csv_export_service import CsvExportService


class TestCsvExportService:
    """Test cases for CsvExportService"""
    
    @pytest.fixture
    def service(self):
        """Create a CsvExportService instance"""
        return CsvExportService()
    
    def test_export_valid_frames(self, service, sample_frames, csv_output_path):
        """Test exporting valid frames to CSV"""
        service.export(sample_frames, csv_output_path)
        
        # Check file exists
        assert csv_output_path.exists()
        
        # Read and verify CSV content
        with open(csv_output_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        # Check number of rows
        assert len(rows) == 3
        
        # Check column names (should be uppercase aliases)
        expected_columns = ["COMMENTS", "VIDEO NAME", "ALTITUDE", "LONGITUDE", "LATITUDE", "TIME", "DATE"]
        assert list(rows[0].keys()) == expected_columns
        
        # Check first row values
        assert rows[0]["VIDEO NAME"] == "test_video"
        assert float(rows[0]["ALTITUDE"]) == pytest.approx(150.0)
        assert float(rows[0]["LONGITUDE"]) == pytest.approx(34.567890)
        assert float(rows[0]["LATITUDE"]) == pytest.approx(31.123456)
        assert rows[0]["TIME"] == "00:00:00:000"
        assert rows[0]["DATE"] == "2024-12-22"
    
    def test_export_empty_list_raises_error(self, service, csv_output_path):
        """Test that exporting empty list raises ValueError"""
        with pytest.raises(ValueError, match="No frames to export"):
            service.export([], csv_output_path)
    
    def test_export_to_nonexistent_directory(self, service, sample_frames, tmp_path):
        """Test that exporting to nonexistent directory raises error"""
        nonexistent_dir = tmp_path / "nonexistent" / "output.csv"
        
        with pytest.raises(OSError):
            service.export(sample_frames, nonexistent_dir)
    
    def test_export_overwrites_existing_file(self, service, sample_frames, csv_output_path):
        """Test that export overwrites existing CSV file"""
        # Create initial file
        csv_output_path.write_text("old content", encoding="utf-8")
        
        # Export new data
        service.export(sample_frames, csv_output_path)
        
        # Read and verify new content
        with open(csv_output_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        assert len(rows) == 3
        assert "old content" not in csv_output_path.read_text()
    
    def test_export_with_none_values(self, service, csv_output_path):
        """Test exporting frames with None values"""
        from app.models.video_frame_metadata import VideoFrameMetadata
        
        frames = [
            VideoFrameMetadata(
                video_name="test",
                altitude=None,
                longitude=None,
                latitude=None
            )
        ]
        
        service.export(frames, csv_output_path)
        
        # Read CSV
        with open(csv_output_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        # None values should be empty strings in CSV
        assert rows[0]["ALTITUDE"] == ""
        assert rows[0]["LONGITUDE"] == ""
        assert rows[0]["LATITUDE"] == ""
    
    def test_csv_format_matches_expected(self, service, sample_frames, csv_output_path):
        """Test that CSV format matches expected structure"""
        service.export(sample_frames, csv_output_path)
        
        # Read raw CSV content
        content = csv_output_path.read_text(encoding='utf-8')
        lines = content.strip().split('\n')
        
        # Check header
        assert lines[0] == "COMMENTS,VIDEO NAME,ALTITUDE,LONGITUDE,LATITUDE,TIME,DATE"
        
        # Check first data row format
        first_row = lines[1].split(',')
        assert len(first_row) == 7
        assert first_row[1] == "test_video"
