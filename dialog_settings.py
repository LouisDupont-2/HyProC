import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import json


class SettingsDialog(tk.Toplevel):
    def __init__(self, parent, settings_path: str):
        super().__init__(parent)
        self.parent = parent
        self.settings_path = settings_path
        self.withdraw()
        self.transient(parent)
        self.title("Settings")
        self.columnconfigure(1, weight=1)

        # Load config
        with open(self.settings_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)

        self._build_ui()
        self._position(parent)

        self.grab_set()
        self.deiconify()
        self.minsize(400, 175)

    def _build_ui(self):
        label_width = 25
        entry_width = 40
        browse_width = 5

        ttk.Label(self, text="SRIM Path:", width=label_width).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.srim_entry = ttk.Entry(self, width=entry_width + browse_width)
        self.srim_entry.insert(0, self.config.get("SRIM_path", ""))
        self.srim_entry.grid(row=0, column=1, padx=(10, 0), pady=5, sticky="ew")

        def browse_srim():
            folder = filedialog.askdirectory(initialdir=self.srim_entry.get())
            if folder:
                self.srim_entry.delete(0, tk.END)
                self.srim_entry.insert(0, folder)

        ttk.Button(self, text="...", command=browse_srim, width=0).grid(row=0, column=2, padx=(0, 5), pady=5)

        ttk.Label(self, text="HyProC data save path:", width=label_width).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.save_entry = ttk.Entry(self, width=entry_width + browse_width)
        self.save_entry.insert(0, self.config.get("save_path", ""))
        self.save_entry.grid(row=1, column=1, padx=(10, 0), pady=5, sticky="ew")

        def browse_save():
            folder = filedialog.askdirectory(initialdir=self.save_entry.get())
            if folder:
                self.save_entry.delete(0, tk.END)
                self.save_entry.insert(0, folder)

        ttk.Button(self, text="...", command=browse_save, width=0).grid(row=1, column=2, padx=(0, 5), pady=5)

        # Column names
        ttk.Label(self, text="Energy column header:", width=label_width).grid(row=2, column=0, padx=10, pady=(5, 0), sticky="w")
        self.energy_entry = ttk.Entry(self, width=entry_width + browse_width)
        self.energy_entry.insert(0, self.config.get("import_curve", {}).get("columns", {}).get("energy", ""))
        self.energy_entry.grid(row=2, column=1, columnspan=2, padx=10, pady=(5, 0), sticky="ew")

        ttk.Label(self, text="Yield column header:", width=label_width).grid(row=3, column=0, padx=10, pady=0, sticky="w")
        self.yield_entry = ttk.Entry(self, width=entry_width + browse_width)
        self.yield_entry.insert(0, self.config.get("import_curve", {}).get("columns", {}).get("yield", ""))
        self.yield_entry.grid(row=3, column=1, columnspan=2, padx=10, pady=0, sticky="ew")

        ttk.Label(self, text="Yield error column header:", width=label_width).grid(row=4, column=0, padx=10, pady=(0, 5), sticky="w")
        self.yield_err_entry = ttk.Entry(self, width=entry_width + browse_width)
        self.yield_err_entry.insert(0, self.config.get("import_curve", {}).get("columns", {}).get("yield_err", ""))
        self.yield_err_entry.grid(row=4, column=1, columnspan=2, padx=10, pady=(0, 5), sticky="ew")

        ttk.Button(self, text="Save", command=self.save_settings).grid(row=5, column=0, columnspan=3, pady=10)

    def _position(self, parent):
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

    def save_settings(self):
        try:
            # Update config dict
            self.config["SRIM_path"] = self.srim_entry.get()
            self.config["save_path"] = self.save_entry.get()
            if "import_curve" not in self.config:
                self.config["import_curve"] = {"columns": {}}
            if "columns" not in self.config["import_curve"]:
                self.config["import_curve"]["columns"] = {}
            self.config["import_curve"]["columns"]["energy"] = self.energy_entry.get()
            self.config["import_curve"]["columns"]["yield"] = self.yield_entry.get()
            self.config["import_curve"]["columns"]["yield_err"] = self.yield_err_entry.get()

            with open(self.settings_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)

            # Update parent's Z2 if possible
            try:
                self.parent.Z2 = self.parent.load_Z2(self.settings_path)
            except Exception:
                pass

            self.destroy()
        except Exception as e:
            messagebox.showerror("Save failed", f"Could not save settings:\n{e}")

    def show(self):
        self.wait_window()
        return
