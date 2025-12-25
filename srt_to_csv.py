"""
DJI SRT to CSV Converter
========================
גרור ושחרר קובץ SRT על הסקריפט כדי ליצור קובץ CSV באותו מיקום.

Drag and drop an SRT file on this script to create a CSV file in the same location.
"""
import sys
import re
from pathlib import Path
from typing import List, Optional
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VideoFrameMetadata:
    """מודל לנתוני מטאדאטה של פריים וידאו"""
    
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
        """המרה למילון עם שמות עמודות מתאימים"""
        return {
            "COMMENTS": self.comments,
            "VIDEO NAME": self.video_name,
            "ALTITUDE": self.altitude,
            "LONGITUDE": self.longitude,
            "LATITUDE": self.latitude,
            "TIME": self.time,
            "DATE": self.date
        }


class SrtProcessor:
    """מעבד קבצי SRT ומחלץ מטאדאטה"""
    
    # Regex patterns
    TIME_RE = re.compile(r"(\d+):(\d+):(\d+),(\d+)")
    DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+)")
    LAT_RE = re.compile(r"\[latitude:\s*([-\d.]+)\]")
    LON_RE = re.compile(r"\[longitude:\s*([-\d.]+)\]")
    ABS_ALT_RE = re.compile(r"abs_alt:\s*([-\d.]+)")
    
    @staticmethod
    def _ms_to_hms(ms: int) -> str:
        """המרת אלפיות שנייה לפורמט HH:MM:SS,mmm"""
        total_seconds = ms // 1000
        milliseconds = ms % 1000
        seconds = total_seconds % 60
        total_minutes = total_seconds // 60
        minutes = total_minutes % 60
        hours = total_minutes // 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"
    
    def _extract_float(self, pattern: re.Pattern, text: str) -> Optional[float]:
        """חילוץ ערך מספרי מטקסט"""
        match = pattern.search(text)
        return float(match.group(1)) if match else None
    
    def _extract_string(self, pattern: re.Pattern, text: str) -> Optional[str]:
        """חילוץ מחרוזת מטקסט"""
        match = pattern.search(text)
        return match.group(1) if match else None
    
    def process_srt(self, srt_path: Path) -> List[VideoFrameMetadata]:
        """עיבוד קובץ SRT וחילוץ מטאדאטה"""
        logger.info(f"מתחיל עיבוד קובץ: {srt_path}")
        
        if not srt_path.exists():
            raise FileNotFoundError(f"קובץ לא נמצא: {srt_path}")
        
        # Read SRT file
        logger.info(f"קורא קובץ SRT: {srt_path}")
        with srt_path.open("r", encoding="utf-8") as f:
            lines = f.readlines()
        
        logger.info(f"נקראו {len(lines)} שורות מקובץ SRT")
        frames: List[VideoFrameMetadata] = []
        
        # Extract video name from path
        video_name = srt_path.stem
        
        i = 0
        while i < len(lines):
            # Search for timecode
            time_match = self.TIME_RE.search(lines[i])
            if not time_match:
                i += 1
                continue
            
            h, m, s, ms = map(int, time_match.groups())
            
            # Read next block (up to 12 lines)
            block_text = "".join(lines[i:i + 12])
            
            # Extract GPS data
            latitude = self._extract_float(self.LAT_RE, block_text)
            longitude = self._extract_float(self.LON_RE, block_text)
            altitude = self._extract_float(self.ABS_ALT_RE, block_text)
            
            # Skip frame if no GPS data
            if latitude is None or longitude is None:
                i += 1
                continue
            
            # Extract date
            date_str = self._extract_string(self.DATE_RE, block_text)
            date_only = date_str.split()[0] if date_str else ""
            
            # Calculate TIME
            timestamp_ms = ((h * 60 + m) * 60 + s) * 1000 + ms
            time_str = self._ms_to_hms(timestamp_ms)
            
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
                logger.info(f"חולצו {len(frames)} פריימים עד כה...")
        
        logger.info(f"סיים חילוץ: {len(frames)} פריימים בסך הכל")
        return frames


def export_to_csv(frames: List[VideoFrameMetadata], output_path: Path) -> None:
    """ייצוא נתונים לקובץ CSV"""
    logger.info(f"מייצא {len(frames)} פריימים ל-CSV")
    
    if not frames:
        raise ValueError("אין פריימים לייצוא")
    
    # Convert to CSV manually (no pandas dependency)
    with output_path.open("w", encoding="utf-8") as f:
        # Write header
        header = frames[0].to_dict()
        f.write(",".join(header.keys()) + "\n")
        
        # Write data rows
        for frame in frames:
            row_dict = frame.to_dict()
            row_values = [str(v) if v is not None else "" for v in row_dict.values()]
            f.write(",".join(row_values) + "\n")
    
    logger.info(f"קובץ CSV נשמר בהצלחה: {output_path}")


def main():
    """נקודת הכניסה הראשית"""
    print("=" * 60)
    print("DJI SRT to CSV Converter")
    print("=" * 60)
    
    # Check if SRT file was provided
    if len(sys.argv) < 2:
        print("\n❌ שגיאה: לא סופק קובץ SRT")
        print("Error: No SRT file provided")
        print("\nשימוש / Usage:")
        print("  גרור ושחרר קובץ SRT על הסקריפט")
        print("  Drag and drop an SRT file on this script")
        print("  OR")
        print("  python srt_to_csv.py <path_to_srt_file>")
        input("\nלחץ Enter לסגירה / Press Enter to close...")
        sys.exit(1)
    
    # Get SRT file path
    srt_path = Path(sys.argv[1])
    
    # Validate file exists and is SRT
    if not srt_path.exists():
        print(f"\n❌ שגיאה: הקובץ לא נמצא")
        print(f"Error: File not found: {srt_path}")
        input("\nלחץ Enter לסגירה / Press Enter to close...")
        sys.exit(1)
    
    if srt_path.suffix.upper() != ".SRT":
        print(f"\n❌ שגיאה: הקובץ אינו SRT")
        print(f"Error: File is not an SRT file: {srt_path}")
        print(f"File extension: {srt_path.suffix}")
        input("\nלחץ Enter לסגירה / Press Enter to close...")
        sys.exit(1)
    
    try:
        # Process SRT file
        print(f"\n📂 מעבד קובץ / Processing file: {srt_path.name}")
        processor = SrtProcessor()
        frames = processor.process_srt(srt_path)
        
        if not frames:
            print("\n⚠️  אזהרה: לא נמצאו נתוני GPS בקובץ")
            print("Warning: No GPS data found in file")
            input("\nלחץ Enter לסגירה / Press Enter to close...")
            sys.exit(1)
        
        # Export to CSV in same directory
        output_path = srt_path.with_suffix(".csv")
        print(f"\n💾 מייצא ל-CSV / Exporting to CSV: {output_path.name}")
        export_to_csv(frames, output_path)
        
        print(f"\n✅ הושלם בהצלחה! / Success!")
        print(f"📊 {len(frames)} פריימים נשמרו ל / frames saved to:")
        print(f"   {output_path}")
        
    except Exception as e:
        print(f"\n❌ שגיאה / Error: {str(e)}")
        logger.exception("Error during processing")
        input("\nלחץ Enter לסגירה / Press Enter to close...")
        sys.exit(1)
    
    input("\nלחץ Enter לסגירה / Press Enter to close...")


if __name__ == "__main__":
    main()
