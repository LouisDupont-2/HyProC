import tkinter as tk
from tkinter import filedialog, messagebox,ttk
import periodictable
import json
import pandas as pd
from matplotlib.figure import Figure
import numpy as np
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,NavigationToolbar2Tk)
import os
import subprocess
import sys
from datetime import datetime
import threading
import traceback
from typing import Sequence, Literal

from class_models import Element, Layer, Target
import UI_geometry
import mod2
import mod3 
import mod4        

def count_datapoints(df_raw: pd.DataFrame, header_row: int) -> int:
    # Count consecutive non-empty rows after the header
    count = 0
    for i in range(header_row + 1, len(df_raw)):
        row = df_raw.iloc[i]
        if row.isnull().all():
            break
        count += 1
    return count  

# Main GUI application
class GUI_App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.script_dir = os.path.dirname(os.path.abspath(__file__)) 
        self.settings_path = os.path.join(self.script_dir, 'settings.json')
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H-%M-%S")

        self.title("HyProC")
        self.geometry("850x900")

        self.style = ttk.Style(self)

        # Define your custom styles
        self.style.configure("Default.TButton", background="#f0f0f0", foreground="black")
        self.style.configure("Working.TButton", background="orange", foreground="black")

        # Load settings for constants
        self.Z2 = self.load_Z2(self.settings_path)
        self.Z2_profile = None

        self.runNbr = 0

        self.target = Target()
        self.selected_layer_index = 0
        self.selected_el_index = 0

        self.std_target = Target()
        self.selected_Std_index = 0

        self.start_ctr = 0
        self.visible_count = 9
        self.chi_val=[]

        UI_geometry.create_widgets(self)
        self.refresh_layer_list()
        self.refresh_element_list() 
        self.refresh_Std_list()
        self.update_exc_plot()
        self.update_chi_plot()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def load_Z2(self, settings_path)->int:
        """
        Loads Z2 (target atomic number) from settings.
        """
        with open(settings_path, 'r', encoding="utf-8") as f:
            settings = json.load(f)
        Z2 = int(settings["reaction"]["Z2"])
        return Z2

    def update_chi_plot(self)->None:
        self.ax1.clear()
        visible_values = self.chi_val[self.start_ctr:self.start_ctr + self.visible_count]
        y_positions = range(len(visible_values))

        bars = self.ax1.barh(y_positions, visible_values, color="cornflowerblue", height=0.8)

        self.ax1.invert_yaxis()
        self.ax1.set_yticks(y_positions)
        self.ax1.set_yticklabels([str(i + self.start_ctr) for i in y_positions])
        self.ax1.set_ylim(self.visible_count - 0.5, -0.5)

        for i, (bar, val) in enumerate(zip(bars, visible_values)):
            self.ax1.text(val + 2, bar.get_y() + bar.get_height() / 2,
                    f"{val}", va='center', ha='left', fontsize=7)

        if len(self.chi_val)==0:
            xmax = 10
        else:
            xmax = max(visible_values) + 10
        self.ax1.set_xlim(0, xmax)
        self.ax1.xaxis.set_visible(False)
        for spine in self.ax1.spines.values():
            spine.set_visible(False)

        # This tightens layout
        #self.figure1.subplots_adjust(left=0.25, right=0.95, top=0.95, bottom=0.05)
        self.canvas1.draw()

    def scroll_up(self)->None:
        if self.start_ctr > 0:
            self.start_ctr -= 1
            self.update_chi_plot()

    def scroll_down(self)->None:
        if self.start_ctr + self.visible_count < len(self.chi_val):
            self.start_ctr += 1
            self.update_chi_plot()

    def update_exc_plot(self, event=None)->None:
        self.ax0.clear()
        
        # Check if experimental curve data is available and valid
        check1 = (
            hasattr(self, 'exp_energy') and hasattr(self, 'ec_yield') and hasattr(self, 'ec_yErr') and
            isinstance(self.exp_energy, list) and isinstance(self.ec_yield, list) and isinstance(self.ec_yErr, list) and
            len(self.exp_energy) > 0 and len(self.ec_yield) > 0 and len(self.ec_yErr) > 0
        )
        
        # Check if simulated curve data is available and valid
        check2 = (
            hasattr(self, 'sim_energy') and hasattr(self, 'sim_curve') and
            isinstance(self.sim_energy, list) and isinstance(self.sim_curve, list) and
            len(self.sim_energy) > 0 and len(self.sim_curve) > 0
        )
        
        if check1:
            self.ax0.scatter(self.exp_energy, self.ec_yield, label='Exp', marker='.', color='tab:blue')
            self.ax0.errorbar(self.exp_energy, self.ec_yield, self.ec_yErr, fmt='none', color='tab:blue')
        
        if check2:
            self.ax0.plot(self.sim_energy, self.sim_curve, label='Sim', linestyle='--', marker='.', color='tab:orange')
        
        if check1 or check2:  # Only add legend if at least one curve is plotted
            self.ax0.legend(loc='best')
        
        self.ax0.set_xlabel("Energy (keV)")
        self.ax0.set_ylabel("Yield (Count/µC)")
        self.ax0.set_ylim(bottom=0)
        self.ax0.grid(alpha=0.4)
        self.canvas.draw()       

    # -------------------------------------------
    # GUI updates in top frames
    def refresh_layer_list(self)->None:
        if self.selected_layer_index >= len(self.target["layers"]):
            self.selected_layer_index = max(0, len(self.target["layers"]) - 1)
        self.layer_listbox.delete(0, tk.END)
        for i, layer in enumerate(self.target["layers"]):
            data = sorted(layer["elements"], key=lambda el: el["percent_at"], reverse=True)
            elements_str = ', '.join(f"{periodictable.elements[el['Z']].symbol}{round(el['percent_at'])}" for el in data)
            self.layer_listbox.insert(
                tk.END,
                f"Layer {i + 1}: {layer['areal_density']} TFU ({elements_str})"
            )
        self.layer_listbox.select_set(self.selected_layer_index)

        # When starting the interface, filling in the textboxs:
        current_layer = self.target["layers"][self.selected_layer_index]
        self.AD_entry.delete(0, tk.END)
        self.AD_entry.insert(0,str(current_layer["areal_density"])) 

    def refresh_element_list(self)->None:
        if self.selected_el_index >= len(self.target["layers"][self.selected_layer_index]["elements"]):
            self.selected_el_index = max(0, len(self.target["layers"][self.selected_layer_index]["elements"]) - 1)
        self.elem_listbox.delete(0, tk.END)
        current_layer = self.target["layers"][self.selected_layer_index]
        for el in current_layer["elements"]:
            self.elem_listbox.insert(
                tk.END,
                f"{periodictable.elements[el['Z']].symbol} (Z={el['Z']}), {el['percent_at']:.2f} % at."
                )
        self.elem_listbox.select_set(self.selected_el_index)

        # When starting the interface, filling in the textboxs:
        element = current_layer["elements"][self.selected_el_index]
        self.element_Z_entry.delete(0, tk.END)
        self.element_Z_entry.insert(0, str(element["Z"])) 
        self.composition_percent_entry.delete(0, tk.END)
        self.composition_percent_entry.insert(0, str(element["percent_at"]))

    def refresh_Std_list(self)->None:
        if self.selected_Std_index >= len(self.std_target["layers"][0]["elements"]):
            self.selected_Std_index = max(0, len(self.std_target["layers"][0]["elements"]) - 1)
        self.Std_elem_listbox.delete(0, tk.END)
        current_layer = self.std_target["layers"][0]
        for el in current_layer["elements"]:
            self.Std_elem_listbox.insert(
                tk.END,
                f"{periodictable.elements[el['Z']].symbol} (Z={el['Z']}), {el['percent_at']:.2f} % at."
                )
        self.Std_elem_listbox.select_set(self.selected_Std_index)

        # When starting the interface, filling in the textboxs:
        element = current_layer["elements"][self.selected_Std_index]
        self.Std_element_Z_entry.delete(0, tk.END)
        self.Std_element_Z_entry.insert(0, str(element["Z"])) 
        self.Std_composition_percent_entry.delete(0, tk.END)
        self.Std_composition_percent_entry.insert(0, str(element["percent_at"]))

    # -------------------------------------------
    # Target Config Commands
    def on_add_layer_click(self)->None:
        self.target.add_layer()
        self.selected_layer_index = len(self.target["layers"]) - 1
        self.selected_el_index = 0
        self.refresh_layer_list()
        self.refresh_element_list()

    def on_remove_layer_click(self)->None:
        self.target.remove_layer(self.selected_layer_index)
        self.selected_layer_index = max(0, self.selected_layer_index - 1)
        self.selected_el_index = 0
        self.refresh_layer_list()
        self.refresh_element_list()

    def on_duplicate_layer_click(self)->None:
        self.target.duplicate_layer(self.selected_layer_index)
        self.selected_layer_index = self.selected_layer_index + 1
        self.refresh_layer_list()
        self.refresh_element_list()

    def on_move_layer_up_click(self)->None:
        self.target.move_layer_up(self.selected_layer_index)
        self.selected_layer_index -= 1 if self.selected_layer_index > 0 else 0
        self.refresh_layer_list()
        self.refresh_element_list()

    def on_move_layer_down_click(self)->None:
        self.target.move_layer_down(self.selected_layer_index)
        self.selected_layer_index += 1 if self.selected_layer_index < len(self.target["layers"]) - 1 else 0
        self.refresh_layer_list()
        self.refresh_element_list()


    def on_add_element_click(self, target_type: Literal['target', 'std'] = 'target')->None:
        try:
            if target_type == 'target':
                self.target["layers"][self.selected_layer_index].add_element()
                self.selected_el_index = len(self.target["layers"][self.selected_layer_index]["elements"]) - 1
                self.refresh_element_list()
                self.refresh_layer_list()
            elif target_type == 'std':
                self.std_target["layers"][0].add_element()
                self.selected_Std_index = len(self.std_target["layers"][0]["elements"]) - 1
                self.refresh_Std_list()
        except ValueError:
            pass 

    def on_remove_element_click(self, target_type: Literal['target', 'std'] = 'target')->None:
        if target_type == 'target':
            self.target["layers"][self.selected_layer_index].remove_element(self.selected_el_index)
            self.selected_el_index = max(0, self.selected_el_index - 1)
            self.refresh_element_list()
            self.refresh_layer_list()
        elif target_type == 'std':
            self.std_target["layers"][0].remove_element(self.selected_Std_index)
            self.selected_Std_index = max(0, self.selected_Std_index - 1)
            self.refresh_Std_list()                

    def on_lock_and_normalize_click(self, target_type: Literal['target', 'std'] = 'target')->None:
        if target_type=='target':
            current_layer = self.target["layers"][self.selected_layer_index]
            index = self.selected_el_index
        elif target_type=='std':
            current_layer = self.std_target["layers"][0]
            index = self.selected_Std_index
        current_layer.lock_and_normalize(index)

        if target_type=='target':
            self.refresh_element_list()
            self.refresh_layer_list()
        elif target_type=='std':
            self.refresh_Std_list()

    # -------------------------------------------
    ## Selection handlers
    def on_layer_select(self, event=None)->None:
        """
        Updates the layer text entries when selecting a layer in the listbox
        """
        selected_layer_index = self.layer_listbox.curselection()
        if not selected_layer_index:
            return
        selected_layer_index = selected_layer_index[0]
        self.selected_layer_index = selected_layer_index
        current_layer = self.target["layers"][selected_layer_index]
        if self.selected_el_index >= len(current_layer["elements"]):
            self.selected_el_index = max(0, len(current_layer["elements"]) - 1)
        # Display the selected layer's thickness in the entry
        self.AD_entry.delete(0, tk.END)
        self.AD_entry.insert(0, str(current_layer["areal_density"]))

        self.refresh_layer_list()
        self.refresh_element_list()

    def on_layer_entry_update(self, event=None)->None:
        """
        Updates the layer listbox when values in the text entries are modified
        """
        selected = self.layer_listbox.curselection()
        if not selected:
            return
        try:
            new_AD = float(self.AD_entry.get())
            if new_AD > 0 :
                current_layer = self.target["layers"][self.selected_layer_index]
                current_layer["areal_density"] = new_AD
                self.refresh_layer_list()
            else:
                print("Value must be positive and non-zero.")
        except ValueError:
            print("Invalid input for areal density.")

    def on_element_select(self, event)->None:
        """
        Updates the element text entries when selecting an element in the listbox
        """
        selected_el_index = self.elem_listbox.curselection()
        if not selected_el_index:
            return
        selected_el_index = selected_el_index[0]
        self.selected_el_index = selected_el_index
        current_layer = self.target["layers"][self.selected_layer_index]
        element = current_layer["elements"][selected_el_index]

        self.element_Z_entry.delete(0, tk.END)
        self.element_Z_entry.insert(0, str(element["Z"]))
        self.composition_percent_entry.delete(0, tk.END)
        self.composition_percent_entry.insert(0, str(element["percent_at"]))
        self.refresh_layer_list()
        self.refresh_element_list()

    def on_element_entry_update(self, event=None, entry_type:Literal['Z', 'percent_at']=None)->None:
        """
        Updates the element listbox when values in the text entries are modified
        """
        selected = self.elem_listbox.curselection()  # Get selected element in the list
        if not selected:
            return
        current_layer = self.target["layers"][self.selected_layer_index]
        element = current_layer["elements"][self.selected_el_index]  
        try:
            if entry_type == 'Z':
                new_value = int(self.element_Z_entry.get())
                if 0 < new_value < 119:  # Make sure the element exist
                    element["Z"] = new_value  
            elif entry_type == 'percent_at':
                new_value = float(self.composition_percent_entry.get()) 
                if 0 <= new_value <= 100:  
                    element["percent_at"] = new_value  
            else:
                print("Unknown entry type")
            self.refresh_element_list()
            self.refresh_layer_list()
        except ValueError:
            print("Invalid input. Please enter a valid number.")

    def on_std_element_select(self, event)->None:
        """
        Updates the standard text entries when selecting an element in the listbox
        """
        selected = self.Std_elem_listbox.curselection()
        if not selected:
            return
        selected = selected[0]
        self.selected_Std_index = selected
        current_layer = self.std_target["layers"][0]
        element = current_layer["elements"][selected]

        self.Std_element_Z_entry.delete(0, tk.END)
        self.Std_element_Z_entry.insert(0, str(element["Z"]))
        self.Std_composition_percent_entry.delete(0, tk.END)
        self.Std_composition_percent_entry.insert(0, str(element["percent_at"]))
        self.refresh_Std_list()

    def on_std_element_entry_update(self, event=None, entry_type:Literal['Z', 'percent_at']=None)->None:
        """
        Updates the standard listbox when one of the text entry is changed
        """
        selected = self.Std_elem_listbox.curselection()  # Get Std selected element in the list
        if not selected:
            return

        current_layer = self.std_target["layers"][0]
        element = current_layer["elements"][self.selected_Std_index]  

        try:
            if entry_type == 'Z':
                new_value = int(self.Std_element_Z_entry.get())  
                if 0 < new_value < 119:  # Make sure the element exist
                    element["Z"] = new_value  
            elif entry_type == 'percent_at':
                new_value = float(self.Std_composition_percent_entry.get()) 
                if 0 <= new_value <= 100:  
                    element["percent_at"] = new_value  
            else:
                print("Unknown entry type")

            self.refresh_Std_list()

        except ValueError:
            print("Invalid input. Please enter a valid number.")

    # -------------------------------------------  
    def load_curve(self)->None:
        file_path = filedialog.askopenfilename(
            title="Load Excitation Curve",
            filetypes=[
                ("Curve Files", "*.xlsx *.xls *.csv *.txt"),
                ("Excel Files", "*.xlsx *.xls"),
                ("Plain text Files", "*.csv" "*.txt"),
                ("All Files", "*.*")
            ]
        )
        if not file_path:
            return 
        try:
            with open(self.settings_path, 'r', encoding="utf-8") as f:
                config = json.load(f)["import_curve"]["columns"]

            ext = os.path.splitext(file_path)[1].lower()
            if ext in [".xlsx", ".xls"]:
                xl = pd.ExcelFile(file_path)
                cols = [config["energy"], config["yield"]]  # Only require energy and yield headers

                matching_sheets = []
                for sheet in xl.sheet_names:
                    df_raw = pd.read_excel(file_path, sheet_name=sheet, header=None, engine='openpyxl')
                    if df_raw.isin(cols).any(axis=None):
                        matching_sheets.append(sheet)
                
                if len(matching_sheets) == 0:
                    messagebox.showerror("Loading Error", "No sheet containing the expected headers was found.")
                    return
                elif len(matching_sheets) == 1:
                    sheet = matching_sheets[0]
                else:
                    sheet = self.ask_sheet(file_path, matching_sheets)
                    if sheet is None:
                        return

                df_raw = pd.read_excel(file_path, sheet_name=sheet, header=None, engine='openpyxl')
                header_rows = df_raw[df_raw.apply(lambda row: all(col in row.values for col in cols), axis=1)].index.tolist()
                if len(header_rows) == 0:
                    messagebox.showerror("Loading Error", "No table containing the expected headers was found.")
                    return
                elif len(header_rows) == 1:
                    header_row = header_rows[0]
                    ndata = count_datapoints(df_raw, header_row)
                else:
                    result = self.ask_table(df_raw, header_rows, cols)
                    if result is None:
                        return
                    header_row, ndata = result           

                df = pd.read_excel(file_path, sheet_name=sheet, skiprows=range(header_row), header=0, nrows=ndata, engine='openpyxl')
            else:
                if ext == ".csv":
                    df = pd.read_csv(file_path, comment='#', engine='python')
                else:
                    df = pd.read_csv(file_path, comment='#', sep=r'[\t ]+', engine='python', header=None)

                if config["energy"] not in df.columns or config["yield"] not in df.columns:
                    if len(df.columns) >= 2:
                        original_columns = list(df.columns)
                        df.rename(columns={original_columns[0]: config["energy"], original_columns[1]: config["yield"]}, inplace=True)
                        if len(original_columns) > 2:
                            df.rename(columns={original_columns[2]: config["yield_err"]}, inplace=True)
                        elif config["yield_err"] not in df.columns:
                            df[config["yield_err"]] = 0.0
                    else:
                        raise ValueError("Curve file must contain at least two columns (energy and yield).")

                if config["yield_err"] not in df.columns:
                    df[config["yield_err"]] = 0.0

            df = df.dropna(subset=[config["energy"], config["yield"], config["yield_err"]])
            df = df[pd.to_numeric(df[config["energy"]], errors='coerce').notna()]

            self.exp_energy = df[config["energy"]].astype(float).tolist()
            self.ec_yield = df[config["yield"]].astype(float).tolist()
            self.ec_yErr = df[config["yield_err"]].astype(float).tolist()

            sorted_indices = sorted(range(len(self.exp_energy)), key=lambda i: self.exp_energy[i]) 
            self.exp_energy = [self.exp_energy[i] for i in sorted_indices]
            self.ec_yield = [self.ec_yield[i] for i in sorted_indices]
            self.ec_yErr = [self.ec_yErr[i] for i in sorted_indices]

        except PermissionError:
            messagebox.showerror("Permission Denied", 
            f"Cannot open the file:\n{file_path}\n\n"
            "Please close it in Excel or any other program and try again.")
            print("PermissionError: File is likely opened in another application.")
        except ValueError as e:
            messagebox.showerror("Loading Error", f"Failed to load the data.\n{e}")
        self.update_exc_plot()

    def ask_sheet(self, file_path:str, sheet_names:list)->str:
        """
        If multiple sheets are found in the loaded Excel file, ask the user which one to load.
        """
        popup = tk.Toplevel()
        popup.title("Select Sheet")
        popup.transient(self)
        popup.grab_set()
    
        ttk.Label(popup, text="Select sheet to load:").pack(pady=5)
        
        selected = tk.StringVar(value=sheet_names[0])
        dropdown = ttk.Combobox(popup, textvariable=selected, values=sheet_names, state="readonly")
        dropdown.pack(pady=5)
    
        result = [None]
    
        def confirm():
            result[0] = selected.get()
            popup.destroy()

        ttk.Button(popup, text="Confirm", command=confirm).pack(pady=5)

        # Centering the popup on main window
        popup.withdraw()
        popup.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - (popup.winfo_width() // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (popup.winfo_height() // 2)
        popup.geometry(f"250x120+{x}+{y}")
        popup.deiconify()
        
        popup.wait_window()  # Blocks until popup is closed
        return result[0]

    def ask_table(self, df_raw: pd.DataFrame, header_rows: list[int], cols: list[str])-> tuple[int, int]:
        popup = tk.Toplevel()
        popup.transient(self)
        popup.grab_set()
        popup.title("Select Table")

        ttk.Label(popup, text="Multiple tables found, select one:").pack(pady=5)

        options = [f"Table {i+1} (header on row {row+1}, {count_datapoints(df_raw, row)} datapoints)"
                   for i, row in enumerate(header_rows)]

        selected = tk.StringVar(value=options[0])
        dropdown = ttk.Combobox(popup, textvariable=selected, values=options, state="readonly", width=50)
        dropdown.pack(pady=5)

        result = [None]

        def confirm():
            idx = options.index(selected.get())
            result[0] = (header_rows[idx], count_datapoints(df_raw, header_rows[idx]))
            popup.destroy()

        ttk.Button(popup, text="Confirm", command=confirm).pack(pady=5)

        popup.withdraw()
        popup.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - (popup.winfo_width() // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (popup.winfo_height() // 2)
        popup.geometry(f"400x120+{x}+{y}")
        popup.deiconify()

        popup.wait_window()
        return result[0]
    
    def load_std(self)->None:
        file_path = filedialog.askopenfilename(title="Load Standard", filetypes=[("JSON files", "*.json")])
        if not file_path:
            return
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)

            layers = [Layer(data=layer) for layer in data["layers"]]

            if len(layers) > 1:
                index = self.ask_layer(layers)
                if index is None:
                    return
                selected_layer = layers[index]
            else:
                selected_layer = layers[0]

            self.std_target["layers"] = [selected_layer]
            self.std_target["layers"][0]["areal_density"] = 1500.0

            if not mod2.check_srim_path(self.settings_path):
                messagebox.showerror("Loading standard failed", "SRIM path not found.\n\nPlease check your settings.")
                return
            self.std_target["layers"][0]["stopping"] = mod2.calc_stopping_power(self.std_target["layers"][0], 6385)

            # Check for the element of interest
            percent_at = self.std_target["layers"][0].find_element(self.Z2)
            if percent_at is None or percent_at == 0:
                messagebox.showerror("Calculation failed", f"Standard calculation error.\n\nNo {periodictable.elements[self.Z2].name.capitalize()} in the standard.")
                return

            print('Standard loaded')
            self.refresh_Std_list()
            self.TargetStd_notebook.select(self.Std_frame)  # Switch to the relevent tab

        except ValueError as e:
            messagebox.showerror("Loading Error", f"Couldn't load the data.\n\n{e}")

    def ask_layer(self, layers:list)->int:
        """"
        If multiple layers are found in the loaded standard, ask the user which one to keep.
        """
        popup = tk.Toplevel()
        popup.transient(self)
        popup.grab_set()
        popup.title("Select Layer")

        ttk.Label(popup, text="Multiple layers found. A standard should have a uniform composition and thus only one layer.\n\nSelect which layer to keep:", wraplength=300).pack(pady=5)

        def layer_label(i, layer):
            elements = sorted(layer.get("elements", []), key=lambda e: e.get("percent_at", 0), reverse=True)
            elements_str = ', '.join(f"{periodictable.elements[el['Z']].symbol}{int(el['percent_at'])}" for el in elements)
            return f"Layer {i+1}: {layer['areal_density']} TFU ({elements_str})"

        options = [layer_label(i, layer) for i, layer in enumerate(layers)]
        selected = tk.StringVar(value=options[0])
        dropdown = ttk.Combobox(popup, textvariable=selected, values=options, state="readonly", width=50)
        dropdown.pack(pady=5)

        result = [None]

        def confirm():
            result[0] = options.index(selected.get())
            popup.destroy()

        ttk.Button(popup, text="Confirm", command=confirm).pack(pady=5)

        # Centering the popup on main window
        popup.withdraw()
        popup.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - (popup.winfo_width() // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (popup.winfo_height() // 2)
        popup.geometry(f"400x150+{x}+{y}")
        popup.deiconify()

        popup.wait_window()
        return result[0]

    def load_target(self)->None:
        file_path = filedialog.askopenfilename(title="Load Target", filetypes=[("JSON files", "*.json")])
        if not file_path:
            return
        try:
            with open(file_path,'r') as f:
                data = json.load(f)
            self.target["layers"] = [Layer(data=layer) for layer in data["layers"]]
            print('Target loaded')
        except ValueError:
            print("Couldn't load the data.")
        self.refresh_layer_list()
        self.refresh_element_list()
        self.TargetStd_notebook.select(self.target_frame)  # Switch to the relevent tab

    def generate_exp_curve(self)->None:
        if not hasattr(self, "sim_curve"):
            messagebox.showerror("Generate curve","No simulation curve data to load as experimental curve.")
            return
        self.ec_yield = self.sim_curve
        self.ec_yErr = np.zeros(len(self.exp_energy))  # Assuming no error bars for the generated curve
        self.update_exc_plot()
    
    def on_remove_exp(self)->None:
        self.ec_yield = []
        self.ec_yErr = []
        self.update_exc_plot()

    def on_remove_sim(self)->None:
        self.sim_curve = []
        self.sim_energy = []
        self.update_exc_plot()

    def reset_chi_history(self)->None:
        self.chi_val = []
        self.start_ctr = 0
        self.update_chi_plot()

    def open_settings(self):
        popup = tk.Toplevel()
        popup.transient(self)
        popup.grab_set()
        popup.title("Settings")
        popup.columnconfigure(1, weight=1)

        with open(self.settings_path, 'r', encoding="utf-8") as f:
            config = json.load(f)

        label_width = 25
        entry_width = 40
        browse_width = 5

        # Paths
        ttk.Label(popup, text="SRIM Path:",width=label_width).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        srim_entry = ttk.Entry(popup, width=entry_width+browse_width)
        srim_entry.insert(0, config["SRIM_path"])
        srim_entry.grid(row=0, column=1, padx=(10,0), pady=5, sticky="ew")
        def browse_srim():
            folder = filedialog.askdirectory(initialdir=srim_entry.get())
            if folder:
                srim_entry.delete(0, tk.END)
                srim_entry.insert(0, folder)
        ttk.Button(popup, text="...", command=browse_srim, width=0).grid(row=0, column=2, padx=(0,5), pady=5)

        ttk.Label(popup, text="HyProC data save path:",width=label_width).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        save_entry = ttk.Entry(popup, width=entry_width+browse_width)
        save_entry.insert(0, config["save_path"])
        save_entry.grid(row=1, column=1, padx=(10,0), pady=5, sticky="ew")
        def browse_save():
            folder = filedialog.askdirectory(initialdir=save_entry.get())
            if folder:
                save_entry.delete(0, tk.END)
                save_entry.insert(0, folder)
        ttk.Button(popup, text="...", command=browse_save, width=0).grid(row=1, column=2, padx=(0,5), pady=5)        

        # Column names
        ttk.Label(popup, text="Energy column header:",width=label_width).grid(row=2, column=0, padx=10, pady=(5,0), sticky="w")
        energy_entry = ttk.Entry(popup, width=entry_width+browse_width)
        energy_entry.insert(0, config["import_curve"]["columns"]["energy"])
        energy_entry.grid(row=2, column=1, columnspan=2, padx=10, pady=(5,0), sticky="ew")

        ttk.Label(popup, text="Yield column header:",width=label_width).grid(row=3, column=0, padx=10, pady=0, sticky="w")
        yield_entry = ttk.Entry(popup, width=entry_width+browse_width)
        yield_entry.insert(0, config["import_curve"]["columns"]["yield"])
        yield_entry.grid(row=3, column=1, columnspan=2, padx=10, pady=0, sticky="ew")

        ttk.Label(popup, text="Yield error column header:",width=label_width).grid(row=4, column=0, padx=10, pady=(0,5), sticky="w")
        yield_err_entry = ttk.Entry(popup, width=entry_width+browse_width)
        yield_err_entry.insert(0, config["import_curve"]["columns"]["yield_err"])
        yield_err_entry.grid(row=4, column=1, columnspan=2, padx=10, pady=(0,5), sticky="ew")

        def save_settings():
            config["SRIM_path"] = srim_entry.get()
            config["save_path"] = save_entry.get()
            config["import_curve"]["columns"]["energy"] = energy_entry.get()
            config["import_curve"]["columns"]["yield"] = yield_entry.get()
            config["import_curve"]["columns"]["yield_err"] = yield_err_entry.get()
            with open(self.settings_path, 'w', encoding="utf-8") as f:
                json.dump(config, f, indent=4)
            self.Z2 = self.load_Z2(self.settings_path)
            popup.destroy()

        ttk.Button(popup, text="Save", command=save_settings).grid(row=5, column=0, columnspan=3, pady=10)

        popup.withdraw()
        popup.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - (popup.winfo_width() // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (popup.winfo_height() // 2)
        popup.geometry(f"+{x}+{y}")
        popup.deiconify()
        popup.minsize(400, 175)

    def open_manual(self):
        manual_path = os.path.join(self.script_dir, "HyProC_Manual.pdf")
        if sys.platform == "win32":
            os.startfile(manual_path)
        elif sys.platform == "darwin":
            subprocess.run(["open", manual_path])
        else:
            subprocess.run(["xdg-open", manual_path])

    def ask_energy_range(self) -> tuple[float, float] | None:
        popup = tk.Toplevel()
        popup.withdraw()  # Hide the window until it's properly sized and positioned
        popup.transient(self)
        popup.grab_set()
        popup.title("No Excitation Curve Loaded")

        ttk.Label(popup, text=f"No experimental excitation curve loaded.\nDefine an energy range to generate a simulated curve.",
                  wraplength=350, justify="center").grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        ttk.Label(popup, text="Minimum energy (keV):").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        min_entry = ttk.Entry(popup, width=10)
        min_entry.insert(0, str(getattr(self, "e_min", "")))
        min_entry.grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(popup, text="Maximum energy (keV):").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        max_entry = ttk.Entry(popup, width=10)
        max_entry.insert(0, str(getattr(self, "e_max", "")))
        max_entry.grid(row=2, column=1, padx=10, pady=5)

        ttk.Label(popup, text="Number of points:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        nbr_entry = ttk.Entry(popup, width=10)
        nbr_entry.insert(0, str(getattr(self, "nbr_points", 150)))
        nbr_entry.grid(row=3, column=1, padx=10, pady=5)

        result = [None]

        def generate():
            try:
                e_min = float(min_entry.get())
                e_max = float(max_entry.get())
                if e_min >= e_max:
                    messagebox.showerror("Invalid Range", "Minimum energy must be less than maximum energy.")
                    return
                nbr = int(nbr_entry.get())
                result[0] = (e_min, e_max, nbr)
                popup.destroy()
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter valid numeric values for both energies.")
                return 

        def cancel():
            popup.destroy()

        btn_frame = ttk.Frame(popup)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Cancel", command=cancel).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Generate", command=generate).pack(side="left", padx=5)

        #popup.withdraw()
        popup.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - (popup.winfo_width() // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (popup.winfo_height() // 2)
        popup.geometry(f"+{x}+{y}")
        popup.deiconify()
        popup.minsize(300, 150)

        popup.wait_window()
        return result[0]

    # -------------------------------------------
    def start_calc(self)->None:
        """
        Prevents the GUI from freezing under load.
        """
        threading.Thread(target=self.Calculation).start() 

    def std_calc(self, yield_value:float, beamWidth:float, DopplerYesNo:bool, straggling_model:str)->float:
        """
        Calculates the K factor (experimental set-up detection efficiency) based on the standard description.
        """      
        energy = 6525 
        self.std_target["layers"][0]["stopping"] = mod2.calc_stopping_power(self.std_target["layers"][0], energy)
        xc,x,y, layers_contribution, outOfTarget = mod3.broadening(energy, self.std_target, beamWidth, DopplerYesNo, straggling_model, False, None)

        #print(f"DEBUG: Broadening output shapes: x={np.array(x).shape}, y={np.array(y).shape}")
        #print(f"DEBUG: x range: [{np.min(x):.3f}, {np.max(x):.3f}], y range: [{np.min(y):.6f}, {np.max(y):.6f}]")
        #print(f"DEBUG: x finite: {np.all(np.isfinite(x))}, y finite: {np.all(np.isfinite(y))}")
        
        try:
            value = mod4.compute_yield(self.std_target, x, y)
        except ValueError as e:
            print(f"DEBUG: compute_yield raised ValueError: {e}")
            raise
        
        #print(f"DEBUG: Computed yield value: {value}, finite: {np.isfinite(value)}")
        if not np.isfinite(value) or value == 0.0:
            raise ValueError(f"Standard yield integral is invalid (value={value}). Check target and broadening data.")
        K = yield_value / value
        #print(self.std_target)
        print("K calculated: ", K)
        return K        

    def Calculation(self)->None:
        """
        Generates a simulated excitation curve.
        """
        # Checking settings: Can SRIM & save paths can be accessed?
        if not mod2.check_srim_path(self.settings_path):
            messagebox.showerror("Calculation failed", "SRIM path not found.\n\nPlease check your settings.")
            return
        with open(self.settings_path, 'r', encoding="utf-8") as f:
            path = json.load(f)["save_path"]
            found = os.path.exists(path)
        if not found:
            messagebox.showerror("Calculation failed", "Save path not found.\n\nPlease check your settings.")
            return
        
        # Retrieving info from GUI
        try:
            beamWidth = float(self.beamSD_entry.get())
        except:
            messagebox.showerror("Calculation failed", "No beam width value was entered.")
            return 
        try:
            std_yield = float(self.std_Yield_entry.get())
        except:
            messagebox.showerror("Calculation failed", "No standard yield value was entered.")
            return
        DopplerYesNo = self.Doppler_bool.get()
        SaveBroadData = self.broadSave_bool.get()
        trackTargetChange = self.TrackTargetChange_bool.get()
        straggling_model = self.straggling_model_combobox.get()
        try:
            offset = float(self.offset_entry.get())
        except:
            offset = 0.0

        # Check for the element of interest in the standard
        percent_at = self.std_target["layers"][0].find_element(Z=self.Z2)
        if percent_at is None or percent_at == 0:
            messagebox.showerror("Calculation failed", f"Standard calculation error.\n\nNo {periodictable.elements[self.Z2].name.capitalize()} in the standard.")
            return

        # If no experimental curve loaded, ask for energy range to generate a simulated curve
        if not hasattr(self, "ec_yield") or not self.ec_yield:
            result = self.ask_energy_range()
            if result is None:
                return
            self.e_min, self.e_max, self.nbr_points = result
            self.exp_energy = list(np.linspace(self.e_min, self.e_max, self.nbr_points))
            self.ec_yield = None  # No experimental yield

        # Calculating K factor
        try:
            print("*-*-*-*-*-*-* Starting Calculation *-*-*-*-*-*-*")  
            if self.std_target["layers"][0].normalize():
                self.refresh_Std_list()
                print("Standard layer normalised.")
            K = self.std_calc(std_yield, beamWidth, DopplerYesNo, straggling_model)
        except:
            messagebox.showerror("Calculation failed", "Standard calculation error.\n\nMake sure all the standards information were correctly entered.")
            raise Exception("Standard calculation failed.")
        
        try:
            self.run_button.config(text="Working...", style="Working.TButton", state="disabled")

            # Normalising target
            self.target.normalize_all_layers()
            size_before = len(self.target["layers"])
            self.target = mod2.assign_stopping(self.target, max(self.exp_energy))
            self.refresh_layer_list()
            self.refresh_element_list()            

            # Generating paths for saving data
            with open(self.settings_path, 'r', encoding="utf-8") as f:
                path = os.path.join(json.load(f)["save_path"], "HyProC")
            if self.runNbr == 0:
                self.session_dir = os.path.join(path, "Session "+ self.timestamp)
            if SaveBroadData or trackTargetChange:
                os.makedirs(self.session_dir, exist_ok=True)
                target_dir = os.path.join(self.session_dir, f"Run {self.runNbr}")
                os.mkdir(target_dir)
                if trackTargetChange:
                    self.save_json(savepath=target_dir+'/_target.json')

            self.sim_energy = []
            self.sim_curve = []
            countE = 0

            # Actual calculation loop
            for energy in self.exp_energy:
                if SaveBroadData:
                    sub_dir = f'datapoint{countE}'
                    savepath = os.path.join(target_dir, sub_dir)
                    os.mkdir(savepath)
                    with open(os.path.join(savepath,f'_E={energy:.1f}kev.dat'),'w') as f:
                        pass
                else:
                    savepath = None

                xc, x, y, layers_contribution, outOfTarget = mod3.broadening(energy, self.target, beamWidth, DopplerYesNo, straggling_model, SaveBroadData, savepath)
                #print(f"DEBUG: Broadening output shapes: x={np.array(x).shape}, y={np.array(y).shape}")
                #print(f"DEBUG: x range: [{np.min(x):.3f}, {np.max(x):.3f}], y range: [{np.min(y):.6f}, {np.max(y):.6f}]")

                integral_yield = mod4.compute_yield(self.target, x, y)
                #print('K*integral_yield: ', K, '*', integral_yield, '=', K * integral_yield)
                value = K*integral_yield
                self.sim_energy.append(energy+offset)
                self.sim_curve.append(value)
                
                countE+=1 # Datapoint number

            self.update_exc_plot()
            if hasattr(self, 'exp_energy') and self.exp_energy is not None and hasattr(self, 'ec_yield') and self.ec_yield is not None:
                self.chi_val.append(round(mod4.chi_squared_test(self.exp_energy, self.ec_yield, self.sim_energy, self.sim_curve), 2))
            else:
                self.chi_val.append(-1.0)
            if len(self.chi_val) > self.visible_count:
                self.scroll_down()
            self.update_chi_plot()

            if trackTargetChange or SaveBroadData:
                print(f"Run data saved in: {target_dir}")

            self.runNbr+=1 # Run number

            if len(self.target["layers"]) != size_before:
                messagebox.showinfo("Calculations","At least one layer has been segmented to more accurately describe stopping powers.")

            print("*-*-*-*-*-*-* Calculation completed *-*-*-*-*-*-*") 
        except Exception as e:
            print(f"An error occurred: {type(e).__name__}: {e}")
            traceback.print_exc()
            tb = traceback.extract_tb(e.__traceback__)
            for frame in tb:
                print(f"File : {frame.filename}, line : {frame.lineno}, code : {frame.line}")
        
        # Unlocking the "Run Calculation" button
        self.run_button.config(text="Run calculation",style="Default.TButton", state="normal")

    def _close_Z2_profile(self)->None:
        self.Z2_profile.destroy()
        self.Z2_profile = None
    
    def plot_Z2_profile(self)->None:
        x,y = mod4.cH_make(self.target)

        # --- If the window already exists, bring it to the front ---
        if self.Z2_profile is not None and self.Z2_profile.winfo_exists():
            self.Z2_profile.lift()

        # --- Creating new window if it doesn't exist or was closed ---
        else:
            self.Z2_profile = tk.Toplevel(self)
            self.Z2_profile.title("Hydrogen Profile")
            fig = Figure(figsize=(8, 5))
            ax = fig.add_subplot()
            canvas_H = FigureCanvasTkAgg(fig, master=self.Z2_profile)
            canvas_H.draw()
            canvas_H.get_tk_widget().pack(fill="both", expand=True)

            toolbar = NavigationToolbar2Tk(canvas_H, self.Z2_profile)
            toolbar.update()
            toolbar.pack(fill='x')

            self.Z2_profile.fig = fig
            self.Z2_profile.ax = ax
            self.Z2_profile.canvas = canvas_H

            self.Z2_profile.update_idletasks()
            x_win = self.winfo_x() + (self.winfo_width() // 2) - (self.Z2_profile.winfo_width() // 2)
            y_win = self.winfo_y() + (self.winfo_height() // 2) - (self.Z2_profile.winfo_height() // 2)
            self.Z2_profile.geometry(f"800x600+{x_win}+{y_win}")

            self.Z2_profile.protocol("WM_DELETE_WINDOW",self._close_Z2_profile)

        # --- Updating the plot itself ---
        ax = self.Z2_profile.ax
        ax.clear()
        ax.step(x,y,where='pre',linewidth=2,color='tab:red')
        # plt.semilogy()
        ax.set_xlabel("x (TFU)", fontsize=16)
        ax.set_ylabel("H content (at. %)", fontsize=16)
        ax.set_xlim(left=0)
        ax.set_ylim(bottom=0.01)
        ax.set_ylim(top=max(y)+9)
        ax.grid()
        ax.grid(which='minor')
        highlight_ranges = list(zip(x[:-1], x[1:]))

        #labels = ['Matrice C', 'Matrice Ti','','','']
        #legend_patches = [Patch(facecolor=colors[i], alpha=0.999, label=labels[i]) 
        #    for i in range(len(highlight_ranges))]

        #ax = plt.gca()
        colors = ["#cfcfcf" if i % 2 == 0 else "#f0f0f0" for i, _ in enumerate(highlight_ranges)]

        # Changing the background of the graph
        for i, (start, end) in enumerate(highlight_ranges):
            ax.axvspan(start, end, color=colors[i % len(colors)], alpha=0.85)
            pass
        
        # Add text labels above each step
        disp_y_shift = 1*max(y)/100 if not max(y) == 0 else 0.05
        for i in range(1,len(x)-1):
            x_mid = (x[i-1] + x[i]) / 2       # midpoint of the horizontal segment
            y_pos = y[i]                
            ax.text(x_mid, y_pos+disp_y_shift, str(x[i]-x[max(i-1,0)])+" TFU", ha='center', va='bottom', fontsize=9)
            ax.text(x_mid, y_pos+5*disp_y_shift, f"{y[i]:.2f} %", ha='center', va='bottom', fontsize=12)

        # Adjust the last point: center relative to previous x
        x_last = (x[-2] + x[-1]) / 2  # midpoint between last two x
        y_last = y[-1]
        ax.text(x_last, y_last+disp_y_shift, str(x[-1]-x[-2])+" TFU", ha='center', va='bottom', fontsize=9)
        ax.text(x_last, y_last+5*disp_y_shift, f"{y_last:.2f} %", ha='center', va='bottom', fontsize=12)

        self.Z2_profile.canvas.draw_idle()

    def Autofit(self)->None:
        print("Not implemented yet")  

    def save_json(self, target_type: Literal['target', 'std'] = 'target', savepath: str | None = None) -> None:
        """
        Saves the current target or standard configuration as a JSON file.
        """
        file_path = savepath or filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            title="Save JSON File"
        )
        if file_path:
            with open(file_path, 'w') as file:
                json.dump(self.std_target if target_type == "std" else self.target, file, indent=4)
            print(f"File saved to: {file_path}")

    def save_sim_curve_txt(self)->None:
        """
        Saves the simulated excitation curve as a TXT file.
        """
        if not hasattr(self, "sim_curve"):
            messagebox.showwarning("Save simulated curve", "No simulated excitation curve to save")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("TXT file", "*.txt")],
            title="Save Simulated curve"
        )
        if not file_path:
            return
        try:
            with open(file_path, 'w') as file:
                for v1, v2 in zip(self.exp_energy, self.sim_curve):
                    file.write(f"{v1:.3f}\t{v2:.1f}\n")
            print(f"File saved to: {file_path}")
        except Exception as e:
            print(f"An error occurred: {type(e).__name__}: {e}")

    def on_close(self)->None:
        exitDialogResult = messagebox.askyesnocancel("Quit", "Save the target before closing?")
        if exitDialogResult is None:
            return
        if exitDialogResult:
            self.save_json()
        self.quit()

# Run app
if __name__ == "__main__":
    app = GUI_App()
    app.mainloop()
