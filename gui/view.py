import customtkinter as ctk

class MainView:
    def __init__(self, root):
        self.root = root
        self.setup_ui()

    def setup_ui(self):
        # Main container
        self.main_container = ctk.CTkFrame(self.root, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # === LEFT PANEL (Sidebar) ===
        self.sidebar = ctk.CTkFrame(self.main_container, width=420)
        self.sidebar.pack(side="left", fill="y", padx=(0, 20))
        self.sidebar.pack_propagate(False)

        # Experiment
        exp_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        exp_frame.pack(fill="x", padx=15, pady=(15, 5))
        ctk.CTkLabel(exp_frame, text="Experiment:", font=ctk.CTkFont(weight="bold")).pack(side="left")
        self.exp_name_entry = ctk.CTkEntry(exp_frame)
        self.exp_name_entry.insert(0, "Hypersphere_Test")
        self.exp_name_entry.pack(side="left", fill="x", expand=True, padx=(10, 0))

        # Tabview
        self.notebook = ctk.CTkTabview(self.sidebar)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=(5, 10))

        self.tab_binary = self.notebook.add("Binary (P1)")
        self.tab_real = self.notebook.add("Real (P2)")
        self.tab_compare = self.notebook.add("Comparison")

        self.setup_binary_tab()
        self.setup_real_tab()
        self.setup_comparison_tab()

        # SHARED PARAMETERS
        self.setup_shared_parameters()

        # START & PROGRESS BAR
        self.start_button = ctk.CTkButton(self.sidebar, text="START EVOLUTION 🧬", font=ctk.CTkFont(weight="bold", size=14), height=45)
        self.start_button.pack(fill="x", padx=20, pady=10)

        self.progress_bar = ctk.CTkProgressBar(self.sidebar)
        self.progress_bar.pack(fill="x", padx=20, pady=10)
        self.progress_bar.set(0)

        # === RIGHT PANEL ===
        self.right_area = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.right_area.pack(side="right", fill="both", expand=True)

        # RESULTS CONSOLE
        self.console_frame = ctk.CTkFrame(self.right_area)
        self.console_frame.pack(side="bottom", fill="x", pady=(15, 0))

        self.console_header = ctk.CTkFrame(self.console_frame, fg_color="transparent")
        self.console_header.pack(fill="x", padx=10, pady=(5, 0))

        self.console_label = ctk.CTkLabel(self.console_header, text="📊 FINAL RESULTS",
                                          font=ctk.CTkFont(weight="bold", size=14))
        self.console_label.pack(side="left")

        self.open_logs_btn = ctk.CTkButton(
            self.console_header,
            text="↗ Open logs folder",
            width=140,
            height=25,
            fg_color="#4E6E5D",
            hover_color="#2C3E35"
        )
        self.open_logs_btn.pack(side="right")

        self.results_console = ctk.CTkTextbox(
            self.console_frame,
            height=250,
            font=ctk.CTkFont("Consolas", 15),
            activate_scrollbars=True
        )
        self.results_console.pack(fill="x", padx=10, pady=(0, 10))
        self.results_console.insert("1.0", "Run the evolution to see the results...")
        self.results_console.configure(state="disabled")

        # PLOT PANEL
        self.plot_panel = ctk.CTkFrame(self.right_area, fg_color="#B5C7BC", corner_radius=10)
        self.plot_panel.pack(side="top", fill="both", expand=True)

        # BOTTOM STATUS
        self.status_label = ctk.CTkLabel(self.root, text="Ready. Select parameters and run.", text_color="gray", font=ctk.CTkFont(size=13))
        self.status_label.pack(side="bottom", fill="x", padx=20, pady=5)

    def setup_binary_tab(self):
        self.add_label(self.tab_binary, "Bits per Variable:")
        self.bits_entry = self.add_entry(self.tab_binary, "20")

        self.add_label(self.tab_binary, "Inversion Rate:")
        self.inv_entry = self.add_entry(self.tab_binary, "0.05")

        self.add_label(self.tab_binary, "Crossover Method:")
        self.cross_combo_bin = ctk.CTkOptionMenu(self.tab_binary, values=["One-Point", "Two-Point", "Uniform", "Grainy"])
        self.cross_combo_bin.set("One-Point")
        self.cross_combo_bin.pack(fill="x", padx=20, pady=5)

        self.add_label(self.tab_binary, "Mutation Method:")
        self.mut_combo_bin = ctk.CTkOptionMenu(self.tab_binary, values=["Bit-Flip", "Boundary", "Single-Point", "Two-Point"])
        self.mut_combo_bin.set("Bit-Flip")
        self.mut_combo_bin.pack(fill="x", padx=20, pady=5)

    def setup_real_tab(self):
        self.cross_sect = ctk.CTkFrame(self.tab_real, fg_color="transparent")
        self.cross_sect.pack(fill="x", pady=5)

        self.add_label(self.cross_sect, "Crossover Method:")
        self.cross_combo_real = ctk.CTkOptionMenu(self.cross_sect, values=["Arithmetic", "Linear", "BLX-α", "BLX-α-β", "Averaging"], command=self.update_visibility)
        self.cross_combo_real.set("Arithmetic")
        self.cross_combo_real.pack(fill="x", padx=20, pady=5)

        # BLX
        self.blx_frame = ctk.CTkFrame(self.cross_sect, fg_color="transparent")
        self.alpha_label = ctk.CTkLabel(self.blx_frame, text="BLX Alpha (α):", font=ctk.CTkFont(weight="bold"))
        self.alpha_entry = ctk.CTkEntry(self.blx_frame)
        self.alpha_entry.insert(0, "0.5")

        self.beta_label = ctk.CTkLabel(self.blx_frame, text="BLX Beta (β):", font=ctk.CTkFont(weight="bold"))
        self.beta_entry = ctk.CTkEntry(self.blx_frame)
        self.beta_entry.insert(0, "0.75")

        self.mut_sect = ctk.CTkFrame(self.tab_real, fg_color="transparent")
        self.mut_sect.pack(fill="x", pady=5)

        self.add_label(self.mut_sect, "Mutation Method:")
        self.mut_combo_real = ctk.CTkOptionMenu(self.mut_sect, values=["Uniform", "Gaussian"], command=self.update_visibility)
        self.mut_combo_real.set("Gaussian")
        self.mut_combo_real.pack(fill="x", padx=20, pady=5)

        # Gaussian
        self.gauss_frame = ctk.CTkFrame(self.mut_sect, fg_color="transparent")
        self.sigma_label = ctk.CTkLabel(self.gauss_frame, text="Gauss Sigma (σ):", font=ctk.CTkFont(weight="bold"))
        self.sigma_entry = ctk.CTkEntry(self.gauss_frame)
        self.sigma_entry.insert(0, "0.5")

    def update_visibility(self, event=None):
        cross_val = self.cross_combo_real.get()
        mut_val = self.mut_combo_real.get()

        if "BLX" in cross_val:
            self.blx_frame.pack(fill="x")
            self.alpha_label.pack(anchor="w", padx=20, pady=(5, 0))
            self.alpha_entry.pack(fill="x", padx=20, pady=0)
            if cross_val == "BLX-α-β":
                self.beta_label.pack(anchor="w", padx=20, pady=(5, 0))
                self.beta_entry.pack(fill="x", padx=20, pady=0)
            else:
                self.beta_label.pack_forget()
                self.beta_entry.pack_forget()
        else:
            self.blx_frame.pack_forget()

        if mut_val == "Gaussian":
            self.gauss_frame.pack(fill="x")
            self.sigma_label.pack(anchor="w", padx=20, pady=(5, 0))
            self.sigma_entry.pack(fill="x", padx=20, pady=0)
        else:
            self.gauss_frame.pack_forget()

    def setup_comparison_tab(self):
        self.matchup_container = ctk.CTkFrame(self.tab_compare, fg_color="transparent")
        self.matchup_container.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            self.matchup_container,
            text="⚔️ MATCHUP SUMMARY",
            font=ctk.CTkFont(weight="bold", size=16),
            text_color="#D3E0D7"
        ).pack(pady=(0, 15))

        # --- BINARY ---
        self.bin_card = ctk.CTkFrame(self.matchup_container, fg_color="#24332D", corner_radius=8)
        self.bin_card.pack(fill="x", pady=(0, 5))

        self.bin_title = ctk.CTkLabel(self.bin_card, text="💻 BINARY ALGORITHM", font=ctk.CTkFont(weight="bold", size=15), text_color="#FFFFFF")
        self.bin_title.pack(pady=(10, 0))

        self.bin_stats = ctk.CTkLabel(self.bin_card, text="Crossover: ---\nMutation: ---", font=ctk.CTkFont(size=14), justify="center", text_color="#D3E0D7")
        self.bin_stats.pack(pady=(5, 10))

        # --- VS ---
        self.vs_badge = ctk.CTkLabel(self.matchup_container, text="VS", font=ctk.CTkFont(weight="bold", size=15), text_color="#4E6E5D")
        self.vs_badge.pack(pady=5)

        # --- REAL ---
        self.real_card = ctk.CTkFrame(self.matchup_container, fg_color="#24332D", corner_radius=8)
        self.real_card.pack(fill="x", pady=(5, 15))

        self.real_title = ctk.CTkLabel(self.real_card, text="📈 REAL ALGORITHM", font=ctk.CTkFont(weight="bold", size=15), text_color="#FFFFFF")
        self.real_title.pack(pady=(10, 0))

        self.real_stats = ctk.CTkLabel(self.real_card, text="Crossover: ---\nMutation: ---", font=ctk.CTkFont(size=14), justify="center", text_color="#D3E0D7")
        self.real_stats.pack(pady=(5, 10))

        ctk.CTkLabel(
            self.matchup_container,
            text="* Settings gathered from other tabs",
            font=ctk.CTkFont(size=12, slant="italic"),
            text_color="gray"
        ).pack(side="bottom", pady=5)

    def setup_shared_parameters(self):
        shared_frame = ctk.CTkFrame(self.sidebar)
        shared_frame.pack(fill="x", padx=15, pady=10)
        for i in range(4):
            shared_frame.grid_columnconfigure(i, weight=1)

        ctk.CTkLabel(
            shared_frame,
            text="Shared Parameters",
            font=ctk.CTkFont(weight="bold", size=14)
        ).grid(row=0, column=0, columnspan=4, pady=(12, 8), sticky="ew")

        def add_param_row(row, label1, widget1, label2, widget2):
            ctk.CTkLabel(shared_frame, text=label1).grid(row=row, column=0, sticky="w", pady=8, padx=(15, 5))
            widget1.grid(row=row, column=1, sticky="w", pady=8, padx=5)
            ctk.CTkLabel(shared_frame, text=label2).grid(row=row, column=2, sticky="w", pady=8, padx=(15, 5))
            widget2.grid(row=row, column=3, sticky="w", pady=8, padx=(5, 15))

        self.pop_entry = ctk.CTkEntry(shared_frame, width=80)
        self.pop_entry.insert(0, "50")
        self.gen_entry = ctk.CTkEntry(shared_frame, width=80)
        self.gen_entry.insert(0, "100")
        add_param_row(1, "Population:", self.pop_entry, "Generations:", self.gen_entry)

        self.dim_entry = ctk.CTkEntry(shared_frame, width=80)
        self.dim_entry.insert(0, "2")
        self.opt_combo = ctk.CTkOptionMenu(shared_frame, values=["Min", "Max"], width=80)
        self.opt_combo.set("Min")
        add_param_row(2, "Dimensions:", self.dim_entry, "Opt Type:", self.opt_combo)

        self.cr_entry = ctk.CTkEntry(shared_frame, width=80)
        self.cr_entry.insert(0, "0.8")
        self.mr_entry = ctk.CTkEntry(shared_frame, width=80)
        self.mr_entry.insert(0, "0.1")
        add_param_row(3, "Cross Rate:", self.cr_entry, "Mut Rate:", self.mr_entry)

        self.lb_entry = ctk.CTkEntry(shared_frame, width=80)
        self.lb_entry.insert(0, "-5.0")
        self.ub_entry = ctk.CTkEntry(shared_frame, width=80)
        self.ub_entry.insert(0, "5.0")
        add_param_row(4, "Lower Bound:", self.lb_entry, "Upper Bound:", self.ub_entry)

        self.elite_entry = ctk.CTkEntry(shared_frame, width=80)
        self.elite_entry.insert(0, "2")
        self.selection_combo = ctk.CTkOptionMenu(shared_frame, values=["Best", "Roulette", "Tournament"], width=80)
        self.selection_combo.set("Tournament")
        add_param_row(5, "Elite Size:", self.elite_entry, "Selection:", self.selection_combo)

    def add_label(self, parent, text):
        ctk.CTkLabel(parent, text=text, font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20, pady=(10, 0))

    def add_entry(self, parent, default_val):
        entry = ctk.CTkEntry(parent)
        entry.insert(0, default_val)
        entry.pack(fill="x", padx=20, pady=5)
        return entry
