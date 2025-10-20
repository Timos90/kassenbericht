import flet as ft

class KassenberichtView(ft.Column):
    def __init__(self):
        super().__init__()
        self.entries = {}
        self.dynamic_sections = {}
        self.scroll = ft.ScrollMode.AUTO
        self.expand = True

        self.wareneinkauf_section = self._create_dynamic_section("Wareneinkäufe", ["Sok Supermarket", "Lidl", "Netto", "Dimitrakopoulos", "Toom"], "wareneinkauf")
        self.gutschein_ausgaben_section = self._create_editable_dynamic_section("Gutschein (Ausgabe)", "gutschein_ausgaben")
        self.gutschein_einnahmen_section = self._create_editable_dynamic_section("Gutschein (Einnahme)", "gutschein_einnahmen")

        self.entries['ec_karte_ausgabe'] = ft.TextField(label="EC-Karte", width=300)
        self.entries['einzahlung_ausgabe'] = ft.TextField(label="Einzahlung", width=300)
        self.entries['kassennebenbestand_vortag'] = ft.TextField(label="abzüglich Kassennebenbestand des Vortages", width=300)
        self.entries['kasseneingang'] = ft.TextField(label="Kasseneingang", width=300)
        self.entries['pfand_einnahme'] = ft.TextField(label="Pfandrückgabe Lidl", width=300)

        self.total_label = ft.Text("Gesamt: 0.00 €", size=16, weight=ft.FontWeight.BOLD)

        self.controls = [
            ft.Text("Wareneinkäufe und Warennebenkosten", style=ft.TextThemeStyle.TITLE_LARGE),
            self.wareneinkauf_section,
            ft.Text("Sonstige Ausgaben", style=ft.TextThemeStyle.TITLE_LARGE),
            self.entries['ec_karte_ausgabe'],
            self.entries['einzahlung_ausgabe'],
            self.gutschein_ausgaben_section,
            ft.Text("Einnahmen", style=ft.TextThemeStyle.TITLE_LARGE),
            self.entries['kassennebenbestand_vortag'],
            self.entries['kasseneingang'],
            ft.Text("abzüglich sonstige Einnahmen", style=ft.TextThemeStyle.TITLE_LARGE),
            self.entries['pfand_einnahme'],
            self.gutschein_einnahmen_section,
            ft.Row([ft.ElevatedButton("Calculate", on_click=self.calculate_total), self.total_label], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        ]

    def _create_dynamic_section(self, title, items, section_key):
        self.entries[section_key] = {}
        controls = []
        for item in items:
            entry = ft.TextField(label=item, width=300, value="0")
            self.entries[section_key][item] = entry
            controls.append(entry)
        return ft.Column(controls)

    def _create_editable_dynamic_section(self, title, section_key):
        self.entries[section_key] = []
        column = ft.Column()
        self.dynamic_sections[section_key] = column

        def add_entry(e):
            name_entry = ft.TextField(label="Name", width=200)
            value_entry = ft.TextField(label="Wert", width=100, value="0")
            new_row = ft.Row([name_entry, value_entry])
            self.entries[section_key].append((name_entry, value_entry))
            column.controls.append(new_row)
            if self.page:
                self.update()

        add_button = ft.ElevatedButton(f"{title} Hinzufügen", on_click=add_entry)
        return ft.Column([ft.Text(title), column, add_button])

    def calculate_total(self, e):
        total_income = 0
        total_expenses = 0
        try:
            total_income += float(self.entries['kassennebenbestand_vortag'].value or 0)
            total_income += float(self.entries['kasseneingang'].value or 0)
            total_income += float(self.entries['pfand_einnahme'].value or 0)
            for _, value_entry in self.entries.get("gutschein_einnahmen", []):
                total_income += float(value_entry.value or 0)

            for entry in self.entries.get("wareneinkauf", {}).values():
                total_expenses += float(entry.value or 0)
            total_expenses += float(self.entries['ec_karte_ausgabe'].value or 0)
            total_expenses += float(self.entries['einzahlung_ausgabe'].value or 0)
            for _, value_entry in self.entries.get("gutschein_ausgaben", []):
                total_expenses += float(value_entry.value or 0)

            final_total = total_income - total_expenses
            self.total_label.value = f"Gesamt: {final_total:.2f} €"
        except ValueError:
            self.total_label.value = "Fehler: Ungültige Eingabe"
        if self.page:
            self.update()

    def get_data(self):
        data = {
            'wareneinkauf': [{'name': name, 'value': entry.value} for name, entry in self.entries['wareneinkauf'].items()],
            'gutschein_ausgaben': [{'name': name.value, 'value': value.value} for name, value in self.entries['gutschein_ausgaben']],
            'gutschein_einnahmen': [{'name': name.value, 'value': value.value} for name, value in self.entries['gutschein_einnahmen']],
        }
        for key in ['ec_karte_ausgabe', 'einzahlung_ausgabe', 'kassennebenbestand_vortag', 'kasseneingang', 'pfand_einnahme']:
            data[key] = self.entries[key].value
        return data

    def load_data(self, data):
        # First, reset all static fields
        for key in ['ec_karte_ausgabe', 'einzahlung_ausgabe', 'kassennebenbestand_vortag', 'kasseneingang', 'pfand_einnahme']:
            self.entries[key].value = ""
        
        # Reset wareneinkauf fields
        for entry in self.entries.get("wareneinkauf", {}).values():
            entry.value = "0"

        # Now, load new data if it exists
        data = data or {}
        
        for key in ['ec_karte_ausgabe', 'einzahlung_ausgabe', 'kassennebenbestand_vortag', 'kasseneingang', 'pfand_einnahme']:
            self.entries[key].value = data.get(key, "")

        for item in data.get('wareneinkauf', []):
            if item['name'] in self.entries['wareneinkauf']:
                self.entries['wareneinkauf'][item['name']].value = item['value']

        for section_key in ['gutschein_ausgaben', 'gutschein_einnahmen']:
            section = self.dynamic_sections[section_key]
            section.controls.clear()
            self.entries[section_key].clear()
            for item in data.get(section_key, []):
                name_entry = ft.TextField(label="Name", width=200, value=item.get('name', ''))
                value_entry = ft.TextField(label="Wert", width=100, value=item.get('value', ''))
                new_row = ft.Row([name_entry, value_entry])
                self.entries[section_key].append((name_entry, value_entry))
                section.controls.append(new_row)

        self.calculate_total(None)
        if self.page:
            self.update()