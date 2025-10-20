import flet as ft
from datetime import datetime
from data_manager import DataManager
from kassenbericht_flet_view import KassenberichtView
from banknotes_flet_view import BanknotesView

def main(page: ft.Page):
    page.title = "Kassenbericht"
    page.window_width = 900
    page.window_height = 700
    page.padding = 10

    dm = DataManager()

    kassenbericht_view = KassenberichtView()
    banknotes_view = BanknotesView(page)     # <- pass page here

    content_area = ft.Column(expand=True, controls=[kassenbericht_view])

    def show_kassenbericht(e):
        content_area.controls = [kassenbericht_view]
        page.update()

    def show_banknotes(e):
        content_area.controls = [banknotes_view]
        page.update()

    def save_data(e):
        date = date_picker.value
        if date:
            data = {
                "kassenbericht": kassenbericht_view.get_data(),
                "banknotes": banknotes_view.get_data(),
            }
            dm.save_data(date, data)
            page.snack_bar = ft.SnackBar(ft.Text(f"Daten für {date.strftime('%d.%m.%Y')} gespeichert."))
            page.snack_bar.open = True
            page.update()

    def load_data(date):
        data = dm.load_data(date) if date else None
        kassenbericht_view.load_data(data.get("kassenbericht") if data else None)
        banknotes_view.load_data(data.get("banknotes") if data else None)
        page.update()   # <- update after both views mutated

    def on_date_change(e):
        date_button.text = date_picker.value.strftime('%d.%m.%Y')
        load_data(date_picker.value)
        page.update()

    date_picker = ft.DatePicker(
        on_change=on_date_change,
        first_date=datetime(2020, 1, 1),
        last_date=datetime(2030, 12, 31),
        value=datetime.now()
    )

    date_button = ft.ElevatedButton(
        datetime.now().strftime('%d.%m.%Y'),
        icon=ft.Icons.CALENDAR_MONTH,
        on_click=lambda _: page.open(date_picker),
    )

    # Add UI first
    page.add(
        ft.Row(
            [
                date_button,
                ft.ElevatedButton("Kassenbericht", on_click=show_kassenbericht),
                ft.ElevatedButton("Banknoten/Münzen", on_click=show_banknotes),
                ft.ElevatedButton("Speichern", on_click=save_data),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        content_area
    )

    # Now it's safe to load data (controls are attached)
    load_data(datetime.now())

if __name__ == "__main__":
    ft.app(target=main)
