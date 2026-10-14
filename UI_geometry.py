import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,NavigationToolbar2Tk)

def create_widgets(self):
        # Menu bar
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load simulation", command=self.load_simulation)
        file_menu.add_command(label="Save simulation", command=self.save_simulation)

        target_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Target & Std", menu=target_menu)
        target_menu.add_command(label="Load target", command=self.load_target)
        target_menu.add_command(label="Save target", command=self.save_json)
        target_menu.add_separator()
        target_menu.add_command(label="Load standard", command=self.load_std)
        target_menu.add_command(label="Save standard", command=lambda: self.save_json(target_type='std'))

        plot_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Plot", menu=plot_menu)
        plot_menu.add_command(label="Rescale excitation curve", command=self.rescale_excitation_curve)
        self.autoscale_exc_bool = tk.BooleanVar(value=True)
        self.autoscale_menu = plot_menu
        plot_menu.add_checkbutton(label="Autoscale: ON", variable=self.autoscale_exc_bool)
        self.autoscale_menu_index = plot_menu.index("end")
        self.autoscale_exc_bool.trace_add("write", self.update_autoscale_menu_label)
        self.sim_markers_bool = tk.BooleanVar(value=True)
        plot_menu.add_checkbutton(label="Sim curve markers: ON", variable=self.sim_markers_bool)
        self.sim_markers_menu_index = plot_menu.index("end")
        self.sim_markers_bool.trace_add("write", self.update_sim_markers_menu_label)
        self.show_chi_energy_bounds_bool = tk.BooleanVar(value=True)
        plot_menu.add_checkbutton(label="Chi-squared energy bounds: ON", variable=self.show_chi_energy_bounds_bool)
        self.chi_energy_bounds_menu_index = plot_menu.index("end")
        self.show_chi_energy_bounds_bool.trace_add("write", self.update_chi_energy_bounds_menu_label)
        plot_menu.add_separator()
        plot_menu.add_command(label="Save simulated curve data", command=self.save_sim_curve_txt)
        plot_menu.add_command(label="Load sim curve as exp curve", command=self.generate_exp_from_sim)
        plot_menu.add_separator()
        plot_menu.add_command(label="Remove experimental curve", command=self.on_remove_exp)
        plot_menu.add_command(label="Remove simulated curve", command=self.on_remove_sim)
        plot_menu.add_separator()
        plot_menu.add_command(label="Reset Chi-squared history", command=self.reset_chi_history)

        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Settings", command=self.open_settings)
        settings_menu.add_command(label="Manual", command=self.open_manual)

        # Main Frame
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill='both', expand=True)

        style = ttk.Style()
        style.configure("Center.TButton", font=("Segoe UI", 9), justify="center")
        style.configure("Center.TMenubutton", font=("Segoe UI", 9), justify="center")
        ##################################################################
        # Left Frame
        self.left_frame = ttk.Frame(self.main_frame,width=150)
        self.left_frame.pack(side='left',fill='y', expand=False, padx=5, pady=5)

        self.import_button = ttk.Button(self.left_frame, text="Import excitation curve", width=20,command=self.load_curve)
        self.import_button.pack(fill="x",padx=10,pady=(10,0))

        self.run_frame = ttk.Frame(self.left_frame)
        self.run_frame.pack(fill="x", padx=10, pady=(0,0))

        self.run_button = ttk.Button(self.run_frame, text='Run Calculation', command=lambda: self.start_calc(mode="normal"), style="Center.TButton")
        self.run_button.pack(side='left', fill='x', expand=True, ipady=10)

        self.run_menu = tk.Menu(self, tearoff=0)
        self.run_menu.add_command(label="Run Calculation", command=lambda: self.start_calc(mode="normal"))
        self.run_menu.add_command(label="Run Calculation (custom energy range)", command=lambda: self.start_calc(mode="custom"))
        self.run_menu.add_command(label="Run Calculation (Loaded curve energy)", command=lambda: self.start_calc(mode="loaded_curve"))

        self.run_menu_button = ttk.Button(self.run_frame, text='▼', width=3, command=self._post_run_menu, style="Center.TButton")
        self.run_menu_button.pack(side='left', ipady=10)

        self.extract_button = ttk.Button(self.left_frame, text='Extract profile', command=self.plot_Z2_profile)
        self.extract_button.pack(fill="x",padx=10,pady=(0,10), ipady=5)     

        #self.load_target_button = ttk.Button(self.left_frame, text='Load target',command=self.load_target)
        #self.load_target_button.pack(fill="x",padx=10,pady=(10,0))
        #self.save_target_button = ttk.Button(self.left_frame, text='Save target',command=self.save_json)
        #self.save_target_button.pack(fill="x",padx=10,pady=(0,10))

        #self.save_sim_curve_button = ttk.Button(self.left_frame, text='Save simulated curve data',command=self.save_sim_curve_txt)
        #self.save_sim_curve_button.pack(fill="x",padx=10,pady=(10,5))

        #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
        # Standard frame
        self.std_frame = ttk.LabelFrame(self.left_frame, text="Standard")
        self.std_frame.pack(fill='x', expand=False, padx=10, pady=5)
        self.std_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(self.std_frame, text="Yield (Count/µC):").grid(row=0, column=0, padx=(10, 0), pady=5, ipadx=10, sticky='e')
        self.std_Yield_entry = ttk.Entry(self.std_frame, width=10)
        self.std_Yield_entry.grid(row=0, column=1, padx=10, pady=(5,0), sticky='we')

        self.load_std_button = ttk.Button(self.std_frame, text='Load', command=self.load_std)
        self.load_std_button.grid(row=1, column=0, padx=(10, 0), pady=5, sticky='we')
        self.save_std_button = ttk.Button(self.std_frame, text='Save', width=10, command=lambda: self.save_json(target_type='std'))
        self.save_std_button.grid(row=1, column=1, padx=10, pady=5, sticky='we')

        #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
        # Options checkbox
        self.options_frame = ttk.LabelFrame(self.left_frame, text="Options")
        self.options_frame.pack(fill='x', expand=False, padx=10, pady=5)

        self.options_frame1 = ttk.Frame(self.options_frame)
        self.options_frame1.pack(fill='x', expand=False, padx=10, pady=(0,5))
        self.options_frame1.grid_columnconfigure(1, weight=1)

        ttk.Label(self.options_frame1, text="Stopping model:").grid(row=0, column=0, padx=(0,5), pady=(5,0), sticky='w')
        self.stopping_model_combobox = ttk.Combobox(
            self.options_frame1,
            values=["SRIM", "SCS-25-Solid"],
            state="readonly",
            width=10,
        )
        self.stopping_model_combobox.grid(row=0, column=1, padx=5, pady=(5,0), sticky='we')
        self.stopping_model_combobox.set("SRIM")

        ttk.Label(self.options_frame1, text="Straggling model:").grid(row=1, column=0, padx=(0,5), pady=(5,0), sticky='w')
        self.straggling_model_combobox = ttk.Combobox(self.options_frame1, values=["Rud", "Rud corr", "Bohr"], state="readonly", width=10)
        self.straggling_model_combobox.grid(row=1, column=1, padx=5, pady=(5,0), sticky='we')
        self.straggling_model_combobox.set("Rud corr")
        
        ttk.Label(self.options_frame1, text="Beam width SD (keV):").grid(row=2, column=0, padx=(0,5), pady=(5,0), sticky='e')
        self.beamSD_entry = ttk.Entry(self.options_frame1, width=8)
        self.beamSD_entry.grid(row=2, column=1, padx=5, pady=(0,0),sticky='e')

        ttk.Label(self.options_frame1, text="Offset (keV):").grid(row=3, column=0, padx=(0,5), pady=5, sticky='e')
        self.offset_entry = ttk.Entry(self.options_frame1, width=8)
        self.offset_entry.grid(row=3, column=1, padx=5, pady=(0,0), sticky='e')
        self.offset_entry.insert(0, "0.0")

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
        self.chi_frame.pack(side='left', fill='both', expand=True, padx=10, pady=(5,10))

        self.chi_energy_range_frame = ttk.Frame(self.chi_frame)
        self.chi_energy_range_frame.pack(fill="x", padx=5, pady=(0, 6))
        ttk.Label(self.chi_energy_range_frame, text="Range (keV):").grid(row=0, column=0, columnspan=4, sticky="w")
        ttk.Label(self.chi_energy_range_frame, text="E Min").grid(row=1, column=0, padx=(10, 3), pady=(3, 0))
        self.chi_energy_min_entry = ttk.Entry(self.chi_energy_range_frame, width=7)
        self.chi_energy_min_entry.grid(row=1, column=1, padx=(0, 10), pady=(3, 0))
        self.chi_energy_min_entry.bind("<KeyRelease>", self.on_chi_energy_bounds_change)
        self.chi_energy_min_entry.bind("<FocusOut>", self.on_chi_energy_bounds_change)
        self.chi_energy_min_entry.bind("<Return>", self.on_chi_energy_bounds_change)
        ttk.Label(self.chi_energy_range_frame, text="E Max").grid(row=1, column=2, padx=(5, 3), pady=(3, 0))
        self.chi_energy_max_entry = ttk.Entry(self.chi_energy_range_frame, width=7)
        self.chi_energy_max_entry.grid(row=1, column=3, pady=(3, 0))
        self.chi_energy_max_entry.bind("<KeyRelease>", self.on_chi_energy_bounds_change)
        self.chi_energy_max_entry.bind("<FocusOut>", self.on_chi_energy_bounds_change)
        self.chi_energy_max_entry.bind("<Return>", self.on_chi_energy_bounds_change)

        self.figure1, self.ax1 = plt.subplots(figsize=(2, 1.5), dpi=100,constrained_layout=True)
        self.canvas1 = FigureCanvasTkAgg(self.figure1, master=self.chi_frame)
        self.canvas1.get_tk_widget().pack(expand=True, fill='both', pady=(5,0))

        self.chi_bounds_legend_frame = ttk.Frame(self.chi_frame)
        self.chi_bounds_legend_frame.pack(fill="x", pady=(2, 0))
        tk.Label(self.chi_bounds_legend_frame, text="■ Current bounds", fg="cornflowerblue").pack(side="left")
        tk.Label(self.chi_bounds_legend_frame, text="■ Different bounds", fg="gray").pack(side="left", padx=(8, 0))

        self.chi_scroll_frame = ttk.Frame(self.chi_frame)
        self.chi_scroll_frame.pack(fill="x", pady=(10, 0))
        self.chi_scroll_frame.grid_columnconfigure((0, 1), weight=1, uniform="chi_scroll_buttons")
        ttk.Button(self.chi_scroll_frame, text="↑ Scroll Up ↑", command=self.scroll_up).grid(row=0, column=0, sticky="ew", padx=(5, 2))
        ttk.Button(self.chi_scroll_frame, text="↓ Scroll Down ↓", command=self.scroll_down).grid(row=0, column=1, sticky="ew", padx=(2, 5))

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
        
        # --- WITH SCROLLBAR (commented out) ---
        # # Frame to hold listbox and scrollbar
        # self.layer_listbox_frame = ttk.Frame(self.layer_frame)
        # self.layer_listbox_frame.pack(fill='both', expand=True, padx=5, pady=5)
        # 
        # self.layer_listbox = tk.Listbox(self.layer_listbox_frame, exportselection=False, height=8)
        # self.layer_listbox.pack(side='left', fill='both', expand=True)
        # 
        # # Scrollbar for layer listbox
        # self.layer_scrollbar = ttk.Scrollbar(self.layer_listbox_frame, orient='vertical', command=self.layer_listbox.yview)
        # self.layer_scrollbar.pack(side='right', fill='y')
        # self.layer_listbox.config(yscrollcommand=self.layer_scrollbar.set)
        # 
        # self.layer_listbox.bind('<<ListboxSelect>>', self.on_layer_select)
    
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
        
        # --- WITH SCROLLBAR (commented out) ---
        # # Frame to hold listbox and scrollbar
        # self.elem_listbox_frame = ttk.Frame(self.elem_frame)
        # self.elem_listbox_frame.pack(fill='both', expand=True, padx=5, pady=5)
        # 
        # self.elem_listbox = tk.Listbox(self.elem_listbox_frame, exportselection=False, height=8)
        # self.elem_listbox.pack(side='left', fill='both', expand=True)
        # 
        # # Scrollbar for element listbox
        # self.elem_scrollbar = ttk.Scrollbar(self.elem_listbox_frame, orient='vertical', command=self.elem_listbox.yview)
        # self.elem_scrollbar.pack(side='right', fill='y')
        # self.elem_listbox.config(yscrollcommand=self.elem_scrollbar.set)
        # 
        # self.elem_listbox.bind('<<ListboxSelect>>', self.on_element_select)
    
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

        self.norm_element_button = ttk.Button(self.right_button_frame, text="Isolate & Normalize", width=30, command=self.on_lock_and_normalize_click)
        self.norm_element_button.grid(row=2, padx=5, pady=(5,0))

        # *=*=*=*=*=*=*=*=*=*=*=*=*=*=* Standard *=*=*=*=*=*=*=*=*=*=*=*=*=*=*
        # Layer Composition
        self.Std_elem_frame = ttk.LabelFrame(self.Std_frame, text="Elements",height=150)
        #self.elem_frame.pack_propagate(False)
        self.Std_elem_frame.pack(fill='x', expand=False, padx=20, pady=(10,5))
    
        self.Std_elem_listbox = tk.Listbox(self.Std_elem_frame,exportselection=False, height=8)
        self.Std_elem_listbox.pack(fill='both', expand=True, padx=5, pady=5)
        self.Std_elem_listbox.bind('<<ListboxSelect>>', self.on_std_element_select)
        
        # --- WITH SCROLLBAR (commented out) ---
        # # Frame to hold listbox and scrollbar
        # self.Std_elem_listbox_frame = ttk.Frame(self.Std_elem_frame)
        # self.Std_elem_listbox_frame.pack(fill='both', expand=True, padx=5, pady=5)
        # 
        # self.Std_elem_listbox = tk.Listbox(self.Std_elem_listbox_frame, exportselection=False, height=8)
        # self.Std_elem_listbox.pack(side='left', fill='both', expand=True)
        # 
        # # Scrollbar for standard element listbox
        # self.Std_elem_scrollbar = ttk.Scrollbar(self.Std_elem_listbox_frame, orient='vertical', command=self.Std_elem_listbox.yview)
        # self.Std_elem_scrollbar.pack(side='right', fill='y')
        # self.Std_elem_listbox.config(yscrollcommand=self.Std_elem_scrollbar.set)
        # 
        # self.Std_elem_listbox.bind('<<ListboxSelect>>', self.on_std_element_select)
    
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

        self.Std_add_element_button = ttk.Button(self.Std_right_button_frame, text="Add Element", width=30, command=lambda: self.on_add_element_click(target_type='std'))
        self.Std_add_element_button.grid(row=0, padx=5)

        self.Std_remove_element_button = ttk.Button(self.Std_right_button_frame, text="Remove Element", width=30, command=lambda: self.on_remove_element_click(target_type='std'))
        self.Std_remove_element_button.grid(row=1, padx=5)

        self.Std_norm_element_button = ttk.Button(self.Std_right_button_frame, text="Isolate & Normalize", width=30, command=lambda: self.on_lock_and_normalize_click(target_type='std'))
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