import tkinter as tk
from tkinter import ttk, messagebox

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from ga.genetic_algorithm import run_genetic_algorithm
from visualization.plotting import create_convergence_figure
from results.logger import save_results


def launch_gui():
    def run_algorithm():
        try:
            # --- ZBIERANIE DANYCH Z GUI ---
            experiment_name = exp_name_entry.get().replace(" ", "_")
            if not experiment_name:
                experiment_name = "test"

            population_size = int(population_entry.get())
            generations = int(generations_entry.get())
            dimensions = int(dimensions_entry.get())
            bits_per_variable = int(bits_entry.get())

            crossover_rate = float(crossover_entry.get())
            mutation_rate = float(mutation_entry.get())
            inversion_rate = float(inversion_entry.get())
            elite_size = int(elite_entry.get())

            lower_bound = float(lower_entry.get())
            upper_bound = float(upper_entry.get())
            optimization_type = opt_type_combo.get()

            if lower_bound >= upper_bound:
                raise ValueError("Dolna granica musi być mniejsza od górnej!")

            selection_method = selection_combo.get()
            crossover_method = crossover_combo.get()
            mutation_method = mutation_combo.get()

            # --- URUCHOMIENIE SILNIKA ---
            best_history, avg_history, execution_time = run_genetic_algorithm(
                population_size=population_size,
                generations=generations,
                dimensions=dimensions,
                bits_per_variable=bits_per_variable,
                crossover_rate=crossover_rate,
                mutation_rate=mutation_rate,
                selection_method=selection_method,
                crossover_method=crossover_method,
                mutation_method=mutation_method,
                lower_bound=lower_bound,
                upper_bound=upper_bound,
                optimization_type=optimization_type,
                elite_size=elite_size,
                inversion_rate=inversion_rate
            )

            # --- ZAPIS (CSV + TXT) I WIZUALIZACJA ---
            filename = save_results(
                experiment_name=experiment_name,
                population_size=population_size,
                generations=generations,
                chromosome_length=dimensions * bits_per_variable,
                crossover_rate=crossover_rate,
                mutation_rate=mutation_rate,
                selection_method=selection_method,
                crossover_method=crossover_method,
                mutation_method=mutation_method,
                best_history=best_history,
                avg_history=avg_history,
                execution_time=execution_time,
                optimization_type=optimization_type,
                dimensions=dimensions,
                lower_bound=lower_bound,
                upper_bound=upper_bound,
                elite_size=elite_size,
                inversion_rate=inversion_rate
            )

            fig = create_convergence_figure(best_history, avg_history)

            for widget in plot_frame.winfo_children():
                widget.destroy()

            canvas_plot = FigureCanvasTkAgg(fig, master=plot_frame)
            canvas_plot.draw()
            canvas_plot.get_tk_widget().pack(fill="both", expand=True)

            toolbar = NavigationToolbar2Tk(canvas_plot, plot_frame)
            toolbar.config(background="#FFFFFF")
            for button in toolbar.winfo_children():
                button.config(background="#FFFFFF", borderwidth=0)
            toolbar.update()

            status_label.config(
                text=(
                    f" ✓ Najlepszy wynik: {best_history[-1]:.6f}   |   "
                    f"⏱ Czas: {execution_time:.4f}s   |   "
                    f"💾 Zapisano jako: {filename}"
                )
            )

        except Exception as e:
            messagebox.showerror("Błąd parametrów", f"Wystąpił błąd: {str(e)}")

    # ===== GŁÓWNE OKNO =====
    root = tk.Tk()
    root.title("Algorytm Genetyczny - Panel Badawczy Pro")
    root.geometry("1600x1000")

    # --- PALETA KOLORÓW ---
    BG_COLOR = "#F0F4F9"
    PANEL_BG = "#FFFFFF"
    TEXT_COLOR = "#1E293B"
    ACCENT_COLOR = "#2563EB"
    BORDER_COLOR = "#E2E8F0"

    root.configure(bg=BG_COLOR)

    # Stylizacja TTK
    style = ttk.Style(root)
    style.theme_use('clam')
    style.configure("Bg.TFrame", background=BG_COLOR)
    style.configure("Card.TFrame", background=PANEL_BG)
    style.configure("TLabel", background=PANEL_BG, foreground=TEXT_COLOR, font=("Segoe UI", 10))
    style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground="#0F172A", background=PANEL_BG)
    style.configure("Section.TLabel", font=("Segoe UI", 9, "bold"), foreground="#64748B", background=PANEL_BG)
    style.configure("TEntry", fieldbackground="#F8FAFC", bordercolor=BORDER_COLOR, padding=5)
    style.configure("Action.TButton", font=("Segoe UI", 11, "bold"), background=ACCENT_COLOR, foreground="white",
                    padding=12)
    style.map("Action.TButton", background=[("active", "#1D4ED8")])

    main_container = ttk.Frame(root, style="Bg.TFrame")
    main_container.pack(fill="both", expand=True)

    # ===== LEWA SEKCJA: WYKRES =====
    plot_card = tk.Frame(main_container, bg=PANEL_BG, highlightthickness=1, highlightbackground=BORDER_COLOR)
    plot_card.pack(side="left", fill="both", expand=True, padx=(25, 10), pady=25)
    plot_frame = tk.Frame(plot_card, bg=PANEL_BG)
    plot_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # ===== PRAWA SEKCJA: DYNAMICZNY PANEL PARAMETRÓW =====
    control_card = tk.Frame(main_container, bg=PANEL_BG, highlightthickness=1, highlightbackground=BORDER_COLOR)
    control_card.pack(side="right", fill="y", padx=(10, 25), pady=25)

    canvas = tk.Canvas(control_card, bg=PANEL_BG, highlightthickness=0)
    scrollbar = ttk.Scrollbar(control_card, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas, style="Card.TFrame")

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    def sync_widths(event):
        canvas.itemconfig(canvas_window, width=event.width)

    canvas.bind("<Configure>", sync_widths)

    canvas.configure(yscrollcommand=scrollbar.set)

    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    control_card.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
    control_card.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    # --- TREŚĆ PARAMETRÓW ---
    content_frame = ttk.Frame(scrollable_frame, style="Card.TFrame")
    content_frame.pack(fill="both", expand=True, padx=30, pady=25)

    ttk.Label(content_frame, text="Konfiguracja Eksperymentu", style="Header.TLabel").pack(anchor="w", pady=(0, 20))

    # [NOWE] Pole na nazwę eksperymentu
    ttk.Label(content_frame, text="NAZWA EKSPERYMENTU", style="Section.TLabel").pack(anchor="w")
    exp_name_entry = ttk.Entry(content_frame)
    exp_name_entry.insert(0, "eksperyment_1")
    exp_name_entry.pack(fill="x", pady=(2, 15))

    tk.Frame(content_frame, bg=BORDER_COLOR, height=1).pack(fill="x", pady=5)

    def add_field(parent, label_text, default_value):
        ttk.Label(parent, text=label_text).pack(anchor="w")
        entry = ttk.Entry(parent)
        entry.insert(0, default_value)
        entry.pack(fill="x", pady=(2, 12))
        return entry

    # 1. Rdzeń
    ttk.Label(content_frame, text="STRUKTURA I CZAS", style="Section.TLabel").pack(anchor="w")
    population_entry = add_field(content_frame, "Wielkość populacji", "50")
    generations_entry = add_field(content_frame, "Liczba pokoleń (epok)", "100")
    dimensions_entry = add_field(content_frame, "Liczba zmiennych (Wymiary N)", "5")
    bits_entry = add_field(content_frame, "Bity na zmienną (Dokładność)", "16")

    tk.Frame(content_frame, bg=BORDER_COLOR, height=1).pack(fill="x", pady=10)

    # 2. Operatory
    ttk.Label(content_frame, text="OPERATORY GENETYCZNE", style="Section.TLabel").pack(anchor="w")
    crossover_entry = add_field(content_frame, "Prawdopodobieństwo krzyżowania", "0.8")
    mutation_entry = add_field(content_frame, "Prawdopodobieństwo mutacji", "0.01")
    inversion_entry = add_field(content_frame, "Prawdopodobieństwo inwersji", "0.1")
    elite_entry = add_field(content_frame, "Rozmiar elity (osobniki)", "2")

    tk.Frame(content_frame, bg=BORDER_COLOR, height=1).pack(fill="x", pady=10)

    # 3. Cel
    ttk.Label(content_frame, text="CEL I DZIEDZINA", style="Section.TLabel").pack(anchor="w")

    bounds_f = ttk.Frame(content_frame, style="Card.TFrame")
    bounds_f.pack(fill="x", pady=(2, 10))
    ttk.Label(bounds_f, text="Min x:").pack(side="left")
    lower_entry = ttk.Entry(bounds_f, width=8)
    lower_entry.insert(0, "-5")
    lower_entry.pack(side="left", padx=5)
    ttk.Label(bounds_f, text="Max x:").pack(side="left")
    upper_entry = ttk.Entry(bounds_f, width=8)
    upper_entry.insert(0, "5")
    upper_entry.pack(side="left", padx=5)

    ttk.Label(content_frame, text="Typ optymalizacji").pack(anchor="w")
    opt_type_combo = ttk.Combobox(content_frame, values=["Min", "Max"], state="readonly")
    opt_type_combo.set("Min")
    opt_type_combo.pack(fill="x", pady=(2, 12))

    tk.Frame(content_frame, bg=BORDER_COLOR, height=1).pack(fill="x", pady=10)

    # 4. Metody
    ttk.Label(content_frame, text="Metoda selekcji").pack(anchor="w")
    selection_combo = ttk.Combobox(
        content_frame,
        values=["tournament", "roulette", "best"],
        state="readonly"
    )
    selection_combo.set("tournament")
    selection_combo.pack(fill="x", pady=(2, 10))

    ttk.Label(content_frame, text="Krzyżowanie").pack(anchor="w")
    crossover_combo = ttk.Combobox(
        content_frame,
        values=["one_point", "two_point", "uniform", "grainy"],
        state="readonly"
    )
    crossover_combo.set("one_point")
    crossover_combo.pack(fill="x", pady=(2, 10))

    ttk.Label(content_frame, text="Mutacja").pack(anchor="w")
    mutation_combo = ttk.Combobox(
        content_frame,
        values=["bit_flip", "boundary", "single_point", "two_point"],
        state="readonly"
    )
    mutation_combo.set("bit_flip")
    mutation_combo.pack(fill="x", pady=(2, 20))

    ttk.Button(content_frame, text="START OPTYMALIZACJI 🚀", command=run_algorithm, style="Action.TButton",
               cursor="hand2").pack(fill="x", pady=(5, 10))

    # Pasek statusu
    status_frame = tk.Frame(root, bg="#FFFFFF", highlightthickness=1, highlightbackground=BORDER_COLOR)
    status_frame.pack(side="bottom", fill="x")
    status_label = tk.Label(status_frame, text="  System gotowy do analizy", bg="#FFFFFF", fg="#64748B",
                            font=("Segoe UI", 10), pady=10)
    status_label.pack(side="left", padx=10)

    root.mainloop()


if __name__ == "__main__":
    launch_gui()