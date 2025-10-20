import flet as ft
import ast, operator as op

class BanknotesView(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.scroll = ft.ScrollMode.AUTO
        self.expand = True

        self.denominations = [500,200,100,50,20,10,5,2,1,0.5,0.2,0.1,0.05,0.02,0.01]
        self.entries = {}

        # header
        self.controls.append(
            ft.Row([
                ft.Text("Stückelung", width=150, weight=ft.FontWeight.BOLD),
                ft.Text("Anzahl", width=200, weight=ft.FontWeight.BOLD),
                ft.Text("Summe", width=150, weight=ft.FontWeight.BOLD),
            ])
        )

        # rows
        for denom in self.denominations:
            summe_text = ft.Text("", width=150)
            anzahl_label = ft.Text("", width=200)

            # clickable Anzahl cell
            anzahl_clickable = ft.Container(
                content=anzahl_label,
                padding=8,
                border_radius=6,
                # Use Colors (capital C) on your current Flet version:
                bgcolor=ft.Colors.with_opacity(0.03, ft.Colors.ON_SURFACE),
                ink=True,
                on_click=lambda e, d=denom: self.show_calculator(d),
            )

            self.entries[denom] = {
                "anzahl": anzahl_label,
                "summe": summe_text,
                "calculation_str": "",
            }

            self.controls.append(
                ft.Container(
                    padding=6,
                    content=ft.Row(
                        [
                            ft.Text(f"{denom} €" if denom >= 1 else f"{int(denom*100)} Cent", width=150),
                            anzahl_clickable,
                            summe_text,
                        ],
                        alignment=ft.MainAxisAlignment.START,
                    ),
                )
            )

        self.total_label = ft.Text("Kassenbestand: 0.00 €", size=16, weight=ft.FontWeight.BOLD)
        self.controls.append(self.total_label)

        # ---- reusable dialog & handlers (create once) ----
        self._current_denom = None
        self._dlg_title = ft.Text("Anzahl berechnen")           # create once
        self._calc_input = ft.TextField(label="Berechnung", autofocus=True)
        self._calc_error = ft.Text("", color=ft.Colors.RED)     # use Colors on your version

        def _on_ok(e):
            try:
                result = self.safe_eval(self._calc_input.value)
                d = self._current_denom
                self.entries[d]["calculation_str"] = self._calc_input.value
                self.entries[d]["anzahl"].value = f"{result} ( {self._calc_input.value} )"
                self.update_sum(d, result)
                self._dlg.open = False
                self.page.update()
            except Exception as ex:
                self._calc_error.value = f"Ungültige Eingabe: {ex}"
                self.page.update()

        def _on_cancel(e):
            self._dlg.open = False
            self.page.update()

        self._dlg = ft.AlertDialog(
            modal=True,
            title=self._dlg_title,  # <- reuse
            content=ft.Column([self._calc_input, self._calc_error], tight=True, spacing=8),
            actions=[ft.TextButton("OK", on_click=_on_ok),
                     ft.TextButton("Abbrechen", on_click=_on_cancel)],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        # Make sure page knows about the dialog exactly once:
        if self._dlg not in self.page.overlay:
            self.page.overlay.append(self._dlg)

    def get_data(self):
        return {
            str(denom): {
                "anzahl": entry["anzahl"].value,
                "calculation_str": entry["calculation_str"]
            }
            for denom, entry in self.entries.items()
        }

    def show_calculator(self, denom):
        self._current_denom = denom
        # mutate existing controls, don't replace them
        self._dlg_title.value = f"Anzahl für {denom} € berechnen"
        self._calc_input.value = self.entries[denom]["calculation_str"]
        self._calc_error.value = ""
        # open using helper (more reliable across versions)
        self.page.open(self._dlg)

    # --- the rest unchanged, but DO NOT call self.update() inside load_data ---
    def safe_eval(self, expr: str) -> float:
        expr = (expr or "").strip().replace(",", ".")
        ops = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv}
        def _eval(node):
            if isinstance(node, ast.Constant): return float(node.value)
            if isinstance(node, ast.Num):      return float(node.n)
            if isinstance(node, ast.BinOp) and type(node.op) in ops:
                return ops[type(node.op)](_eval(node.left), _eval(node.right))
            if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
                return +_eval(node.operand) if isinstance(node.op, ast.UAdd) else -_eval(node.operand)
            raise ValueError("Nur +, -, *, / und Zahlen sind erlaubt.")
        return _eval(ast.parse(expr, mode="eval").body)

    def update_sum(self, denom, anzahl):
        try:
            summe = float(anzahl) * float(denom)
        except (TypeError, ValueError):
            summe = 0.0
        self.entries[denom]["summe"].value = f"{summe:.2f} €"
        self.update_total_kassenbestand()

    def update_total_kassenbestand(self):
        total = 0.0
        for info in self.entries.values():
            s = (info["summe"].value or "").replace("€", "").strip().replace(",", ".")
            try:
                total += float(s) if s else 0.0
            except ValueError:
                pass
        self.total_label.value = f"Kassenbestand: {total:.2f} €"
        # no self.update() here — parent will call page.update()

    def load_data(self, data):
        # First, reset all fields to default
        for denom, entry in self.entries.items():
            entry["anzahl"].value = ""
            entry["calculation_str"] = ""
            self.update_sum(denom, 0)

        # Now, load new data if it exists
        data = data or {}
        for denom_str, denom_data in data.items():
            denom = float(denom_str)
            if denom in self.entries:
                self.entries[denom]["anzahl"].value = denom_data.get("anzahl", "")
                self.entries[denom]["calculation_str"] = denom_data.get("calculation_str", "")
                raw = (denom_data.get("anzahl", "") or "").split(" ")[0]
                try:
                    self.update_sum(denom, float(raw) if raw else 0.0)
                except (ValueError, IndexError):
                    self.update_sum(denom, 0.0)
        
        self.update_total_kassenbestand()
