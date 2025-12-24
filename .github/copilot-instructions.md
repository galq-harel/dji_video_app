# DJI Video App - AI Coding Agent Instructions

## Project Overview

This is a desktop application that extracts metadata from DJI drone videos and exports the data to CSV format. Built with **Flet** (Flutter for Python) for the UI, **Pydantic** for data validation, and **Pandas** for CSV export.

**Architecture**: Desktop GUI app with three-layer separation:
- **UI Layer** (`src/app/ui.py`): Flet components - file picker and export buttons
- **Models** (`src/app/models/`): Pydantic data classes defining video frame metadata schema
- **Services** (`src/app/services/`): Business logic for video processing and export

## Key Architecture Patterns

### Data Flow Pipeline
```
Video File → VideoMetadataService.extract_from_video() → List[VideoFrameMetadata] → CsvExportService.export() → CSV File
```

The `VideoFrameMetadata` model is the core contract between all components. All extracted data must conform to this schema:
- Frame tracking: `frame_index`, `timestamp_ms`
- GPS: `latitude`, `longitude`, `altitude_m`
- Drone orientation: `yaw`, `pitch`, `roll` (degrees)
- Gimbal orientation: same three-axis angles

### Service Pattern
Services in `src/app/services/` are stateless utility classes. Example from `CsvExportService`:
```python
# Services take input, perform transformation, produce output
df = pd.DataFrame([f.model_dump() for f in frames])  # Pydantic → Pandas
df.to_csv(output_path, index=False)
```

## Critical Implementation Status

**VideoMetadataService is not implemented** (`src/app/services/video_metadata_service.py`). This is the highest priority:
- Method `extract_from_video(video_path: Path) -> List[VideoFrameMetadata]` raises `NotImplementedError`
- Comments indicate two possible approaches: exiftool or SRT file parsing
- All UI export functionality is disabled until this is complete

**UI is partially wired** (`src/app/ui.py`):
- File picker works (video selection callback updates `selected_video_path`)
- Export button is disabled (`disabled=True`)
- Export button's click handler shows placeholder dialog instead of calling service

## Development Conventions

1. **Hebrew Comments**: Project uses Hebrew comments extensively. Maintain this convention for consistency.
2. **Pydantic Models**: All data classes use Pydantic `BaseModel` for validation and serialization.
3. **Optional Fields**: DJI metadata may be incomplete - use `Optional[float] = None` for nullable fields.
4. **Entry Point**: `src/main.py` is the application entry point (Flet app setup).

## Integration Points

- **Flet Framework**: Desktop GUI. Window setup in `main.py`, UI components built dynamically in `build_main_view()`.
- **Pandas**: Used only in `CsvExportService.export()` for DataFrame → CSV conversion.
- **Pydantic**: `model_dump()` method converts models to dictionaries for Pandas/CSV export.

## Common Tasks

### Extracting Metadata from DJI Videos
Implement in `VideoMetadataService.extract_from_video()`:
1. Parse video file (exiftool command or SRT sidecar file)
2. Map telemetry data to `VideoFrameMetadata` fields
3. Handle missing/optional fields gracefully
4. Return ordered list by timestamp

### Adding UI Export Flow
Currently, export button is disabled and placeholder:
1. Wire export button click → call `VideoMetadataService.extract_from_video(selected_video_path)`
2. Pass results to `CsvExportService.export(frames, output_path)`
3. Show success/error dialog with `ft.AlertDialog`
4. Handle file picker for output location

### Adding New Metadata Fields
1. Add field to `VideoFrameMetadata` model in `src/app/models/video_frame_metadata.py`
2. Update extraction logic in `VideoMetadataService.extract_from_video()`
3. CSV export automatically includes new field (Pydantic's `model_dump()` handles it)

## Testing Notes

No tests currently exist. When adding tests:
- Use sample DJI video files or mock data
- Test `VideoFrameMetadata` validation (Pydantic handles this)
- Test CSV export format with `CsvExportService`
- Mock file I/O in UI layer tests
