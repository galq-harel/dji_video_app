from pathlib import Path

from app.services.video_metadata_service import VideoMetadataService
from app.services.csv_export_service import CsvExportService


def main():
    project_root = Path(__file__).resolve().parent.parent

    video_dir = project_root / "DJI_202512221456_005"
    video_path = video_dir / "DJI_20251222150801_0005_S.MP4"



    metadata_service = VideoMetadataService()
    frames = metadata_service.extract_from_video(video_path)

    exporter = CsvExportService()
    exporter.export(frames, Path("video_gps_per_minute.csv"))

    print("✔ CSV נוצר בהצלחה")


if __name__ == "__main__":
    main()
