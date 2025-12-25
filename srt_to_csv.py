"""
DJI SRT to CSV Converter
========================
Drag and drop an SRT file on this script to create a CSV file in the same location.
"""
import sys
import re
from pathlib import Path
from typing import List, Optional
import csv

# Regex patterns
TIME_RE = re.compile(r"(\d+):(\d+):(\d+),(\d+)")
DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+)")
LAT_RE = re.compile(r"\[latitude:\s*([-\d.]+)\]")
LON_RE = re.compile(r"\[longitude:\s*([-\d.]+)\]")
ABS_ALT_RE = re.compile(r"abs_alt:\s*([-\d.]+)")


class VideoFrameMetadata:
    """Model for video frame metadata"""
    
    def __init__(
        self,
        comments: str = "",
        video_name: str = "",
        altitude: Optional[float] = None,
        longitude: Optional[float] = None,
        latitude: Optional[float] = None,
        time: str = "",
        date: str = ""
    ):
        self.comments = comments
        self.video_name = video_name
        self.altitude = altitude
        self.longitude = longitude
        self.latitude = latitude
        self.time = time
        self.date = date
    
    def to_dict(self):
        """Convert to dictionary with proper column names"""
        return {
            "COMMENTS": self.comments,
            "VIDEO NAME": self.video_name,
            "ALTITUDE": self.altitude,
            "LONGITUDE": self.longitude,
            "LATITUDE": self.latitude,
            "TIME": self.time,
            "DATE": self.date
        }


def ms_to_hms(ms: int) -> str:
    """Convert milliseconds to HH:MM:SS:mmm format"""
    total_seconds = ms // 1000
    milliseconds = ms % 1000
    seconds = total_seconds % 60
    total_minutes = total_seconds // 60
    minutes = total_minutes % 60
    hours = total_minutes // 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}:{milliseconds:03d}"


def extract_float(pattern: re.Pattern, text: str) -> Optional[float]:
    """Extract float value from text using regex"""
    match = pattern.search(text)
    return float(match.group(1)) if match else None


def extract_string(pattern: re.Pattern, text: str) -> Optional[str]:
    """Extract string from text using regex"""
    match = pattern.search(text)
    return match.group(1) if match else None


def process_srt(srt_path: Path) -> List[VideoFrameMetadata]:
    """Process SRT file and extract metadata"""
    print(f"Processing file: {srt_path}")
    
    if not srt_path.exists():
        raise FileNotFoundError(f"File not found: {srt_path}")
    
    # Read SRT file
    print(f"Reading SRT file: {srt_path}")
    with srt_path.open("r", encoding="utf-8") as f:
        lines = f.readlines()
    
    print(f"Read {len(lines)} lines from SRT file")
    frames: List[VideoFrameMetadata] = []
    
    # Extract video name from path
    video_name = srt_path.stem
    
    i = 0
    while i < len(lines):
        # Search for timecode
        time_match = TIME_RE.search(lines[i])
        if not time_match:
            i += 1
            continue
        
        h, m, s, ms = map(int, time_match.groups())
        
        # Read next block (up to 12 lines)
        block_text = "".join(lines[i:i + 12])
        
        # Extract GPS data
        latitude = extract_float(LAT_RE, block_text)
        longitude = extract_float(LON_RE, block_text)
        altitude = extract_float(ABS_ALT_RE, block_text)
        
        # Skip frame if no GPS data
        if latitude is None or longitude is None:
            i += 1
            continue
        
        # Extract date
        date_str = extract_string(DATE_RE, block_text)
        date_only = date_str.split()[0] if date_str else ""
        
        # Calculate TIME
        timestamp_ms = ((h * 60 + m) * 60 + s) * 1000 + ms
        time_str = ms_to_hms(timestamp_ms)
        
        # Create frame metadata
        frame = VideoFrameMetadata(
            comments="",
            video_name=video_name,
            altitude=altitude,
            longitude=longitude,
            latitude=latitude,
            time=time_str,
            date=date_only,
        )
        
        frames.append(frame)
        i += 1
        
        # Log progress every 1000 frames
        if len(frames) % 1000 == 0:
            print(f"Extracted {len(frames)} frames so far...")
    
    print(f"Extraction complete: {len(frames)} frames total")
    return frames


def export_to_csv(frames: List[VideoFrameMetadata], output_path: Path) -> None:
    """Export data to CSV file"""
    print(f"Exporting {len(frames)} frames to CSV")
    
    if not frames:
        raise ValueError("No frames to export")
    
    # Use csv module to properly handle quoting (matches pandas behavior)
    with output_path.open("w", encoding="utf-8", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["COMMENTS", "VIDEO NAME", "ALTITUDE", "LONGITUDE", "LATITUDE", "TIME", "DATE"])
        writer.writeheader()
        
        for frame in frames:
            writer.writerow(frame.to_dict())
    
    print(f"CSV file saved successfully: {output_path}")


def main():
    """Main entry point"""
    print("=" * 60)
    print("DJI SRT to CSV Converter")
    print("=" * 60)
    
    # Check if SRT file was provided
    if len(sys.argv) < 2:
        print("\nError: No SRT file provided")
        print("\nUsage:")
        print("  Drag and drop an SRT file on this script")
        print("  OR")
        print("  python srt_to_csv.py <path_to_srt_file>")
        input("\nPress Enter to close...")
        sys.exit(1)
    
    # Get SRT file path
    srt_path = Path(sys.argv[1])
    
    # Validate file exists and is SRT
    if not srt_path.exists():
        print(f"\nError: File not found: {srt_path}")
        input("\nPress Enter to close...")
        sys.exit(1)
    
    if srt_path.suffix.upper() != ".SRT":
        print(f"\nError: File is not an SRT file: {srt_path}")
        print(f"File extension: {srt_path.suffix}")
        input("\nPress Enter to close...")
        sys.exit(1)
    
    try:
        # Process SRT file
        print(f"\nProcessing file: {srt_path.name}")
        frames = process_srt(srt_path)
        
        if not frames:
            print("\nWarning: No GPS data found in file")
            input("\nPress Enter to close...")
            sys.exit(1)
        
        # Export to CSV in same directory
        output_path = srt_path.with_suffix(".csv")
        print(f"\nExporting to CSV: {output_path.name}")
        export_to_csv(frames, output_path)
        
        print(f"\nSuccess!")
        print(f"{len(frames)} frames saved to:")
        print(f"   {output_path}")
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to close...")
        sys.exit(1)
    
    input("\nPress Enter to close...")


if __name__ == "__main__":
    main()
