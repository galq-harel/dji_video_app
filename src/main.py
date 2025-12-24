import flet as ft
from app.ui import build_main_view


def main(page: ft.Page) -> None:
    page.title = "DJI SRT → CSV"
    page.scroll = "auto"
    page.window_width = 900
    page.window_height = 600

    main_view = build_main_view(page)
    page.add(main_view)


if __name__ == "__main__":
    ft.app(target=main)
