import tkinter as tk
from tkinter import filedialog,messagebox
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,NavigationToolbar2Tk
import matplotlib.pyplot as plt
import os
import re
import glob

class GUI_app:
    def __init__(self, root):
        self.root = root
        self.root.title("Broadplotter")

        self.filename = None

        # Style
        #self.style = ttk.Style()
        #self.style.theme_use('clam')  # 'clam', 'alt', 'default', 'classic' available

        # --- Folder Selection Button ---
        self.folder_button = ttk.Button(root, text="Select Run folder", command=self.choose_folder)
        self.folder_button.pack(pady=10)

        # --- Label for datapoints ---
        self.data_label = ttk.Label(root, text="Datapoints", font=("Arial", 10, "bold"))
        self.data_label.pack()

        # --- Previous / Next buttons in one row ---
        self.button_frame = ttk.Frame(root)
        self.button_frame.pack(pady=5)

        self.prev_button = ttk.Button(self.button_frame, text="Previous", command=self.previous)
        self.prev_button.pack(side=tk.LEFT, padx=5)

        self.next_button = ttk.Button(self.button_frame, text="Next", command=self.next)
        self.next_button.pack(side=tk.LEFT, padx=5)

        # --- Combobox under buttons ---
        self.combo_label = ttk.Label(root, text="Select Data Type:")
        self.combo_label.pack(pady=(10, 0))

        # Mapping: display_name -> actual filename or variable
        self.data_mapping = {
            "Beam": "Beam.txt",
            "Straggling": "Stragg.txt",
            "Doppler": "Doppler.txt",
            "Total Gauss": "Total_Gauss.txt",
            "Cross section": "xsec.txt",
            "Total Broadening": "Total_Broadening.txt",
            "Total Broadening (TFU)": "Total_Broadening_TFU.txt"
        }

        # Display names for the combobox
        self.data_options = list(self.data_mapping.keys())

        self.combo_var = tk.StringVar()
        self.combobox = ttk.Combobox(root, textvariable=self.combo_var, values=self.data_options, state="readonly")
        self.combobox.set("Choose file")  # default value
        self.combobox.pack(pady=5)
        self.combobox.bind("<<ComboboxSelected>>", self.combobox_changed)        

        # --- Matplotlib Figure ---
        self.fig, self.ax = plt.subplots(figsize=(5,4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.root)
        self.toolbar.update()
        self.toolbar.pack(side='bottom', fill='x')

        # Placeholder for current folder and index
        self.folder_path = ""
        self.current_index = 0
        self.max_index = 0

    # --- Button callbacks ---
    def choose_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            # Look for subfolders starting with "datapoint"
            subfolders = [
                name for name in os.listdir(folder)
                if os.path.isdir(os.path.join(folder, name)) and name.lower().startswith("datapoint")
            ]

            if not subfolders:
                messagebox.showerror(
                    "Invalid Folder",
                    "The selected folder does not contain any subfolder starting with 'datapoint'."
                )
                return  # stop here if invalid

            self.folder_path = folder
            with os.scandir(self.folder_path) as entries:
                self.max_index = sum(1 for entry in entries if entry.is_dir())

            print(f"Selected folder: {self.folder_path}")
            ## Check all expected files
            #missing_files = []
            #for display_name, filename in self.data_mapping.items():
            #    file_path = os.path.join(self.folder_path, filename)
            #    if not os.path.isfile(file_path):
            #        missing_files.append(filename)
            #
            #if missing_files:
            #    missing_list = "\n".join(missing_files)
            #    messagebox.showerror(
            #        "Missing Files",
            #        f"The following files could not be found in the selected folder:\n{missing_list}"
            #    ) 
        
        selected_display = self.combo_var.get()
        if not selected_display == "Choose file":
            self.load_and_plot(os.path.join(self.folder_path,f"datapoint{self.current_index}",self.filename) )

    def previous(self):
        self.current_index = max(0, self.current_index - 1)
        self.load_and_plot(os.path.join(self.folder_path,f"datapoint{self.current_index}",self.filename) )

    def next(self):
        if not self.current_index == self.max_index-1:
            self.current_index += 1
            self.load_and_plot(os.path.join(self.folder_path,f"datapoint{self.current_index}",self.filename) )

    def combobox_changed(self, event):
        display_name = self.combo_var.get()
        self.filename = self.data_mapping.get(display_name)
        
        # You can update your plot or logic here based on selection
        if not self.folder_path == "":
            self.load_and_plot(os.path.join(self.folder_path,f"datapoint{self.current_index}",self.filename) )        

    def load_and_plot(self, filename, delimiter='\t'):
        """
        Load two-column data from a .txt file and plot it.

        Parameters:
            filename (str): Path to the text file.
            delimiter (str): Column separator (default is tab).
        """

        x_vals = []
        y_vals = []

        with open(filename, 'r') as f:
            for line in f:
                if line.strip():  # skip empty lines
                    parts = line.strip().split(delimiter)
                    if len(parts) == 2:
                        try:
                            x = float(parts[0])
                            y = float(parts[1])
                            x_vals.append(x)
                            y_vals.append(y)
                        except ValueError:
                            print(f"Skipping invalid line: {line.strip()}")

        for i,x in enumerate(x_vals):
            if None or x < 0:
                y_vals[i]=0

        # nrg_loc = os.path.join(self.folder_path,f"datapoint{self.current_index}")

        # Plotting
        self.ax.clear()
        self.ax.set_title(f"Datapoint {self.current_index} (E = {self.get_energy_from_dat()} keV)")
        self.ax.plot(x_vals, y_vals, marker='.', linestyle='-')
        if filename.endswith("TFU.txt"):
            self.ax.set_xlabel("x (TFU)")
            self.ax.set_xlim(left=0.0, right=max(1,max(x_vals)+0.05*max(x_vals)))
        else:
            self.ax.set_xlabel("E (keV)")
        if filename.endswith("xsec.txt"):
            self.ax.set_ylabel("Cross section (mb)")
        else:
            self.ax.set_ylabel("Probability")

        self.ax.grid(True)
        self.fig.tight_layout()
        self.canvas.draw()

    def get_dat_filename(self):
        dat_files = glob.glob(os.path.join(self.folder_path,f"datapoint{self.current_index}", "*.dat"))
        if len(dat_files) != 1:
            raise FileNotFoundError("Expected exactly one .dat file in the folder.")
        return os.path.basename(dat_files[0])
    
    def get_energy_from_dat(self):
        filename = self.get_dat_filename()
        match = re.search(r"_E=([\d.]+)kev", filename)
        if not match:
            raise ValueError(f"Could not find energy pattern in {filename}")
        return float(match.group(1))

# --- Run the GUI ---
if __name__ == "__main__":
    root = tk.Tk()
    app = GUI_app(root)
    root.mainloop()
