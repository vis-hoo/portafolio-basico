#!/usr/bin/env python3
"""Calculator: calculadora científica GTK4 con libadwaita."""

import os
import sys

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gdk, Gtk, Pango

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import evaluate, format_number, to_fraction

BG = "#1e1e2e"
SURFACE = "#2a2a3c"
DIGIT_BG = "#3a3a4e"
ACCENT = "#3584e4"
TEXT = "#e4e4ef"
DIM = "#9a9ab0"
ERROR = "#e64553"

CSS = f"""
window {{ background: {BG}; }}
.entry-box {{
  background: {SURFACE};
  border-radius: 10px;
  padding: 10px 14px;
}}
.expr {{ color: {DIM}; font-size: 15px; }}
.result {{
  color: {TEXT};
  font-size: 34px;
  font-weight: bold;
}}
.result.error {{ color: {ERROR}; }}
.frac {{ color: {DIM}; font-size: 16px; }}
button {{
  background: {SURFACE};
  color: {TEXT};
  border: none;
  border-radius: 10px;
  font-size: 16px;
  min-height: 44px;
  min-width: 44px;
}}
button:hover {{ background: #34344a; }}
button.digit {{ background: {DIGIT_BG}; font-size: 18px; }}
button.digit:hover {{ background: #46465e; }}
button.op {{ font-weight: bold; }}
button.eq {{ background: {ACCENT}; color: white; font-size: 20px; font-weight: bold; }}
button.eq:hover {{ background: #4a90e8; }}
button.toggle {{ background: {ACCENT}; color: #ffffff; }}
button.toggle:hover {{ background: #5b9ceb; color: #ffffff; }}
button.toggle:active {{ background: #7fb4f2; color: #ffffff; }}
button.toggle:checked {{ background: {ACCENT}; color: #ffffff; }}
button.toggle:checked:hover {{ background: #5b9ceb; }}
button.toggle:checked:active {{ background: #7fb4f2; }}
button.history-panel {{ background: {DIGIT_BG}; }}
.history-row {{
  background: {SURFACE};
  border-radius: 8px;
  padding: 6px 10px;
  margin: 2px 0;
}}
.history-expr {{ color: {DIM}; font-size: 12px; }}
.history-result {{ color: {TEXT}; font-size: 14px; font-weight: bold; }}
.history-empty {{ color: {DIM}; font-size: 13px; padding: 8px; }}
.sidebar-title {{ color: {TEXT}; font-weight: bold; padding: 4px 0; }}
"""


def build_css():
    provider = Gtk.CssProvider()
    provider.load_from_data(CSS.encode())
    display = Gdk.Display.get_default()
    Gtk.StyleContext.add_provider_for_display(
        display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )


class CalculatorWindow(Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="Calculator", default_width=560)
        self.set_default_size(560, 520)
        self.expr = ""
        self.ans = 0.0
        self.degrees = True
        self.locked = False
        self.last_ok = False

        header = Adw.HeaderBar()
        header.set_title_widget(Adw.WindowTitle.new("Calculator", ""))

        self.deg_toggle = Gtk.ToggleButton(label="Deg")
        self.deg_toggle.add_css_class("toggle")
        self.deg_toggle.set_active(True)
        self.deg_toggle.connect("toggled", self.on_deg_toggled)
        header.pack_start(self.deg_toggle)

        clear_history = Gtk.Button.new_from_icon_name("user-trash-symbolic")
        clear_history.set_tooltip_text("Vaciar historial")
        clear_history.connect("clicked", lambda _b: self.clear_history())
        header.pack_end(clear_history)

        # --- Columna izquierda: expresión + resultado --------------------
        expr_label = Gtk.Label(label="")
        expr_label.set_xalign(1)
        expr_label.set_ellipsize(Pango.EllipsizeMode.END)
        expr_label.add_css_class("expr")
        self.expr_label = expr_label

        self.result_label = Gtk.Label(label="")
        self.result_label.set_xalign(1)
        self.result_label.add_css_class("result")

        self.frac_label = Gtk.Label(label="")
        self.frac_label.set_xalign(1)
        self.frac_label.add_css_class("frac")

        entry_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        entry_box.add_css_class("entry-box")
        entry_box.append(expr_label)
        entry_box.append(self.result_label)
        entry_box.append(self.frac_label)

        # --- Bloque izquierdo: dígitos y operadores (4 columnas) -----------
        left_buttons = [
            # (etiqueta, fila, col, span, clase)
            ("(", 0, 0, 1, "op"),
            (")", 0, 1, 1, "op"),
            ("%", 0, 2, 1, "op"),
            ("÷", 0, 3, 1, "op"),
            ("7", 1, 0, 1, "digit"),
            ("8", 1, 1, 1, "digit"),
            ("9", 1, 2, 1, "digit"),
            ("×", 1, 3, 1, "op"),
            ("4", 2, 0, 1, "digit"),
            ("5", 2, 1, 1, "digit"),
            ("6", 2, 2, 1, "digit"),
            ("−", 2, 3, 1, "op"),
            ("1", 3, 0, 1, "digit"),
            ("2", 3, 1, 1, "digit"),
            ("3", 3, 2, 1, "digit"),
            ("+", 3, 3, 1, "op"),
            ("0", 4, 0, 1, "digit"),
            (",", 4, 1, 1, "digit"),
            ("=", 4, 2, 2, "eq"),
        ]

        left_grid = Gtk.Grid()
        left_grid.set_column_spacing(8)
        left_grid.set_row_spacing(8)
        for text, row, col, span, css in left_buttons:
            button = Gtk.Button(label=text)
            button.add_css_class(css)
            button.connect("clicked", self.on_button, text)
            left_grid.attach(button, col, row, span, 1)

        # --- Bloque derecho: funciones y utilidades (6 columnas) -----------
        # Los pares (e, π) y (ln, log) ocupan 3 columnas cada uno (la mitad
        # de la fila); los tríos ocupan 2 columnas cada uno.
        right_buttons = [
            ("C", 0, 0, 2, "op"),
            ("⌫", 0, 2, 2, "op"),
            ("Ans", 0, 4, 2, "op"),
            ("e", 1, 0, 3, "digit"),
            ("π", 1, 3, 3, "digit"),
            ("ln", 2, 0, 3, "op"),
            ("log", 2, 3, 3, "op"),
            ("^", 3, 0, 2, "op"),
            ("√", 3, 2, 2, "op"),
            ("!", 3, 4, 2, "op"),
            ("sin", 4, 0, 2, "op"),
            ("cos", 4, 2, 2, "op"),
            ("tan", 4, 4, 2, "op"),
        ]

        right_grid = Gtk.Grid()
        right_grid.set_column_spacing(8)
        right_grid.set_row_spacing(8)
        for text, row, col, span, css in right_buttons:
            button = Gtk.Button(label=text)
            button.add_css_class(css)
            button.connect("clicked", self.on_button, text)
            right_grid.attach(button, col, row, span, 1)

        separator = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)

        keypad = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=24)
        keypad.append(left_grid)
        keypad.append(separator)
        keypad.append(right_grid)

        left = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        left.set_margin_top(8)
        left.set_margin_start(16)
        left.set_margin_end(8)
        left.set_margin_bottom(16)
        left.append(entry_box)
        left.append(keypad)

        # --- Historial -----------------------------------------------------
        self.history_list = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.history_empty = Gtk.Label(label="Sin cálculos aún")
        self.history_empty.add_css_class("history-empty")
        self.history_list.append(self.history_empty)

        title = Gtk.Label(label="Historial")
        title.add_css_class("sidebar-title")
        title.set_xalign(0)

        side = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        side.set_margin_top(8)
        side.set_margin_end(16)
        side.set_margin_bottom(16)
        side.set_size_request(200, -1)
        side.append(title)
        side.append(self.history_list)

        outer = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        outer.append(left)
        outer.append(side)

        toolbar_view = Adw.ToolbarView()
        toolbar_view.add_top_bar(header)
        toolbar_view.set_content(outer)
        self.set_content(toolbar_view)

        self.evaluate_live()

    # --- Lógica -------------------------------------------------------------

    def on_button(self, _button, text):
        if text == "C":
            self.expr = ""
            self.locked = False
            self.evaluate_live()
            return
        if text == "=":
            self.confirm()
            return
        # Tras confirmar con '=', el primer botón de entrada inicia una
        # expresión nueva; el resultado permanece visible hasta ese momento.
        if self.locked:
            if text == "Ans" or text == "⌫":
                return
            self.expr = ""
            self.locked = False
        if text == "⌫":
            self.expr = self.expr[:-1]
        elif text == ",":
            self.expr += "."
        elif text == "√":
            self.expr += "sqrt("
        elif text == "sin":
            self.expr += "sin("
        elif text == "cos":
            self.expr += "cos("
        elif text == "tan":
            self.expr += "tan("
        elif text == "log":
            self.expr += "log("
        elif text == "ln":
            self.expr += "ln("
        elif text == "−":
            self.expr += "-"
        elif text == "×":
            self.expr += "*"
        elif text == "÷":
            self.expr += "/"
        else:
            self.expr += text
        self.evaluate_live()

    def evaluate_live(self):
        self.expr_label.set_text(self.expr if self.expr else " ")
        if not self.expr:
            self.show_result("")
            return
        ok, value = evaluate(self.expr, self.degrees, self.ans)
        self.last_ok = ok
        if ok:
            self.show_result(format_number(value))
            frac = to_fraction(value)
            self.frac_label.set_text(frac if frac else "")
        else:
            if value == "división por cero":
                self.show_result("Error", is_error=True)
            elif value in ("incompleta", "vacía"):
                self.show_result("")
            else:
                self.show_result("Error", is_error=True)

    def show_result(self, text, is_error=False):
        self.result_label.set_text(text)
        if is_error:
            self.result_label.add_css_class("error")
        else:
            self.result_label.remove_css_class("error")

    def confirm(self):
        if self.locked:
            return
        if not self.last_ok or not self.expr:
            self.show_result("Error", is_error=True)
            return
        ok, value = evaluate(self.expr, self.degrees, self.ans)
        if not ok:
            self.show_result("Error", is_error=True)
            return
        self.ans = value
        result_text = format_number(value)
        self.add_history(self.expr, result_text)
        self.expr = result_text
        self.locked = True
        self.evaluate_live()

    def on_deg_toggled(self, button):
        self.degrees = button.get_active()
        button.set_label("Deg" if self.degrees else "Rad")
        self.evaluate_live()

    # --- Historial -----------------------------------------------------------

    def add_history(self, expr, result):
        self.history_empty.set_visible(False)
        row = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        row.add_css_class("history-row")
        expr_lbl = Gtk.Label(label=f"{expr} =")
        expr_lbl.add_css_class("history-expr")
        expr_lbl.set_xalign(0)
        expr_lbl.set_ellipsize(Pango.EllipsizeMode.END)
        res_lbl = Gtk.Label(label=result)
        res_lbl.add_css_class("history-result")
        res_lbl.set_xalign(0)
        row.append(expr_lbl)
        row.append(res_lbl)
        self.history_list.append(row)

    def clear_history(self):
        child = self.history_list.get_first_child()
        while child:
            nxt = child.get_next_sibling()
            self.history_list.remove(child)
            child = nxt
        self.history_empty.set_text("Sin cálculos aún")
        self.history_list.append(self.history_empty)
        self.history_empty.set_visible(True)


class CalculatorApp(Adw.Application):
    def do_activate(self):
        build_css()
        CalculatorWindow(self).present()


if __name__ == "__main__":
    CalculatorApp(application_id="com.github.vishoo.calculator").run([])
