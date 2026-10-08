import tkinter as tk
from tkinter import ttk
import pandas as pd


class SheetSelectionDialog(tk.Toplevel):
    """Dialog for selecting a sheet from an Excel file."""

    def __init__(self, parent, sheet_names: list):
        super().__init__(parent)
        self.withdraw()
        self.transient(parent)
        self.title("Select Sheet")
        self.grab_set()

        self.sheet_names = sheet_names
        self.result = None

        self._build_ui()
        self._position(parent)

        self.deiconify()

    def _build_ui(self):
        ttk.Label(self, text="Select sheet to load:").pack(pady=5)

        self.selected = tk.StringVar(value=self.sheet_names[0])
        dropdown = ttk.Combobox(self, textvariable=self.selected, values=self.sheet_names, state="readonly")
        dropdown.pack(pady=5)

        ttk.Button(self, text="Confirm", command=self.confirm).pack(pady=5)

    def _position(self, parent):
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"250x120+{x}+{y}")

    def confirm(self):
        self.result = self.selected.get()
        self.destroy()

    def show(self):
        self.wait_window()
        return self.result


class TableSelectionDialog(tk.Toplevel):
    """Dialog for selecting a table from a DataFrame with multiple header rows."""

    def __init__(self, parent, df_raw: pd.DataFrame, header_rows: list, count_datapoints_func):
        super().__init__(parent)
        self.withdraw()
        self.transient(parent)
        self.title("Select Table")
        self.grab_set()

        self.df_raw = df_raw
        self.header_rows = header_rows
        self.count_datapoints_func = count_datapoints_func
        self.result = None

        self._build_ui()
        self._position(parent)

        self.deiconify()

    def _build_ui(self):
        ttk.Label(self, text="Multiple tables found, select one:").pack(pady=5)

        options = [
            f"Table {i + 1} (header on row {row + 1}, {self.count_datapoints_func(self.df_raw, row)} datapoints)"
            for i, row in enumerate(self.header_rows)
        ]

        self.selected = tk.StringVar(value=options[0])
        dropdown = ttk.Combobox(self, textvariable=self.selected, values=options, state="readonly", width=50)
        dropdown.pack(pady=5)

        self.options = options
        ttk.Button(self, text="Confirm", command=self.confirm).pack(pady=5)

    def _position(self, parent):
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"400x120+{x}+{y}")

    def confirm(self):
        idx = self.options.index(self.selected.get())
        header_row = self.header_rows[idx]
        ndata = self.count_datapoints_func(self.df_raw, header_row)
        self.result = (header_row, ndata)
        self.destroy()

    def show(self):
        self.wait_window()
        return self.result
