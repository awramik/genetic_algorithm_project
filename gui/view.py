import tkinter as tk
from tkinter import ttk
from gui.styles import COLORS, FONTS


class MainView:
    def __init__(self, root):
        self.root = root

        self.main_container = None
        self.sidebar = None
        self.exp_name_entry = None
        self.cross_combo_real = None
        self.alpha_entry = None
        self.notebook = None
        self.tab_binary = None
        self.tab_real = None
        self.tab_compare = None
        self.start_button = None
        self.progress_bar = None
        self.plot_panel = None
        self.main_container = None
        self.status_label = None
        self.console_label = None
        self.console_frame = None
        self.results_console = None

        self.setup_ui()

    def setup_ui(self):
        self.main_container = tk.Frame(self.root, bg=COLORS["bg_main"])
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # LEFT PANEL
        self.sidebar = tk.Frame(self.main_container, bg=COLORS["bg_panel"], width=420)
        self.sidebar.pack(side="left", fill="y", padx=(0, 20))
        self.sidebar.pack_propagate(False)

        # EXPERIMENT NAME
        exp_frame = tk.Frame(self.sidebar, bg=COLORS["bg_panel"])
        exp_frame.pack(fill="x", padx=15, pady=(15, 5))
        tk.Label(exp_frame, text="Experiment:", bg=COLORS["bg_panel"], font=FONTS["header"], fg=COLORS["accent"]).pack(
            side="left")
        self.exp_name_entry = tk.Entry(exp_frame, font=FONTS["body"], relief="solid", bd=1)
        self.exp_name_entry.insert(0, "Hypersphere_Test")
        self.exp_name_entry.pack(side="left", fill="x", expand=True, padx=(10, 0))

        # TABS
        self.notebook = ttk.Notebook(self.sidebar)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=(5, 10))

        self.tab_binary = tk.Frame(self.notebook, bg=COLORS["bg_panel"])
        self.tab_real = tk.Frame(self.notebook, bg=COLORS["bg_panel"])
        self.tab_compare = tk.Frame(self.notebook, bg=COLORS["bg_panel"])

        self.notebook.add(self.tab_binary, text="Binary (P1)")
        self.notebook.add(self.tab_real, text="Real (P2)")
        self.notebook.add(self.tab_compare, text="Comparison")

        self.setup_binary_tab()
        self.setup_real_tab()
        self.setup_comparison_tab()

        # SHARED PARAMS
        self.setup_shared_parameters()

        # START & PROGRESS
        self.start_button = tk.Button(self.sidebar, text="START EVOLUTION 🧬",
                                      bg=COLORS["accent"], fg="white", font=FONTS["button"], pady=12, cursor="hand2")
        self.start_button.pack(fill="x", padx=20, pady=10)

        self.progress_bar = ttk.Progressbar(self.sidebar, style="SGA.Horizontal.TProgressbar", mode="determinate")
        self.progress_bar.pack(fill="x", padx=20, pady=5)

        # RIGHT FRAME
        self.right_area = tk.Frame(self.main_container, bg="white")
        self.right_area.pack(side="right", fill="both", expand=True)

        # RESULTS
        self.console_frame = tk.Frame(self.right_area, bg=COLORS.get("bg_panel", "white"))
        self.console_frame.pack(side="bottom", fill="x", padx=10, pady=10)

        self.console_label = tk.Label(self.console_frame, text="Final Results:",
                                      font=FONTS.get("header", ("Arial", 11, "bold")),
                                      bg=COLORS.get("bg_panel", "white"))
        self.console_label.pack(anchor="w")

        self.results_console = tk.Text(self.console_frame, height=7, wrap="word",
                                       font=FONTS.get("body", ("Consolas", 10)),
                                       relief="solid", bd=1, bg="#f9f9f9")
        self.results_console.pack(fill="x", pady=(5, 0))
        self.results_console.insert("1.0", "Run the evolution to see the results...")
        self.results_console.config(state="disabled")

        # 2. PLOT
        self.plot_panel = tk.Frame(self.right_area, bg="white")
        self.plot_panel.pack(side="top", fill="both", expand=True)

        # 3. STATUS LABEL
        self.status_label = tk.Label(self.root, text="Ready. Select parameters and run.",
                                     anchor="w", bg=COLORS["bg_main"], fg=COLORS["text_muted"], font=FONTS["body"])
        self.status_label.pack(side="bottom", fill="x", padx=20, pady=5)

    def setup_binary_tab(self):
        self.add_label(self.tab_binary, "Bits per Variable:")
        self.bits_entry = self.add_entry(self.tab_binary, "20")

        self.add_label(self.tab_binary, "Inversion Rate:")
        self.inv_entry = self.add_entry(self.tab_binary, "0.05")

        self.add_label(self.tab_binary, "Crossover Method:")
        self.cross_combo_bin = ttk.Combobox(self.tab_binary, values=["one_point", "two_point", "uniform", "grainy"],
                                            state="readonly")
        self.cross_combo_bin.set("one_point")
        self.cross_combo_bin.pack(fill="x", padx=20, pady=5)

        self.add_label(self.tab_binary, "Mutation Method:")
        self.mut_combo_bin = ttk.Combobox(self.tab_binary, values=["bit_flip", "boundary", "single_point", "two_point"],
                                          state="readonly")
        self.mut_combo_bin.set("bit_flip")
        self.mut_combo_bin.pack(fill="x", padx=20, pady=5)

    def setup_real_tab(self):
        # --- CROSSOVER ---
        self.cross_sect = tk.Frame(self.tab_real, bg=COLORS["bg_panel"])
        self.cross_sect.pack(fill="x", pady=5)

        self.add_label(self.cross_sect, "Crossover Method:")
        self.cross_combo_real = ttk.Combobox(
            self.cross_sect,
            values=["arithmetic", "linear", "blx_alpha", "blx_alpha_beta", "averaging"],
            state="readonly"
        )
        self.cross_combo_real.set("arithmetic")
        self.cross_combo_real.pack(fill="x", padx=20, pady=5)

        # BLX (Alfa, Beta)
        self.blx_frame = tk.Frame(self.cross_sect, bg=COLORS["bg_panel"])

        # Tworzymy widgety, ale nie pakujemy ich jeszcze
        self.alpha_label = tk.Label(self.blx_frame, text="BLX Alpha (\u03b1):", font=FONTS["header"],
                                    bg=COLORS["bg_panel"], fg=COLORS["text_main"])
        self.alpha_entry = tk.Entry(self.blx_frame, font=FONTS["body"], relief="solid", bd=1)
        self.alpha_entry.insert(0, "0.5")

        self.beta_label = tk.Label(self.blx_frame, text="BLX Beta (\u03b2):", font=FONTS["header"],
                                   bg=COLORS["bg_panel"], fg=COLORS["text_main"])
        self.beta_entry = tk.Entry(self.blx_frame, font=FONTS["body"], relief="solid", bd=1)
        self.beta_entry.insert(0, "0.75")

        # --- MUTATION ---
        self.mut_sect = tk.Frame(self.tab_real, bg=COLORS["bg_panel"])
        self.mut_sect.pack(fill="x", pady=5)

        self.add_label(self.mut_sect, "Mutation Method:")
        self.mut_combo_real = ttk.Combobox(self.mut_sect, values=["uniform", "gaussian"], state="readonly")
        self.mut_combo_real.set("gaussian")
        self.mut_combo_real.pack(fill="x", padx=20, pady=5)

        # Gaussian Sigma
        self.gauss_frame = tk.Frame(self.mut_sect, bg=COLORS["bg_panel"])
        self.sigma_label = tk.Label(self.gauss_frame, text="Gauss Sigma (\u03c3):", font=FONTS["header"],
                                    bg=COLORS["bg_panel"], fg=COLORS["text_main"])
        self.sigma_entry = tk.Entry(self.gauss_frame, font=FONTS["body"], relief="solid", bd=1)
        self.sigma_entry.insert(0, "0.5")

    def update_visibility(self, event=None):
        cross_val = self.cross_combo_real.get()
        mut_val = self.mut_combo_real.get()

        # 1. BLX crossover
        if "blx" in cross_val:
            self.blx_frame.pack(fill="x")  # Pakuje się NA KOŃCU swojej sekcji (pod dropdownem)
            self.alpha_label.pack(anchor="w", padx=20, pady=(10, 0))
            self.alpha_entry.pack(fill="x", padx=20, pady=5)

            if cross_val == "blx_alpha_beta":
                self.beta_label.pack(anchor="w", padx=20, pady=(10, 0))
                self.beta_entry.pack(fill="x", padx=20, pady=5)
            else:
                self.beta_label.pack_forget()
                self.beta_entry.pack_forget()
        else:
            self.blx_frame.pack_forget()

        # 2. Gaussian mutation
        if mut_val == "gaussian":
            self.gauss_frame.pack(fill="x")
            self.sigma_label.pack(anchor="w", padx=20, pady=(10, 0))
            self.sigma_entry.pack(fill="x", padx=20, pady=5)
        else:
            self.gauss_frame.pack_forget()

    def setup_comparison_tab(self):
        """Sets up the Matchup Board in the Comparison tab."""

        self.matchup_container = tk.Frame(self.tab_compare, bg=COLORS["bg_panel"])
        self.matchup_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Header
        tk.Label(self.matchup_container, text="⚔️ MATCHUP SUMMARY",
                 font=FONTS.get("header", ("Arial", 12, "bold")),
                 bg=COLORS["bg_panel"], fg=COLORS["accent"]).pack(pady=(0, 15))

        self.matchup_info = tk.Text(
            self.matchup_container,
            height=10,
            font=("Consolas", 9),
            bg="#f0f0f0",
            fg=COLORS["text_main"],
            relief="flat",
            padx=10, pady=10
        )
        self.matchup_info.pack(fill="both", expand=True)
        self.matchup_info.insert("1.0", "Select Comparison tab to refresh data...")
        self.matchup_info.config(state="disabled")

        tk.Label(
            self.matchup_container,
            text="* Settings gathered from other tabs",
            font=("Arial", 7, "italic"),
            bg=COLORS["bg_panel"], fg=COLORS["text_muted"]
        ).pack(side="bottom", pady=2)

    def setup_shared_parameters(self):
        shared_frame = tk.LabelFrame(self.sidebar, text="Shared Parameters", bg=COLORS["bg_panel"],
                                     font=FONTS["header"])
        shared_frame.pack(fill="x", padx=15, pady=10)

        def add_param_row(row, label1, widget1, label2, widget2):
            tk.Label(shared_frame, text=label1, bg=COLORS["bg_panel"]).grid(row=row, column=0, sticky="w", pady=6,
                                                                            padx=(10, 2))
            widget1.grid(row=row, column=1, sticky="w", pady=6, padx=2)
            tk.Label(shared_frame, text=label2, bg=COLORS["bg_panel"]).grid(row=row, column=2, sticky="w", pady=6,
                                                                            padx=(15, 2))
            widget2.grid(row=row, column=3, sticky="w", pady=6, padx=(2, 10))

        self.pop_entry = tk.Entry(shared_frame, width=10)
        self.pop_entry.insert(0, "50")
        self.gen_entry = tk.Entry(shared_frame, width=10)
        self.gen_entry.insert(0, "100")
        add_param_row(0, "Population:", self.pop_entry, "Generations:", self.gen_entry)

        self.dim_entry = tk.Entry(shared_frame, width=10)
        self.dim_entry.insert(0, "2")
        self.opt_combo = ttk.Combobox(shared_frame, values=["Min", "Max"], state="readonly", width=7)
        self.opt_combo.set("Min")
        add_param_row(1, "Dimensions:", self.dim_entry, "Opt Type:", self.opt_combo)

        self.cr_entry = tk.Entry(shared_frame, width=10)
        self.cr_entry.insert(0, "0.8")
        self.mr_entry = tk.Entry(shared_frame, width=10)
        self.mr_entry.insert(0, "0.1")
        add_param_row(2, "Cross Rate:", self.cr_entry, "Mut Rate:", self.mr_entry)

        self.lb_entry = tk.Entry(shared_frame, width=10)
        self.lb_entry.insert(0, "-5.0")
        self.ub_entry = tk.Entry(shared_frame, width=10)
        self.ub_entry.insert(0, "5.0")
        add_param_row(3, "Lower Bound:", self.lb_entry, "Upper Bound:", self.ub_entry)

        self.elite_entry = tk.Entry(shared_frame, width=10)
        self.elite_entry.insert(0, "2")
        self.selection_combo = ttk.Combobox(shared_frame, values=["best", "roulette", "tournament"], state="readonly", width=8)
        self.selection_combo.set("tournament")
        add_param_row(4, "Elite Size:", self.elite_entry, "Selection:", self.selection_combo)

    def add_label(self, parent, text):
        tk.Label(parent, text=text, font=FONTS["header"], bg=COLORS["bg_panel"], fg=COLORS["text_main"]).pack(
            anchor="w", padx=20, pady=(10, 0))

    def add_entry(self, parent, default_val):
        entry = tk.Entry(parent, font=FONTS["body"], relief="solid", bd=1)
        entry.insert(0, default_val)
        entry.pack(fill="x", padx=20, pady=5)
        return entry
    