import flet as ft
from pathlib import Path
import logging
import subprocess
import sys
from app.services.video_metadata_service import VideoMetadataService
from app.services.csv_export_service import CsvExportService

# הגדרת logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def build_main_view(page: ft.Page) -> ft.Column:
    selected_srt_path = ft.Text(value="לא נבחר קובץ SRT", selectable=True)
    status_text = ft.Text(value="", color="blue", size=14, selectable=True)
    open_folder_button = ft.ElevatedButton(
        "פתח תיקיית CSV",
        icon="folder_open",
        visible=False,
        on_click=None,  # נגדיר מאוחר יותר
    )

    def pick_srt(e: ft.FilePickerResultEvent):
        if e.files:
            selected_srt_path.value = e.files[0].path
            export_button.disabled = False
            open_folder_button.visible = False
            status_text.value = ""
            logger.info(f"נבחר קובץ SRT: {e.files[0].path}")
            page.update()

    file_picker = ft.FilePicker(on_result=pick_srt)
    page.overlay.append(file_picker)

    pick_button = ft.ElevatedButton(
        "בחר קובץ SRT",
        icon="description",
        on_click=lambda _: file_picker.pick_files(
            allow_multiple=False,
            allowed_extensions=["srt", "SRT"],
        ),
    )

    def export_to_csv(e):
        try:
            logger.info("מתחיל תהליך יצוא ל-CSV")
            status_text.value = "מעבד קובץ SRT..."
            status_text.color = "blue"
            page.update()
            
            srt_path = Path(selected_srt_path.value)
            logger.info(f"נתיב קובץ SRT: {srt_path}")
            
            if not srt_path.exists():
                raise FileNotFoundError(f"הקובץ לא קיים: {srt_path}")
            
            # חילוץ מטאדאטה מקובץ ה-SRT
            logger.info("מחלץ מטאדאטה מקובץ SRT...")
            status_text.value = "מחלץ מטאדאטה..."
            page.update()
            
            metadata_service = VideoMetadataService()
            frames = metadata_service.extract_from_video(srt_path)
            
            logger.info(f"חולצו {len(frames)} פריימים מהקובץ")
            
            if not frames:
                logger.warning("לא נמצאה מטאדאטה בקובץ SRT")
                status_text.value = "שגיאה: לא נמצאה מטאדאטה"
                status_text.color = "red"
                page.update()
                dialog = ft.AlertDialog(
                    title=ft.Text("שגיאה"),
                    content=ft.Text("לא נמצאה מטאדאטה בקובץ SRT."),
                )
                page.dialog = dialog
                dialog.open = True
                page.update()
                return
            
            # יצירת שם קובץ CSV
            csv_path = srt_path.with_suffix(".csv")
            logger.info(f"יוצר קובץ CSV: {csv_path}")
            status_text.value = f"יוצר קובץ CSV ({len(frames)} שורות)..."
            page.update()
            
            # יצוא ל-CSV
            export_service = CsvExportService()
            export_service.export(frames, csv_path)
            
            logger.info(f"קובץ CSV נוצר בהצלחה: {csv_path}")
            status_text.value = f"✓ הקובץ נוצר בהצלחה! ({len(frames)} שורות)"
            status_text.color = "green"
            
            # הוספת פונקציה לפתיחת תיקייה
            def open_folder(e):
                folder_path = csv_path.parent
                logger.info(f"פותח תיקייה: {folder_path}")
                try:
                    if sys.platform == "win32":
                        subprocess.run(["explorer", str(folder_path)])
                    elif sys.platform == "darwin":
                        subprocess.run(["open", str(folder_path)])
                    else:
                        subprocess.run(["xdg-open", str(folder_path)])
                except Exception as err:
                    logger.error(f"שגיאה בפתיחת תיקייה: {err}")
            
            open_folder_button.on_click = open_folder
            open_folder_button.visible = True
            page.update()
            
            # הצגת הודעת הצלחה
            dialog = ft.AlertDialog(
                title=ft.Text("הצלחה!"),
                content=ft.Text(
                    f"הקובץ נוצר בהצלחה:\n\n"
                    f"📄 {csv_path.name}\n"
                    f"📊 {len(frames)} שורות נוצרו\n\n"
                    f"נתיב מלא:\n{csv_path}"
                ),
            )
            page.dialog = dialog
            dialog.open = True
            page.update()
            
        except PermissionError as err:
            logger.error(f"אין הרשאה לכתוב לקובץ: {err}")
            status_text.value = "שגיאה: הקובץ נעול או פתוח בתוכנה אחרת"
            status_text.color = "red"
            page.update()
            dialog = ft.AlertDialog(
                title=ft.Text("שגיאה - הקובץ נעול"),
                content=ft.Text(
                    "לא ניתן לכתוב לקובץ CSV.\n\n"
                    "נא לסגור את הקובץ אם הוא פתוח ב-Excel או בתוכנה אחרת,\n"
                    "ולאחר מכן לנסות שוב."
                ),
            )
            page.dialog = dialog
            dialog.open = True
            page.update()
        except FileNotFoundError as err:
            logger.error(f"קובץ לא נמצא: {err}")
            status_text.value = f"שגיאה: {err}"
            status_text.color = "red"
            page.update()
            dialog = ft.AlertDialog(
                title=ft.Text("שגיאה"),
                content=ft.Text(f"קובץ לא נמצא:\n{err}"),
            )
            page.dialog = dialog
            dialog.open = True
            page.update()
        except Exception as err:
            logger.error(f"שגיאה בעיבוד הקובץ: {err}", exc_info=True)
            status_text.value = f"שגיאה: {str(err)}"
            status_text.color = "red"
            page.update()
            dialog = ft.AlertDialog(
                title=ft.Text("שגיאה"),
                content=ft.Text(f"שגיאה בעיבוד הקובץ:\n{str(err)}"),
            )
            page.dialog = dialog
            dialog.open = True
            page.update()
    
    export_button = ft.ElevatedButton(
        "יצא ל-CSV",
        icon="table_view",
        on_click=export_to_csv,
        disabled=True,
    )

    return ft.Column(
        [
            ft.Text("DJI SRT → CSV", size=32, weight=ft.FontWeight.BOLD),
            ft.Text("אפליקציה לחילוץ מטאדאטה מקבצי SRT של DJI ויצוא ל-CSV."),
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
