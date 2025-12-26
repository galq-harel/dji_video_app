import flet as ft
from pathlib import Path
import logging
import subprocess
import sys
from app.services.video_metadata_service import VideoMetadataService
from app.services.csv_export_service import CsvExportService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def build_main_view(page: ft.Page) -> ft.Column:
    selected_srt_path = ft.Text(value="No SRT file selected", selectable=True)
    status_text = ft.Text(value="", color="blue", size=14, selectable=True)
    open_folder_button = ft.ElevatedButton(
        "Open CSV Folder",
        icon="folder_open",
        visible=False,
        on_click=None,  # Will be set later
    )

    def pick_srt(e: ft.FilePickerResultEvent):
        if e.files:
            file_path = Path(e.files[0].path)
            
            # Basic validation checks
            if not file_path.exists():
                status_text.value = "Error: File not found"
                status_text.color = "red"
                selected_srt_path.value = "No SRT file selected"
                export_button.disabled = True
                page.update()
                show_error_dialog(
                    "File Not Found",
                    "The selected file does not exist in the system.",
                    f"Path: {file_path}"
                )
                return
            
            if file_path.suffix.upper() not in ['.SRT', '.srt']:
                status_text.value = "Error: File is not SRT"
                status_text.color = "red"
                selected_srt_path.value = "No SRT file selected"
                export_button.disabled = True
                page.update()
                show_error_dialog(
                    "Unsupported File Type",
                    "The selected file is not an SRT file.",
                    f"File extension: {file_path.suffix}\n\nPlease select a valid SRT file."
                )
                return
            
            # If everything is valid
            selected_srt_path.value = e.files[0].path
            export_button.disabled = False
            open_folder_button.visible = False
            status_text.value = "✓ Valid SRT file selected"
            status_text.color = "green"
            logger.info(f"SRT file selected: {e.files[0].path}")
            page.update()

    file_picker = ft.FilePicker(on_result=pick_srt)
    page.overlay.append(file_picker)

    pick_button = ft.ElevatedButton(
        "Select SRT File",
        icon="description",
        on_click=lambda _: file_picker.pick_files(
            allow_multiple=False,
            allowed_extensions=["srt", "SRT"],
        ),
    )

    def show_error_dialog(title: str, message: str, details: str = ""):
        """Display error dialog with additional details"""
        content_parts = [ft.Text(message, size=14)]
        if details:
            content_parts.extend([
                ft.Text(""),
                ft.Text("Additional Details:", weight=ft.FontWeight.BOLD, size=12),
                ft.Text(details, size=11, color="grey"),
            ])
        
        dialog = ft.AlertDialog(
            title=ft.Text(title, color="red"),
            content=ft.Column(content_parts, tight=True, spacing=5),
            actions=[
                ft.TextButton("Close", on_click=lambda _: setattr(dialog, 'open', False) or page.update())
            ],
        )
        page.dialog = dialog
        dialog.open = True
        page.update()

    def export_to_csv(e):
        try:
            logger.info("Starting CSV export process")
            status_text.value = "Processing SRT file..."
            status_text.color = "blue"
            page.update()
            
            srt_path = Path(selected_srt_path.value)
            logger.info(f"SRT file path: {srt_path}")
            
            # Check if file exists
            if not srt_path.exists():
                logger.error(f"SRT file does not exist: {srt_path}")
                status_text.value = "Error: SRT file not found"
                status_text.color = "red"
                page.update()
                show_error_dialog(
                    "SRT File Not Found",
                    "The selected file does not exist in the system.",
                    f"Path: {srt_path}\n\nThe file may have been deleted or moved to another location."
                )
                return
            
            # Check file size
            file_size = srt_path.stat().st_size
            if file_size == 0:
                logger.error(f"SRT file is empty: {srt_path}")
                status_text.value = "Error: SRT file is empty"
                status_text.color = "red"
                page.update()
                show_error_dialog(
                    "Empty SRT File",
                    "The selected file does not contain any content.",
                    f"File size: 0 bytes\n\nPlease select a valid SRT file with metadata."
                )
                return
            
            # Extract metadata from SRT file
            logger.info("Extracting metadata from SRT file...")
            status_text.value = "Extracting metadata..."
            page.update()
            
            metadata_service = VideoMetadataService()
            frames = metadata_service.extract_from_video(srt_path)
            
            logger.info(f"Extracted {len(frames)} frames from file")
            
            if not frames:
                logger.warning("No GPS data found in SRT file")
                status_text.value = "Error: No GPS data found"
                status_text.color = "red"
                page.update()
                show_error_dialog(
                    "No GPS Data Found",
                    "The file does not contain valid GPS metadata.",
                    f"The file contains {file_size:,} bytes but no frames with GPS data were found.\n\n"
                    "Make sure this is a valid SRT file from a DJI drone."
                )
                return
            
            # Create CSV filename
            csv_path = srt_path.with_suffix(".csv")
            
            # Check write permissions
            csv_dir = csv_path.parent
            if not csv_dir.exists():
                logger.error(f"Output directory does not exist: {csv_dir}")
                status_text.value = "Error: Output directory does not exist"
                status_text.color = "red"
                page.update()
                show_error_dialog(
                    "Output Directory Does Not Exist",
                    "The directory where the SRT file is located does not exist.",
                    f"Path: {csv_dir}"
                )
                return
            
            # Check if CSV file already exists and is locked
            if csv_path.exists():
                try:
                    # Try to open the file in write mode to check if it's locked
                    with open(csv_path, 'a'):
                        pass
                except PermissionError:
                    logger.error(f"CSV file is locked: {csv_path}")
                    status_text.value = "Error: File is locked"
                    status_text.color = "red"
                    page.update()
                    show_error_dialog(
                        "CSV File is Locked",
                        f"The file {csv_path.name} is open in another application.",
                        "Please close the file in Excel or any other application and try again."
                    )
                    return
            
            logger.info(f"Creating CSV file: {csv_path}")
            status_text.value = f"Creating CSV file ({len(frames)} rows)..."
            page.update()
            
            # Export to CSV
            export_service = CsvExportService()
            export_service.export(frames, csv_path)
            
            logger.info(f"CSV file created successfully: {csv_path}")
            status_text.value = f"✓ File created successfully! ({len(frames)} rows)"
            status_text.color = "green"
            
            # Add function to open folder
            def open_folder(e):
                folder_path = csv_path.parent
                logger.info(f"Opening folder: {folder_path}")
                try:
                    if sys.platform == "win32":
                        subprocess.run(["explorer", str(folder_path)])
                    elif sys.platform == "darwin":
                        subprocess.run(["open", str(folder_path)])
                    else:
                        subprocess.run(["xdg-open", str(folder_path)])
                except Exception as err:
                    logger.error(f"Error opening folder: {err}")
            
            open_folder_button.on_click = open_folder
            open_folder_button.visible = True
            page.update()
            
            # Display success message
            dialog = ft.AlertDialog(
                title=ft.Text("Success!"),
                content=ft.Text(
                    f"File created successfully:\n\n"
                    f"📄 {csv_path.name}\n"
                    f"📊 {len(frames)} rows created\n\n"
                    f"Full path:\n{csv_path}"
                ),
            )
            page.dialog = dialog
            dialog.open = True
            page.update()
            
        except PermissionError as err:
            logger.error(f"Permission denied: {err}")
            status_text.value = "Error: Permission denied"
            status_text.color = "red"
            page.update()
            show_error_dialog(
                "Permission Denied",
                "Cannot write the CSV file.",
                f"Error: {str(err)}\n\n"
                "Possible causes:\n"
                "• File is open in Excel or another application - please close and try again\n"
                "• No write permissions for the directory\n"
                "• Disk is full"
            )
        except FileNotFoundError as err:
            logger.error(f"File not found: {err}")
            status_text.value = "Error: File not found"
            status_text.color = "red"
            page.update()
            show_error_dialog(
                "File Not Found",
                "SRT file not found in the system.",
                f"{str(err)}\n\nThe file may have been deleted during processing."
            )
        except UnicodeDecodeError as err:
            logger.error(f"Encoding error: {err}")
            status_text.value = "Error: Invalid file encoding"
            status_text.color = "red"
            page.update()
            show_error_dialog(
                "Encoding Error",
                "Cannot read the SRT file.",
                f"The file is not encoded in UTF-8.\n\n"
                f"Error: {str(err)}\n\n"
                "Please make sure this is a valid SRT file from a DJI drone."
            )
        except ValueError as err:
            logger.error(f"Value error: {err}")
            status_text.value = "Error: Invalid data"
            status_text.color = "red"
            page.update()
            show_error_dialog(
                "Data Error",
                "The data in the file is invalid.",
                f"{str(err)}\n\nThe file format may not match DJI SRT files."
            )
        except OSError as err:
            logger.error(f"Filesystem error: {err}")
            status_text.value = "Error: Filesystem issue"
            status_text.color = "red"
            page.update()
            
            # Detailed analysis of filesystem errors
            error_msg = str(err)
            if "disk full" in error_msg.lower() or "no space" in error_msg.lower():
                details = "Disk is full. Please free up space and try again."
            elif "read-only" in error_msg.lower():
                details = "Directory is read-only. Please change permissions and try again."
            else:
                details = f"Filesystem error:\n{error_msg}"
            
            show_error_dialog(
                "Filesystem Error",
                "An error occurred accessing the filesystem.",
                details
            )
        except Exception as err:
            logger.error(f"Unexpected error: {err}", exc_info=True)
            status_text.value = "Error: Unexpected failure"
            status_text.color = "red"
            page.update()
            show_error_dialog(
                "Unexpected Error",
                "An unexpected error occurred while processing the file.",
                f"Error type: {type(err).__name__}\n"
                f"Message: {str(err)}\n\n"
                "Please check the LOG file for more details."
            )
    
    export_button = ft.ElevatedButton(
        "Export to CSV",
        icon="table_view",
        on_click=export_to_csv,
        disabled=True,
    )

    return ft.Column(
        [
            ft.Text("DJI SRT → CSV", size=32, weight=ft.FontWeight.BOLD),
            ft.Text("Extract metadata from DJI SRT files and export to CSV."),
            ft.Divider(),
            pick_button,
            selected_srt_path,
            ft.Divider(),
            export_button,
            status_text,
            open_folder_button,
        ],
        spacing=20,
        expand=True,
    )
