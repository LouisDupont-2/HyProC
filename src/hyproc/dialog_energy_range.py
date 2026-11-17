import tkinter as tk
import math
from tkinter import messagebox, ttk


class EnergyRangeDialog(tk.Toplevel):
    def __init__(self, parent, offset: float = 0.0, e_min=None, e_max=None, step_size=2.5, sim_energy=None):
        super().__init__(parent)
        self.withdraw()
        self.transient(parent)
        self.title("Define energy range")

        self.offset = offset
        self.sim_energy = sim_energy or []
        self.result = None

        self._build_ui(e_min, e_max, step_size)
        self._position(parent)

        self.grab_set()
        self.deiconify()
        self.minsize(275, 275)

    def _build_ui(self, e_min, e_max, step_size):
        ttk.Label(
            self,
            text="Define an energy range to generate a simulated curve.",
            wraplength=250,
            justify="center",
        ).grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        ttk.Label(
            self,
            text=f"NOTE: The offset ({self.offset:.1f} keV) is subtracted for the calculation and added back to the displayed energies.",
            wraplength=250,
            justify="center",
        ).grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        ttk.Label(self, text="Minimum energy (keV):").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.min_entry = ttk.Entry(self, width=10)
        self.min_entry.insert(0, str(e_min) if e_min is not None else "")
        self.min_entry.grid(row=2, column=1, padx=10, pady=5)

        ttk.Label(self, text="Maximum energy (keV):").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.max_entry = ttk.Entry(self, width=10)
        self.max_entry.insert(0, str(e_max) if e_max is not None else "")
        self.max_entry.grid(row=3, column=1, padx=10, pady=5)

        ttk.Label(self, text="Step size (keV):").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.step_entry = ttk.Entry(self, width=10)
        self.step_entry.insert(0, str(round(step_size, 1)))
        self.step_entry.grid(row=4, column=1, padx=10, pady=5)

        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=(10, 5))

        ttk.Button(btn_frame, text="Cancel", command=self.cancel).grid(row=0, column=0, padx=5, ipadx=5, sticky="w")
        ttk.Button(btn_frame, text="Generate", command=self.generate).grid(row=0, column=1, padx=5, ipadx=5, sticky="e")

        self.use_sim_btn = ttk.Button(btn_frame, text="Use current simulated energies", command=self.use_sim_curve)
        self.use_sim_btn.grid(row=1, column=0, columnspan=2, padx=5, pady=5, ipadx=5)

    def _position(self, parent):
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")

    def generate(self):
        try:
            e_min = float(self.min_entry.get())
            e_max = float(self.max_entry.get())
            step_size = float(self.step_entry.get())
            if not all(math.isfinite(value) for value in (e_min, e_max, step_size)):
                messagebox.showerror("Invalid Range", "Energies and step size must be finite numbers.")
                return
            if e_min >= e_max:
                messagebox.showerror("Invalid Range", "Minimum energy must be less than maximum energy.")
                return
            if step_size <= 0:
                messagebox.showerror("Invalid Step Size", "Step size must be greater than zero.")
                return
            self.result = (e_min, e_max, step_size)
            self.destroy()
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numeric values for both energies and the step size.")

    def use_sim_curve(self):
        if not self.sim_energy:
            messagebox.showerror("No simulated curve", "There are no simulated energy values to reuse.")
            return
        energies = sorted([energy - self.offset for energy in self.sim_energy])
        if not energies:
            messagebox.showerror("No simulated curve", "There are no simulated energy values to reuse.")
            return
        self.result = (energies[0], energies[-1], len(energies), energies)
        self.destroy()

    def cancel(self):
        self.destroy()

    def show(self):
        self.wait_window()
        return self.result