import tkinter as tk
from tkinter import filedialog, messagebox,ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,NavigationToolbar2Tk)
from datetime import datetime

def create_widgets(self):
        # Main Frame
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill='both', expand=True)

        ################################################################
        # Left Frame
        self.left_frame = ttk.Frame(self.main_frame,width=150)
        self.left_frame.pack(side='left',fill='y', expand=False, padx=5, pady=5)

        self.import_button = ttk.Button(self.left_frame, text="Import experimental\n    excitation curve", width=20,command=self.load_file)
        self.import_button.pack(fill="x",padx=10,pady=(10,0))

        self.run_button = ttk.Button(self.left_frame, text='Run calculation',command=self.start_calc)
        self.run_button.pack(fill="x",padx=10,pady=(0,10))

        self.load_target_button = ttk.Button(self.left_frame, text='Load target',command=self.load_target)
        self.load_target_button.pack(fill="x",padx=10,pady=(15,0))

        self.save_target_button = ttk.Button(self.left_frame, text='Save target',command=self.save_to_json)
        self.save_target_button.pack(fill="x",padx=10,pady=(0,10))

        # Standard frame
        self.std_frame = ttk.LabelFrame(self.left_frame, text="Standard")
        self.std_frame.pack(fill='x', expand=False, padx=10, pady=5)

        ttk.Label(self.std_frame, text="Z:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.std_Z_entry = ttk.Entry(self.std_frame, width=10)
        self.std_Z_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.std_frame, text="H at. %:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.std_H_entry = ttk.Entry(self.std_frame, width=10)
        self.std_H_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.std_frame, text="Yield (Count/µC):").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.std_Yield_entry = ttk.Entry(self.std_frame, width=10)
        self.std_Yield_entry.grid(row=2, column=1, padx=5, pady=5 )


        # Options checkbox
        self.options_frame = ttk.LabelFrame(self.left_frame, text="Options")
        self.options_frame.pack(fill='x', expand=False, padx=10, pady=5)

        # Put frame here
        self.options_frame1 = ttk.Frame(self.options_frame)
        self.options_frame1.pack(fill='x', expand=False, padx=10, pady=5)
        
        ttk.Label(self.options_frame1, text="Beam Stdev (keV):").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.beamSD_entry = ttk.Entry(self.options_frame1,width=12)
        self.beamSD_entry.grid(row=0, column=1, padx=5, pady=(0,5),sticky='e')

        self.options_frame2 = ttk.Frame(self.options_frame)
        self.options_frame2.pack(fill='x', expand=False, padx=5, pady=5)

        self.Doppler_bool = tk.BooleanVar(value=True)
        self.options_doppler_entry = ttk.Checkbutton(self.options_frame2,text="Doppler", variable=self.Doppler_bool)
        self.options_doppler_entry.pack(padx=5, pady=(5,0),anchor='w')

        self.broadSave_bool = tk.BooleanVar(value=False)
        self.broadSave_entry = ttk.Checkbutton(self.options_frame2,text="Save broadening data", variable=self.broadSave_bool)
        self.broadSave_entry.pack(padx=5, pady=(0,5),anchor='w')        
        
        # Options checkbox
        self.chi_frameLabel = ttk.LabelFrame(self.left_frame, text="Chi-squared history")
        self.chi_frameLabel.pack(fill='x', expand=False, padx=10, pady=5)

        self.chi_frame = ttk.Frame(self.chi_frameLabel)
        self.chi_frame.pack(side='left', fill='both', expand=True, padx=10, pady=(10,10))

        self.figure1, self.ax1 = plt.subplots(figsize=(2, 1.5), dpi=100,constrained_layout=True)
        self.canvas1 = FigureCanvasTkAgg(self.figure1, master=self.chi_frame)
        self.canvas1.get_tk_widget().pack(expand=True, fill='both')

        self.scrollUp_button = ttk.Button(self.chi_frame, text="↑ Scroll Up ↑", command=self.scroll_up).pack(fill="x",padx=10,pady=(15,0))
        self.scrollDown_button =ttk.Button(self.chi_frame, text="↓ Scroll Down ↓", command=self.scroll_down).pack(fill="x",padx=10,pady=(0,0))

        ################################################################
        # Target Frame
        self.target_frame = ttk.LabelFrame(self.main_frame, text="Target Configurator")
        self.target_frame.pack(fill='both', expand=False, padx=10, pady=10)
    
        # Left Frame
        self.target_left_frame = ttk.Frame(self.target_frame)
        self.target_left_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)
    
        # Layer Frame
        self.layer_frame = ttk.LabelFrame(self.target_left_frame, text="Layers", height=150)
        self.layer_frame.pack(fill='x', expand=False, padx=10, pady=0)
    
        self.layer_listbox = tk.Listbox(self.layer_frame, exportselection=False,height=8)
        self.layer_listbox.pack(fill='both', expand=True, padx=5, pady=5)
        self.layer_listbox.bind('<<ListboxSelect>>', self.on_layer_select)
    
        # Layer Details
        self.detail_frame = ttk.LabelFrame(self.target_left_frame, text="Layer Details")
        self.detail_frame.pack(fill='x',expand=False, padx=10, pady=5)
    
        ttk.Label(self.detail_frame, text="Areal density (TFU):").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.AD_entry = ttk.Entry(self.detail_frame)
        self.AD_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(self.detail_frame, text="").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.AD_entry.bind('<FocusOut>', self.on_layer_entry_update)
        self.AD_entry.bind('<Return>', self.on_layer_entry_update)
    
        # Add/remove layer buttons
        self.left_button_frame = ttk.Frame(self.target_left_frame)
        self.left_button_frame.pack(padx=10, pady=5, anchor='center')
        layer_button_size = 18
    
        self.add_layer_button = ttk.Button(self.left_button_frame, text="Add Layer", width=layer_button_size, command=self.add_layer)
        self.add_layer_button.grid(row=0,column=0, padx=5)
    
        self.remove_layer_button = ttk.Button(self.left_button_frame, text="Remove Layer", width=layer_button_size, command=self.remove_layer)
        self.remove_layer_button.grid(row=0,column=1, padx=5)
    
        self.up_button = ttk.Button(self.left_button_frame, text="Move Up", width=layer_button_size,command=self.move_layer_up)
        self.up_button.grid(row=1,column=0, padx=5)
    
        self.down_button = ttk.Button(self.left_button_frame, text="Move Down", width=layer_button_size, command=self.move_layer_down)
        self.down_button.grid(row=1,column=1, padx=5)

        self.duplicate_button = ttk.Button(self.target_left_frame, text="Duplicate Layer", width=layer_button_size, command=self.duplicate_layer)
        self.duplicate_button.pack(fill="x",padx=25)
    
        # Right Frame
        self.target_right_frame = ttk.Frame(self.target_frame)
        self.target_right_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)
    
        # Layer Composition
        self.elem_frame = ttk.LabelFrame(self.target_right_frame, text="Elements",height=150)
        #self.elem_frame.pack_propagate(False)
        self.elem_frame.pack(fill='x', expand=False, padx=10, pady=0)
    
        self.elem_listbox = tk.Listbox(self.elem_frame,exportselection=False, height=8)
        self.elem_listbox.pack(fill='both', expand=True, padx=5, pady=5)
        self.elem_listbox.bind('<<ListboxSelect>>', self.on_element_select)
    
        # Element Details
        self.composition_frame = ttk.LabelFrame(self.target_right_frame, text="Elements Details")
        self.composition_frame.pack(fill='x', padx=10, pady=5)
    
        ttk.Label(self.composition_frame, text="Z:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.element_Z_entry = ttk.Entry(self.composition_frame)
        self.element_Z_entry.grid(row=0, column=1, padx=5, pady=5)
        self.element_Z_entry.bind("<FocusOut>", lambda event: self.element_on_entry_update(event, 'Z'))
        self.element_Z_entry.bind("<Return>", lambda event: self.element_on_entry_update(event, 'Z'))      

        ttk.Label(self.composition_frame, text="% at:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.composition_percent_entry = ttk.Entry(self.composition_frame)
        self.composition_percent_entry.grid(row=1, column=1, padx=5, pady=5)
        self.composition_percent_entry.bind("<FocusOut>", lambda event: self.element_on_entry_update(event, 'percent_at'))
        self.composition_percent_entry.bind("<Return>", lambda event: self.element_on_entry_update(event, 'percent_at'))

        # Element Button (add)
        self.right_button_frame = ttk.Frame(self.target_right_frame)
        self.right_button_frame.pack(anchor='center', padx=10, pady=5)

        self.add_element_button = ttk.Button(self.right_button_frame, text="Add Element to Layer", width=30, command=self.add_element)
        self.add_element_button.grid(row=0, padx=5)

        self.remove_element_button = ttk.Button(self.right_button_frame, text="Remove Element from Layer", width=30, command=self.remove_element)
        self.remove_element_button.grid(row=1, padx=5)

        #################################
        # Canvas for excitation curves
        self.exc_curve_frameLabel = ttk.LabelFrame(self.main_frame, text="Excitation curves")
        self.exc_curve_frameLabel.pack(fill='both', expand= False, padx=10, pady=(5,5))
        self.exc_curve_frame = ttk.Frame(self.exc_curve_frameLabel)
        self.exc_curve_frame.pack(side='left', fill='both', expand=True, padx=10, pady=(10,0))

        self.figure0, self.ax0 = plt.subplots(figsize=(10, 5),constrained_layout=True)
        
        # self.figure0.tight_layout()
        self.canvas = FigureCanvasTkAgg(self.figure0, master=self.exc_curve_frame)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.exc_curve_frame)
        self.toolbar.update()
        self.toolbar.pack(side='bottom', fill='x')

        self.canvas.get_tk_widget().pack(expand=True, fill='both')