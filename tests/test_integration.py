"""
Integration tests for complete workflow
"""
import pytest
import csv
from pathlib import Path
from app.services.video_metadata_service import VideoMetadataService
from app.services.csv_export_service import CsvExportService


class TestIntegration:
    """Integration tests for end-to-end workflows"""
    
    def test_complete_srt_to_csv_workflow(self, sample_srt_path, tmp_path):
        """Test complete workflow from SRT file to CSV export"""
        # Step 1: Extract metadata from SRT
        metadata_service = VideoMetadataService()
        frames = metadata_service.extract_from_video(sample_srt_path)
        
        assert len(frames) > 0
        
        # Step 2: Export to CSV
        csv_path = tmp_path / "output.csv"
        export_service = CsvExportService()
        export_service.export(frames, csv_path)
        
        # Step 3: Verify CSV output
        assert csv_path.exists()
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            csv_rows = list(reader)
        
        # Verify data integrity
        assert len(csv_rows) == len(frames)
        
        for i, (csv_row, frame) in enumerate(zip(csv_rows, frames)):
            assert csv_row["VIDEO NAME"] == frame.video_name
            assert float(csv_row["ALTITUDE"]) == pytest.approx(frame.altitude)
            assert float(csv_row["LONGITUDE"]) == pytest.approx(frame.longitude)
            assert float(csv_row["LATITUDE"]) == pytest.approx(frame.latitude)
            assert csv_row["TIME"] == frame.time
            assert csv_row["DATE"] == frame.date
    
    def test_empty_srt_workflow(self, empty_srt_path, tmp_path):
        """Test workflow with empty SRT file"""
        metadata_service = VideoMetadataService()
        frames = metadata_service.extract_from_video(empty_srt_path)
        
        assert len(frames) == 0
        
        # Should not be able to export empty frames
        csv_path = tmp_path / "output.csv"
        export_service = CsvExportService()
        
        with pytest.raises(ValueError):
            export_service.export(frames, csv_path)
    
    def test_invalid_srt_workflow(self, invalid_srt_path, tmp_path):
        """Test workflow with invalid SRT (no GPS data)"""
        metadata_service = VideoMetadataService()
        frames = metadata_service.extract_from_video(invalid_srt_path)
        
        # No GPS data means no frames extracted
        assert len(frames) == 0
        
        # Should not be able to export
        csv_path = tmp_path / "output.csv"
        export_service = CsvExportService()
        
        with pytest.raises(ValueError):
            export_service.export(frames, csv_path)
    
    def test_multiple_exports_same_file(self, sample_srt_path, tmp_path):
        """Test exporting to the same file multiple times"""
        metadata_service = VideoMetadataService()
        export_service = CsvExportService()
        csv_path = tmp_path / "output.csv"
        
        # First export
        frames1 = metadata_service.extract_from_video(sample_srt_path)
        export_service.export(frames1, csv_path)
        
        first_size = csv_path.stat().st_size
        
        # Second export (should overwrite)
        frames2 = metadata_service.extract_from_video(sample_srt_path)
        export_service.export(frames2, csv_path)
        
        second_size = csv_path.stat().st_size
        
        # File should be overwritten with same data
        assert first_size == second_size
        
        # Verify content is still valid
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        assert len(rows) == len(frames2)
