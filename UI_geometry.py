import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,NavigationToolbar2Tk)

def create_widgets(self):
        # Main Frame
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill='both', expand=True)

        style = ttk.Style()
        style.configure("Center.TButton", font=("Segoe UI", 9), justify="center")
        ##################################################################
        # Left Frame
        self.left_frame = ttk.Frame(self.main_frame,width=150)
        self.left_frame.pack(side='left',fill='y', expand=False, padx=5, pady=5)

        self.import_button = ttk.Button(self.left_frame, text="Import excitation curve", width=20,command=self.load_curve)
        self.import_button.pack(fill="x",padx=10,pady=(10,0))

        self.run_button = ttk.Button(self.left_frame, text='Run\nCalculation', command=self.start_calc,style="Center.TButton")
        self.run_button.pack(fill="x",padx=10,pady=(0,0), ipady=10)

        self.extract_button = ttk.Button(self.left_frame, text='Extract H profile', command=self.plot_H_profile)
        self.extract_button.pack(fill="x",padx=10,pady=(0,10), ipady=5)     

        self.load_target_button = ttk.Button(self.left_frame, text='Load target',command=self.load_target)
        self.load_target_button.pack(fill="x",padx=10,pady=(10,0))

        self.save_target_button = ttk.Button(self.left_frame, text='Save target',command=self.save_json)
        self.save_target_button.pack(fill="x",padx=10,pady=(0,10))

        self.save_sim_curve_button = ttk.Button(self.left_frame, text='Save simulated curve data',command=self.save_sim_curve_txt)
        self.save_sim_curve_button.pack(fill="x",padx=10,pady=(10,5))

        #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
        # Standard frame
        self.std_frame = ttk.LabelFrame(self.left_frame, text="Standard")
        self.std_frame.pack(fill='x', expand=False, padx=10, pady=5)

        ttk.Label(self.std_frame, text="Yield (Count/µC):").grid(row=0, column=0, padx=15, pady=5, sticky='e')
        self.std_Yield_entry = ttk.Entry(self.std_frame, width=12)
        self.std_Yield_entry.grid(row=0, column=1, padx=5, pady=(5,0) )

        self.load_target_button = ttk.Button(self.std_frame, text='Load',command=self.load_std).grid(row=1, column=0, padx=5, pady=5,sticky='we')
        self.save_target_button = ttk.Button(self.std_frame, text='Save',command=lambda: self.save_json(type='Std')).grid(row=1, column=1, padx=5, pady=5,sticky='we')

        #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
        # Options checkbox
        self.options_frame = ttk.LabelFrame(self.left_frame, text="Options")
        self.options_frame.pack(fill='x', expand=False, padx=10, pady=5)

        self.options_frame1 = ttk.Frame(self.options_frame)
        self.options_frame1.pack(fill='x', expand=False, padx=10, pady=5)

        ttk.Label(self.options_frame1, text="Straggling model:").grid(row=0, column=0, padx=(0,5), pady=5, sticky='w')
        self.straggling_model_combobox = ttk.Combobox(self.options_frame1, values=["Rud", "Rud corr", "Bohr"], state="readonly", width=10)
        self.straggling_model_combobox.grid(row=0, column=1, padx=5, pady=(5,0), sticky='e')
        self.straggling_model_combobox.set("Rud corr")
        
        ttk.Label(self.options_frame1, text="Beam width SD (keV):").grid(row=1, column=0, padx=(0,5), pady=5, sticky='e')
        self.beamSD_entry = ttk.Entry(self.options_frame1, width=8)
        self.beamSD_entry.grid(row=1, column=1, padx=5, pady=(0,0),sticky='e')

        self.options_frame2 = ttk.Frame(self.options_frame)
        self.options_frame2.pack(fill='x', expand=False, padx=5, pady=0)

        self.Doppler_bool = tk.BooleanVar(value=True)
        self.options_doppler_entry = ttk.Checkbutton(self.options_frame2,text="Doppler", variable=self.Doppler_bool)
        self.options_doppler_entry.pack(padx=5, pady=(0,0),anchor='w')

        self.broadSave_bool = tk.BooleanVar(value=False)
        self.broadSave_entry = ttk.Checkbutton(self.options_frame2,text="Save broadening data", variable=self.broadSave_bool)
        self.broadSave_entry.pack(padx=5, pady=0 ,anchor='w')

        self.TrackTargetChange_bool = tk.BooleanVar(value=False)
        self.TrackTargetChange_entry = ttk.Checkbutton(self.options_frame2,text="Track target changes", variable=self.TrackTargetChange_bool)
        self.TrackTargetChange_entry.pack(padx=5, pady=(0,5),anchor='w')    
        
        #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
        # Chi-squared graph
        self.chi_frameLabel = ttk.LabelFrame(self.left_frame, text="Chi-squared history")
        self.chi_frameLabel.pack(fill='x', expand=False, padx=10, pady=5)

        self.chi_frame = ttk.Frame(self.chi_frameLabel)
        self.chi_frame.pack(side='left', fill='both', expand=True, padx=10, pady=(10,10))

        self.figure1, self.ax1 = plt.subplots(figsize=(2, 1.5), dpi=100,constrained_layout=True)
        self.canvas1 = FigureCanvasTkAgg(self.figure1, master=self.chi_frame)
        self.canvas1.get_tk_widget().pack(expand=True, fill='both')

        self.scrollUp_button = ttk.Button(self.chi_frame, text="↑ Scroll Up ↑", command=self.scroll_up).pack(fill="x",padx=5,pady=(15,0))
        self.scrollDown_button =ttk.Button(self.chi_frame, text="↓ Scroll Down ↓", command=self.scroll_down).pack(fill="x",padx=5,pady=(0,0))

        ################################################################
        # Target/Std Notebook Frame
        self.TargetStd_notebook = ttk.Notebook(self.main_frame)
        self.TargetStd_notebook.pack(fill='both', expand=False, padx=10, pady=10)

        self.target_frame = ttk.Frame(self.TargetStd_notebook)
        self.target_frame.pack(fill='both', expand=False, padx=10, pady=10)
        self.TargetStd_notebook.add(self.target_frame, text='Target')

        self.Std_frame = ttk.Frame(self.TargetStd_notebook)
        self.Std_frame.pack(fill='both', expand=False, padx=10, pady=10)
        self.TargetStd_notebook.add(self.Std_frame, text='Standard')

        # *=*=*=*=*=*=*=*=*=*=*=*=*=*=* TARGET *=*=*=*=*=*=*=*=*=*=*=*=*=*=*
        # Left Frame (layers)
        self.target_left_frame = ttk.Frame(self.target_frame)
        self.target_left_frame.pack(side='left', fill='both', expand=True, padx=(10,0), pady=10)
    
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
        
        # Buttons
        self.left_button_frame = ttk.Frame(self.target_left_frame)
        self.left_button_frame.pack(padx=10, pady=5, anchor='center')
        layer_button_size = 18
    
        self.add_layer_button = ttk.Button(self.left_button_frame, text="Add Layer", width=layer_button_size, command=self.on_add_layer_click)
        self.add_layer_button.grid(row=0,column=0, padx=5)
    
        self.remove_layer_button = ttk.Button(self.left_button_frame, text="Remove Layer", width=layer_button_size, command=self.on_remove_layer_click)
        self.remove_layer_button.grid(row=1,column=0, padx=5)
    
        self.up_button = ttk.Button(self.left_button_frame, text="Move Up", width=layer_button_size,command=self.on_move_layer_up_click)
        self.up_button.grid(row=0,column=1, padx=5)
    
        self.down_button = ttk.Button(self.left_button_frame, text="Move Down", width=layer_button_size, command=self.on_move_layer_down_click)
        self.down_button.grid(row=1,column=1, padx=5)

        self.duplicate_button = ttk.Button(self.left_button_frame, text="Duplicate Layer", width=(layer_button_size)*2+3, command=self.on_duplicate_layer_click)
        self.duplicate_button.grid(row=2,column=0, padx=5, pady=(5,0), columnspan=2)
        
        #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
        # Right Frame (elements)
        self.target_right_frame = ttk.Frame(self.target_frame)
        self.target_right_frame.pack(side='right', fill='both', expand=True, padx=(0,10), pady=10)
    
        # Layer Composition
        self.elem_frame = ttk.LabelFrame(self.target_right_frame, text="Elements",height=150)
        #self.elem_frame.pack_propagate(False)
        self.elem_frame.pack(fill='x', expand=False, padx=10, pady=0)
    
        self.elem_listbox = tk.Listbox(self.elem_frame,exportselection=False, height=8)
        self.elem_listbox.pack(fill='both', expand=True, padx=5, pady=5)
        self.elem_listbox.bind('<<ListboxSelect>>', self.on_element_select)
    
        # Element Details
        self.composition_frame = ttk.LabelFrame(self.target_right_frame, text="Elements Details")
        self.composition_frame.pack(fill='x',expand=False, padx=10, pady=5)
    
        ttk.Label(self.composition_frame, text="Z:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.element_Z_entry = ttk.Entry(self.composition_frame)
        self.element_Z_entry.grid(row=0, column=1, padx=5, pady=5)
        self.element_Z_entry.bind("<FocusOut>", lambda event: self.on_element_entry_update(event, 'Z'))
        self.element_Z_entry.bind("<Return>", lambda event: self.on_element_entry_update(event, 'Z'))      

        ttk.Label(self.composition_frame, text="% at:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.composition_percent_entry = ttk.Entry(self.composition_frame)
        self.composition_percent_entry.grid(row=1, column=1, padx=5, pady=0)
        self.composition_percent_entry.bind("<FocusOut>", lambda event: self.on_element_entry_update(event, 'percent_at'))
        self.composition_percent_entry.bind("<Return>", lambda event: self.on_element_entry_update(event, 'percent_at'))

        # Element Buttons
        self.right_button_frame = ttk.Frame(self.target_right_frame)
        self.right_button_frame.pack(anchor='center', padx=10, pady=5)

        self.add_element_button = ttk.Button(self.right_button_frame, text="Add Element", width=30, command=self.on_add_element_click)
        self.add_element_button.grid(row=0, padx=5)

        self.remove_element_button = ttk.Button(self.right_button_frame, text="Remove Element", width=30, command=self.on_remove_element_click)
        self.remove_element_button.grid(row=1, padx=5)

        self.norm_element_button = ttk.Button(self.right_button_frame, text="Isolate & Normalize", width=30, command=self.on_normalize_percentages_click)
        self.norm_element_button.grid(row=2, padx=5, pady=(5,0))

        # *=*=*=*=*=*=*=*=*=*=*=*=*=*=* Standard *=*=*=*=*=*=*=*=*=*=*=*=*=*=*
        # Layer Composition
        self.Std_elem_frame = ttk.LabelFrame(self.Std_frame, text="Elements",height=150)
        #self.elem_frame.pack_propagate(False)
        self.Std_elem_frame.pack(fill='x', expand=False, padx=20, pady=5)
    
        self.Std_elem_listbox = tk.Listbox(self.Std_elem_frame,exportselection=False, height=8)
        self.Std_elem_listbox.pack(fill='both', expand=True, padx=5, pady=5)
        self.Std_elem_listbox.bind('<<ListboxSelect>>', self.on_std_element_select)
    
        # Element Details
        self.Std_composition_frame = ttk.LabelFrame(self.Std_frame, text="Elements Details")
        self.Std_composition_frame.pack(fill='x', padx=20, pady=5)
    
        ttk.Label(self.Std_composition_frame, text="Z:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.Std_element_Z_entry = ttk.Entry(self.Std_composition_frame)
        self.Std_element_Z_entry.grid(row=0, column=1, padx=5, pady=5)
        self.Std_element_Z_entry.bind("<FocusOut>", lambda event: self.on_std_element_entry_update(event, 'Z'))
        self.Std_element_Z_entry.bind("<Return>", lambda event: self.on_std_element_entry_update(event, 'Z'))      

        ttk.Label(self.Std_composition_frame, text="% at:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.Std_composition_percent_entry = ttk.Entry(self.Std_composition_frame)
        self.Std_composition_percent_entry.grid(row=1, column=1, padx=5, pady=5)
        self.Std_composition_percent_entry.bind("<FocusOut>", lambda event: self.on_std_element_entry_update(event, 'percent_at'))
        self.Std_composition_percent_entry.bind("<Return>", lambda event: self.on_std_element_entry_update(event, 'percent_at'))

        # Element Buttons
        self.Std_right_button_frame = ttk.Frame(self.Std_frame)
        self.Std_right_button_frame.pack(anchor='center', padx=10, pady=5)

        self.Std_add_element_button = ttk.Button(self.Std_right_button_frame, text="Add Element", width=30, command=lambda: self.on_add_element_click(type='std'))
        self.Std_add_element_button.grid(row=0, padx=5)

        self.Std_remove_element_button = ttk.Button(self.Std_right_button_frame, text="Remove Element", width=30, command=lambda: self.on_remove_element_click(type='std'))
        self.Std_remove_element_button.grid(row=1, padx=5)

        self.Std_norm_element_button = ttk.Button(self.Std_right_button_frame, text="Isolate & Normalize", width=30, command=lambda: self.on_normalize_percentages_click(type='std'))
        self.Std_norm_element_button.grid(row=2, padx=5, pady=(5,0))

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