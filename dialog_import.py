import tkinter as tk
from tkinter import messagebox, ttk

from curve_import import ColumnMapping, CurveTable, ExperimentalCurve, validate_curve


class CurveImportDialog(tk.Toplevel):
    """Preview candidate tables and confirm the columns used for the curve."""

    def __init__(self, parent, tables: list[CurveTable]):
        super().__init__(parent)
        self.withdraw()
        self.transient(parent)
        self.title("Import Excitation Curve")
        self.minsize(580, 410)
        self.bind("<Escape>", lambda _event: self.destroy())
        self.result: ExperimentalCurve | None = None
        self.tables = tables
        self._build_ui()
        self._select_sheet()
        self.deiconify()
        self.grab_set()
        self.sheet_picker.focus_set()

    def _build_ui(self):
        panel = ttk.Frame(self, padding=12)
        panel.pack(fill="both", expand=True)
        panel.columnconfigure(1, weight=1)
        panel.rowconfigure(2, weight=1)
        self.sheet_picker = self._picker(panel, 0, "Sheet / file")
        self.sheet_picker.configure(values=list(dict.fromkeys(table.sheet for table in self.tables)))
        self.sheet_picker.current(0)
        self.sheet_picker.bind("<<ComboboxSelected>>", self._select_sheet)
        self.table_picker = self._picker(panel, 1, "Table")
        self.table_picker.bind("<<ComboboxSelected>>", self._select_table)

        preview = ttk.Frame(panel)
        preview.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=8)
        preview.columnconfigure(0, weight=1)
        preview.rowconfigure(0, weight=1)
        self.samples = ttk.Treeview(preview, show="headings", height=8)
        self.samples.grid(row=0, column=0, sticky="nsew")
        horizontal = ttk.Scrollbar(preview, orient="horizontal", command=self.samples.xview)
        vertical = ttk.Scrollbar(preview, orient="vertical", command=self.samples.yview)
        horizontal.grid(row=1, column=0, sticky="ew")
        vertical.grid(row=0, column=1, sticky="ns")
        self.samples.configure(xscrollcommand=horizontal.set, yscrollcommand=vertical.set)

        self.energy_picker = self._picker(panel, 3, "Energy (keV)")
        self.yield_picker = self._picker(panel, 4, "Yield")
        self.uncertainty_picker = self._picker(panel, 5, "Uncertainty")
        buttons = ttk.Frame(panel)
        buttons.grid(row=6, column=0, columnspan=2, sticky="e", pady=(8, 0))
        ttk.Button(buttons, text="Cancel", command=self.destroy).pack(side="left", padx=(0, 6))
        ttk.Button(buttons, text="Import", command=self._confirm).pack(side="left")

    @staticmethod
    def _picker(parent, row, label):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", padx=(0, 10), pady=3)
        picker = ttk.Combobox(parent, state="readonly")
        picker.grid(row=row, column=1, sticky="ew", pady=3)
        return picker

    def _select_sheet(self, _event=None):
        self.sheet_tables = [table for table in self.tables if table.sheet == self.sheet_picker.get()]
        self.table_picker.configure(values=[
            f"{'Header' if table.has_header else 'Data'} at row {table.first_row} ({len(table.rows)} data rows)" for table in self.sheet_tables
        ])
        self.table_picker.current(0)
        self._select_table()

    def _select_table(self, _event=None):
        table = self.sheet_tables[self.table_picker.current()]
        labels = [f"{i + 1}: {header}" if header else f"Column {i + 1}" for i, header in enumerate(table.headers)]
        self.samples.delete(*self.samples.get_children())
        self.samples.configure(columns=list(range(len(labels) + 1)))
        for i, label in enumerate(["Row", *labels]):
            self.samples.heading(i, text=label)
            self.samples.column(i, width=60 if i == 0 else 135, minwidth=45, stretch=False)
        for number, row in table.rows[:12]:
            values = ["" if value is None else value for value in (
                table.value(row, i) for i in range(len(labels))
            )]
            self.samples.insert("", "end", values=[number, *values])

        for picker in (self.energy_picker, self.yield_picker):
            picker.configure(values=["Select a column", *labels])
            picker.current(0)
        self.uncertainty_picker.configure(values=["None", *labels])
        self.uncertainty_picker.current(0)
        if table.mapping is not None:
            self.energy_picker.current(table.mapping.energy + 1)
            self.yield_picker.current(table.mapping.yield_ + 1)
            if table.mapping.uncertainty is not None:
                self.uncertainty_picker.current(table.mapping.uncertainty + 1)

    def _confirm(self):
        energy = self.energy_picker.current() - 1
        yield_ = self.yield_picker.current() - 1
        uncertainty = self.uncertainty_picker.current() - 1
        if min(energy, yield_) < 0:
            messagebox.showerror("Choose columns", "Select both energy and yield columns.", parent=self)
            return
        table = self.sheet_tables[self.table_picker.current()]
        try:
            self.result = validate_curve(table, ColumnMapping(energy, yield_, None if uncertainty < 0 else uncertainty))
        except ValueError as error:
            messagebox.showerror("Invalid curve data", str(error), parent=self)
            return
        self.destroy()

    def show(self):
        self.wait_window()
        return self.result
