import flet as ft

def build_main_view(page: ft.Page) -> ft.Column:
    selected_video_path = ft.Text(value="No video selected", selectable=True)

    def pick_video(e: ft.FilePickerResultEvent):
        if e.files:
            selected_video_path.value = e.files[0].path
            page.update()

    file_picker = ft.FilePicker(on_result=pick_video)
    page.overlay.append(file_picker)

    pick_button = ft.ElevatedButton(
        "בחר סרטון DJI",
        icon="video_file",
        on_click=lambda _: file_picker.pick_files(
            allow_multiple=False,
            allowed_extensions=["mp4", "mov"],
        ),
    )

    export_button = ft.ElevatedButton(
        "יצא ל-CSV",
        icon="table_view",
        on_click=lambda _: ft.AlertDialog(
            title=ft.Text("Coming soon"),
            content=ft.Text("כאן נייצר CSV מהסרטון."),
        ),
        disabled=True,
    )

    return ft.Column(
        [
            ft.Text("DJI Video → CSV", size=32, weight=ft.FontWeight.BOLD),
            ft.Text("אפליקציה לחילוץ מטאדאטה מסרטוני DJI ויצוא ל-CSV."),
            ft.Divider(),
            pick_button,
            selected_video_path,
            ft.Divider(),
            export_button,
        ],
        spacing=20,
        expand=True,
    )
