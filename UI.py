import tkinter as tk
from tkinter import filedialog, messagebox,ttk
import periodictable
import json
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,NavigationToolbar2Tk)
import os
from datetime import datetime
import copy
import threading
from UI_geometry import create_widgets
import traceback
import numpy as np
from scipy.interpolate import make_smoothing_spline
from scipy.interpolate import UnivariateSpline

import mod2
import mod3 
import mod4

class Element(dict):
    def __init__(self, Z: int = 14, percent_at: float = 100.0): # Default: Si, 100% at.
        super().__init__()
        self["Z"] = Z
        self["percent_at"] = percent_at

class Layer(dict):
    def __init__(self, AD: float = 1000.0):
        super().__init__()
        self["areal_density"] = AD
        self["stopping"] = 0.01 # Dummy value
        self["elements"] = [Element()]  

class Target(dict):
    def __init__(self):
        self["layers"] = [Layer()]  # Start with one default layer

# Main GUI application
class GUI_App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.base = r'C:\HyProC'
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        
        self.runNbr = 0

        self.title("HyProC")
        self.geometry("850x900")

        self.style = ttk.Style(self)
        #self.style.theme_use("default")  # Required for color customization
        # Define your custom styles
        self.style.configure("Default.TButton", background="snow", foreground="black")
        self.style.configure("Working.TButton", background="orange", foreground="black")

        self.target = Target()
        self.selected_layer_index = 0
        self.selected_el_index = 0

        self.start_ctr = 0
        self.visible_count = 9
        self.chi_val=[]

        create_widgets(self)
        self.refresh_layer_list()
        self.refresh_element_list() 
        self.update_chi_plot()
        self.protocol("WM_DELETE_WINDOW", self.on_close)


    def update_chi_plot(self):
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

    def scroll_up(self):
        if self.start_ctr > 0:
            self.start_ctr -= 1
            self.update_chi_plot()

    def scroll_down(self):
        if self.start_ctr + self.visible_count < len(self.chi_val):
            self.start_ctr += 1
            self.update_chi_plot()

    def update_exc_plot(self, event=None):
        self.ax0.clear()
        # Experimental datapoints
        try:
            self.ax0.scatter(self.ec_energy, self.ec_yield, label='Exp',marker='.',color='tab:blue')   # HERE
            self.ax0.errorbar(self.ec_energy, self.ec_yield, self.ec_yErr, fmt='none', color='tab:blue' )
        except:
            print("No experimental excitation curve.")
        # Simulation curve 
        try:
            self.ax0.plot(self.ec_energy,self.sim_curve,label='Sim',linestyle='--',marker='.',color='tab:orange')  # HERE

            #self.y_spl = make_smoothing_spline(self.ec_energy, self.sim_curve, lam=None)
            #self.y_spl = UnivariateSpline(self.ec_energy, self.sim_curve, s=1)
            #self.sim_smooth_x = np.linspace(min(self.ec_energy),max(self.ec_energy),301)
            #self.sim_smooth_y = self.y_spl(self.sim_smooth_x)
            #self.ax0.plot(self.sim_smooth_x,self.sim_smooth_y,label='Sim',linestyle='--',color='tab:orange')
        except :
            pass
        #ax = self.ax0.gca()
        self.ax0.legend(loc='best')
        self.ax0.set_xlabel("Energy (keV)")
        self.ax0.set_ylabel("Yield (Count/µC)")
        self.ax0.set_ylim(bottom=0)
        self.ax0.grid(alpha=0.4)
        self.canvas.draw()       

    # GUI updates in top frames
    def refresh_layer_list(self):
        self.layer_listbox.delete(0, tk.END)
        for i, layer in enumerate(self.target["layers"]):
            # Retrieve symbols for all elements in this layer
            data = layer["elements"]
            element_symbols = [periodictable.elements[el["Z"]].symbol for el in data]
            element_percent = [el["percent_at"] for el in data]
            elements_str = ', '.join(f"{sym}{int(percent)}" for sym, percent in zip(element_symbols, element_percent))
            self.layer_listbox.insert(
                tk.END,
                f"Layer {i + 1}: {layer['areal_density']} TFU ({elements_str})"
            )
        self.layer_listbox.select_set(self.selected_layer_index)
        # When starting the interface, filling in the textboxs:
        current_layer = self.target["layers"][self.selected_layer_index]
        self.AD_entry.delete(0, tk.END)
        self.AD_entry.insert(0,str(current_layer["areal_density"])) 


    def refresh_element_list(self):
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


    # Target Config Commands
    def add_layer(self):
        self.target["layers"].append(Layer())
        self.selected_layer_index = len(self.target["layers"]) - 1
        self.selected_el_index = 0
        self.refresh_layer_list()
        self.refresh_element_list()

    def remove_layer(self):
        if len(self.target["layers"]) > 1:
            del self.target["layers"][self.selected_layer_index]
            self.selected_layer_index = max(0, self.selected_layer_index - 1)
            self.selected_el_index = 0
            self.refresh_layer_list()
            self.refresh_element_list()

    def duplicate_layer(self):
        original_layer = self.target["layers"][self.selected_layer_index]
        duplicated_layer = copy.deepcopy(original_layer)
        self.target["layers"].append(duplicated_layer)
        self.selected_layer_index = len(self.target["layers"]) - 1
        self.refresh_layer_list()
        self.refresh_element_list()

    def move_layer_up(self):
        if self.selected_layer_index > 0:
            i = self.selected_layer_index
            self.target["layers"][i - 1], self.target["layers"][i] = self.target["layers"][i], self.target["layers"][i - 1]
            self.selected_layer_index -= 1
            self.refresh_layer_list()
            self.refresh_element_list()

    def move_layer_down(self):
        if self.selected_layer_index < len(self.target["layers"]) - 1:
            i = self.selected_layer_index
            self.target["layers"][i + 1], self.target["layers"][i] = self.target["layers"][i], self.target["layers"][i + 1]
            self.selected_layer_index += 1
            self.refresh_layer_list()
            self.refresh_element_list()


    def add_element(self):
        try:
            #Z = int(self.element_Z_entry.get())
            #percent = float(self.composition_percent_entry.get())
            current_layer = self.target["layers"][self.selected_layer_index]
            current_layer["elements"].append(Element())
            self.selected_el_index = len(current_layer["elements"]) - 1
            self.refresh_element_list()
            self.refresh_layer_list()
        except ValueError:
            pass  # You might want to show an error dialog

    def remove_element(self):
       selected = self.elem_listbox.curselection()
       if selected:
           current_layer = self.target["layers"][self.selected_layer_index]
           if len(current_layer["elements"]) > 1:
               del current_layer["elements"][selected[0]]
               self.selected_el_index = max(0, self.selected_el_index - 1)
               self.refresh_element_list()
               self.refresh_layer_list()

    def normalize_percentages(self):
        """
        Adjusts the percent_at values so they sum to 100.0,
        while keeping the selected element's value unchanged.
        """

        current_layer = self.target["layers"][self.selected_layer_index]
        elements = current_layer["elements"]

        # Extract current percentages
        percentages = [el["percent_at"] for el in elements]
        total = sum(percentages)

        if abs(total - 100.0) < 1e-9:
            return   # Already sums to 100

        # Value to keep fixed
        fixed_value = percentages[self.selected_el_index]

        # Remaining sum that other elements should share
        remaining = 100.0 - fixed_value

        # Current sum of the other elements
        current_other_sum = total - fixed_value

        if current_other_sum == 0:
            # If all others are zero, just set them proportionally equal
            elements[self.selected_el_index]["percent_at"] = 100.0
        else:
            # Scale other elements proportionally
            for i, el in enumerate(elements):
                if i != self.selected_el_index:
                    el["percent_at"] = el["percent_at"] / current_other_sum * remaining

        self.refresh_element_list()
        self.refresh_layer_list()


    ## Selection handlers

    # Updating the layer text entries when selecting a layer in the listbox
    def on_layer_select(self, event=None):
        selected_layer_index = self.layer_listbox.curselection()
        self.selected_el_index = 0
        if selected_layer_index:
            selected_layer_index = selected_layer_index[0]
            self.selected_layer_index = selected_layer_index
            current_layer = self.target["layers"][selected_layer_index]

            # Display the selected layer's thickness in the entry
            self.AD_entry.delete(0, tk.END)
            self.AD_entry.insert(0, str(current_layer["areal_density"]))

            self.refresh_layer_list()
            self.refresh_element_list()

    # Updating the layer listbox when values in the text entries are modified
    def on_layer_entry_update(self, event=None):
        selected = self.layer_listbox.curselection()
        if selected: # making sure something is selected
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

    # Updating the element text entries when selecting an element in the listbox
    def on_element_select(self, event):
        selected_el_index = self.elem_listbox.curselection()
        if selected_el_index:
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

    # Updating the element listbox when values in the text entries are modified
    def element_on_entry_update(self, event=None, entry_type=None):
        selected = self.elem_listbox.curselection()  # Get selected element in the list
        if selected:  # Ensure something is selected

            current_layer = self.target["layers"][self.selected_layer_index]
            element = current_layer["elements"][self.selected_el_index]  # Get the selected element

            try:
                if entry_type == 'Z':
                    new_value = int(self.element_Z_entry.get())  # Get the Z value as an integer
                    if 0 < new_value < 119:  # Make sure the element exist
                        element["Z"] = new_value  # Update the Z value
                elif entry_type == 'percent_at':
                    new_value = float(self.composition_percent_entry.get())  # Get the percent_at value
                    if 0 <= new_value <= 100:  # Ensure % is within valid range (0 to 100)
                        element["percent_at"] = new_value  # Update the percent_at value
                else:
                    print("Unknown entry type")
                # After updating, refresh the element list and layer list to reflect changes

                self.refresh_element_list()
                self.refresh_layer_list()

            except ValueError:
                print("Invalid input. Please enter a valid number.")


    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx *.xls *.csv"),
        ("All Files", "*.*")])
        if file_path:
            try:
                # Important raw data
                self.script_dir = os.path.dirname(os.path.abspath(__file__))
                settings_path = os.path.join(self.script_dir, 'import_file_settings.json')

                with open(settings_path,'r', encoding="utf-8") as f:
                    filedata = json.load(f)
                    tab_nbr = filedata["sheet_number"]
                    header_pos = filedata["header_pos"]
                    header0 = filedata["energy_header_name"]
                    header1 = filedata["yield_header_name"]
                    header2 = filedata["yErr_header_name"]
                df = pd.read_excel(file_path,sheet_name=tab_nbr, header=header_pos,engine='openpyxl')
                self.ec_energy = df[header0].tolist()
                self.ec_yield = df[header1].tolist()
                self.ec_yErr = df[header2].tolist()
                # Sorting data (by energy, ascending)
                sorted_indices = sorted(range(len(self.ec_energy)), key=lambda i: self.ec_energy[i]) 
                self.ec_energy = [self.ec_energy[i] for i in sorted_indices]
                self.ec_yield = [self.ec_yield[i] for i in sorted_indices]
                self.ec_yErr = [self.ec_yErr[i] for i in sorted_indices]
            except PermissionError:
                messagebox.showerror("Permission Denied", 
                f"Cannot open the file:\n{file_path}\n\n"
                "Please close it in Excel or any other program and try again.")
                print("PermissionError: File is likely opened in another application.")
            except ValueError:
                print("Couldn't load the data.")
            self.update_exc_plot()

            return self.ec_energy, self.ec_yield
        else:
            print("No file selected")
    
    def load_target(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            try:
                with open(file_path,'r') as f:
                    self.target = json.load(f)
                print('Target loaded')
            except ValueError:
                print("Couldn't load the data.")
        self.refresh_layer_list()
        self.refresh_element_list()

    def get_std_info(self):
        try:
            H = float(self.std_H_entry.get())
            notH = 100.0 - H
            std = {
                "elements": [
                    {
                        "Z": 1,
                        "percent_at": float(H)
                    },
                    {
                        "Z": int(self.std_Z_entry.get()),
                        "percent_at": notH
                    }
                ]
            }
            std_Yield = float(self.std_Yield_entry.get())
            std_S = mod2.calc_stopping_power(std, 6385)
        except ValueError:
            print("Invalid standard inputs.")
        return H, std_S, std_Yield, std
    
    def std_calc(self):
        stdH, stdS, stdY, std = self.get_std_info()
        beamWidth = float(self.beamSD_entry.get())
        DopplerYesNo = self.Doppler_bool.get()

        self.std_target = Target()
        self.std_target["layers"][0]["stopping"] = stdS
        del self.std_target["layers"][0]["elements"]
        self.std_target["layers"][0].update(std)
        self.std_target["layers"][0]["areal_density"] = 1500.0

        xc,x,y, layers_contribution, outOfTarget = mod3.broadening(6500, self.std_target, beamWidth, DopplerYesNo, False, None)

        value = mod4.compute_yield(self.std_target, x, y)
        K = stdY/value
        print("K calculated: ", K)
        return K
        

    def start_calc(self):
        threading.Thread(target=self.Calculation).start() # Prevents the GUI from freezing under load

    def Calculation(self):
        if not hasattr(self, "ec_energy"):
            messagebox.showerror("Run Calculation","No simulated excitation curve loaded.")
            return None
        
        # Retrieving info from GUI first 
        try:
            beamWidth = float(self.beamSD_entry.get())
        except:
            messagebox.showerror("Run Calculation","No beam width value was entered.")
            return None
        DopplerYesNo = self.Doppler_bool.get()
        SaveBroadData = self.broadSave_bool.get()

        print("*-*-*-*-*-*-* Starting Calculation *-*-*-*-*-*-*")

        if self.runNbr == 0:
            self.session_dir = os.path.join(self.base, "Session "+ self.timestamp)
        
        if SaveBroadData:
            if not os.path.isdir(self.session_dir):
                os.mkdir(self.session_dir)
            target_dir = os.path.join(self.session_dir, f"Run {self.runNbr}")
            os.mkdir(target_dir)
        self.runNbr+=1

        try:
            try:
                K = self.std_calc()
            except:
                messagebox.showerror("Run Calculation","Standard calculation error.\n\nMake sure all the standards fields were correctly filled.")
                return None

            self.run_button.config(text="Working...", style="Working.TButton", state="disabled")

            # Normalising target
            for i, layer_i in enumerate(self.target["layers"]):
                elements = layer_i["elements"]

                # Extract current percentages
                percentages = [el["percent_at"] for el in elements]
                total = sum(percentages)
                
                if not total == 100.0:
                # Scale everything proportionally
                    for el in elements:
                        el["percent_at"] = el["percent_at"] / total * 100.0
                    self.refresh_layer_list()
                    self.refresh_element_list()
                    print(f"Normalised target layer {i}")

        
            self.sim_curve = []

            size_before = len(self.target["layers"])
            self.target = mod2.assign_stopping(self.target,max(self.ec_energy))
            #os.chdir(path)

            countE = 0
            #sub_dir = f'datapoint{countE}'
            #os.mkdir(sub_dir)
            #os.chdir(sub_dir)

            for energy in self.ec_energy:
                if SaveBroadData:
                    sub_dir = f'datapoint{countE}'
                    savepath = os.path.join(target_dir, sub_dir)
                    os.mkdir(savepath)
                    with open(os.path.join(savepath,f'_E={energy:.1f}kev.dat'),'w') as f:
                        pass
                    
                else:
                    savepath = None

                xc,x,y, layers_contribution, outOfTarget = mod3.broadening(energy, self.target, beamWidth, DopplerYesNo, SaveBroadData, savepath)

                # value = stdH/stdY/stdS*sim_exc_curve.compute_yield(self.target, x, y)
                integral_yield = mod4.compute_yield(self.target, x, y)

                value = K*integral_yield

                self.sim_curve.append(value)
                
                # Keeping track of the run number
                countE+=1

            self.update_exc_plot()
            self.chi_val.append(round(mod4.chi_squared_test(self.ec_yield,self.sim_curve),2))
            if len(self.chi_val) > self.visible_count:
                self.scroll_down()

            self.update_chi_plot()

            self.refresh_element_list()
            self.refresh_layer_list()

            if not len(self.target["layers"]) == size_before:
                messagebox.showinfo("Calculations","A layer has been segmented to more accurately describe stopping powers.")

            print("*-*-*-*-*-*-* Calculation completed *-*-*-*-*-*-*") 
        except Exception as e:
            print(f"An error occurred: {type(e).__name__}: {e}")
            traceback.print_exc()
            tb = traceback.extract_tb(e.__traceback__)
            for frame in tb:
                print(f"File : {frame.filename}, line : {frame.lineno}, code : {frame.line}")
        
        # Unlocking the "Run Calculation" button
        self.run_button.config(text="Run calculation",style="Default.TButton", state="normal")


    def Autofit():
        print("Not implemented yet")  

    def save_target_json(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json",filetypes=[("JSON files", "*.json")],title="Save JSON File")
        # Save the dictionary to the selected file
        if file_path:
            with open(file_path, 'w') as file:
                json.dump(self.target, file, indent=4)
            print(f"File saved to: {file_path}")
        else:
            print("Save canceled.")

    def save_sim_curve_txt(self):

        if not hasattr(self, "sim_curve"):
            #print("No simulated excitation curve to save.")
            messagebox.showwarning("Save simulated curve","No simulated excitation curve to save")
            return None
        try:
            file_path = filedialog.asksaveasfilename(defaultextension=".txt",filetypes=[("TXT file", "*.txt")],title="Save Simulated curve")
            # Save the dictionary to the selected file
            if file_path:
                with open(file_path, 'w') as file:
                    for v1, v2 in zip(self.ec_energy, self.sim_curve):
                        file.write(f"{v1:.3f}\t{v2:.1f}\n")
                    print(f"File saved to: {file_path}")
            else:
                print("Save canceled.")
        except Exception as e:
            print(f"An error occurred: {type(e).__name__}: {e}")
    
    # Closing
    def on_close(self):
        exitDialogResult = messagebox.askyesnocancel("Quit", "Save the target before closing?")
        if exitDialogResult is True:
            self.save_target_json()
            self.quit()
        elif exitDialogResult is False:
            self.quit()
        else:
            return


# Run app
if __name__ == "__main__":
    app = GUI_App()
    app.mainloop()
