import json
import math
import tkinter as tk
from tkinter import messagebox, ttk

import periodictable


class ReactionDialog(tk.Toplevel):
    def __init__(self, parent, settings_path: str):
        super().__init__(parent)
        self.parent = parent
        self.settings_path = settings_path
        self.withdraw()
        self.transient(parent)
        self.title("Reaction")
        self.resizable(False, False)
        self.columnconfigure(0, weight=1)

        try:
            with open(self.settings_path, "r", encoding="utf-8") as file:
                self.settings = json.load(file)
            reaction = self.settings["reaction"]
            resonance = self.settings["resonance"]
            self._reaction_values = {key: str(reaction[key]) for key in ("Z1", "A1", "Z2", "A2")}
            self._resonance_values = {
                key: str(resonance[key]) for key in ("E_R", "Gamma", "Sigma")
            }
        except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
            messagebox.showerror("Reaction settings", f"Could not load reaction settings:\n\n{exc}", parent=self)
            self.destroy()
            return

        self.entries: dict[str, ttk.Entry] = {}
        self._build_ui()
        self._position(parent)
        self.grab_set()
        self.deiconify()

    def _build_ui(self)->None:
        reaction_frame = ttk.LabelFrame(self, text="Reaction")
        reaction_frame.grid(row=0, column=0, padx=12, pady=(12, 6), sticky="ew")

        reaction_fields = (
            ("Z1", "Projectile atomic number (Z1)", self._reaction_values["Z1"]),
            ("A1", "Projectile mass number (A1)", self._reaction_values["A1"]),
            ("Z2", "Target atomic number (Z2)", self._reaction_values["Z2"]),
            ("A2", "Target mass number (A2)", self._reaction_values["A2"]),
        )
        self._add_fields(reaction_frame, reaction_fields, start_row=0)

        resonance_frame = ttk.LabelFrame(self, text="Resonance")
        ttk.Label(resonance_frame, text="Resonance shape: Lorentzian").grid(
            row=0, column=0, columnspan=2, padx=10, pady=2, sticky="w"
        )
        resonance_frame.grid(row=1, column=0, padx=12, pady=6, sticky="ew")
        resonance_fields = (
            ("E_R", "Resonance energy E_R (keV)", self._resonance_values["E_R"]),
            ("Gamma", "Resonance width Gamma_R (keV)", self._resonance_values["Gamma"]),
            ("Sigma", "Peak cross section Sigma_R (barn)", self._resonance_values["Sigma"]),
        )
        self._add_fields(resonance_frame, resonance_fields, start_row=1)

        buttons = ttk.Frame(self)
        buttons.grid(row=2, column=0, padx=12, pady=(6, 12))
        ttk.Button(buttons, text="Cancel", command=self.destroy).pack(side="left", padx=3)
        ttk.Button(buttons, text="Confirm", command=self.save_settings).pack(side="left", padx=3)

    def _add_fields(
        self,
        frame: ttk.LabelFrame,
        fields: tuple[tuple[str, str, str], ...],
        start_row: int = 0,
    )->None:
        frame.columnconfigure(1, weight=1)
        for row, (key, label, value) in enumerate(fields, start=start_row):
            ttk.Label(frame, text=label).grid(row=row, column=0, padx=10, pady=2, sticky="w")
            entry = ttk.Entry(frame, width=10)
            entry.insert(0, value)
            entry.grid(row=row, column=1, padx=10, pady=2, sticky="ew")
            self.entries[key] = entry

    def _position(self, parent)->None:
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

    def save_settings(self)->None:
        try:
            reaction_values = {
                key: int(self.entries[key].get().strip()) for key in ("Z1", "A1", "Z2", "A2")
            }
            for z_key, a_key in (("Z1", "A1"), ("Z2", "A2")):
                z_value = reaction_values[z_key]
                a_value = reaction_values[a_key]
                if not 1 <= z_value <= 118 or a_value <= 0:
                    raise ValueError(f"{z_key} must be between 1 and 118 and {a_key} must be positive.")
                isotope = periodictable.elements[z_value][a_value]
                if isotope.mass is None or not math.isfinite(float(isotope.mass)):
                    raise ValueError(f"No isotope mass is available for {z_key}={z_value}, {a_key}={a_value}.")

            resonance_values = {}
            for key in ("E_R", "Gamma", "Sigma"):
                value = float(self.entries[key].get().strip())
                if not math.isfinite(value):
                    raise ValueError(f"{key} must be a finite number.")
                resonance_values[key] = value
            if resonance_values["E_R"] <= 0 or resonance_values["Gamma"] <= 0 or resonance_values["Sigma"] <= 0:
                raise ValueError("E_R, Gamma, and Sigma must be greater than zero.")

            self.settings["reaction"].update({key: str(value) for key, value in reaction_values.items()})
            self.settings["resonance"].update(resonance_values)
            with open(self.settings_path, "w", encoding="utf-8") as file:
                json.dump(self.settings, file, indent=4)

            self.parent.reload_reaction_settings()
            self.destroy()
        except (OSError, KeyError, TypeError, ValueError) as exc:
            messagebox.showerror("Save failed", f"Could not save reaction settings:\n\n{exc}", parent=self)
