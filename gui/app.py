import tkinter as tk
from tkinter import ttk, messagebox

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from ga.genetic_algorithm import run_genetic_algorithm
from visualization.plotting import create_convergence_figure
from results.logger import save_results


def launch_gui():
    def run_algorithm():
        try:
            population_size = int(population_entry.get())
            generations = int(generations_entry.get())
            chromosome_length = int(chromosome_entry.get())

            crossover_rate = float(crossover_entry.get())
            mutation_rate = float(mutation_entry.get())

            lower_bound = float(lower_entry.get())
            upper_bound = float(upper_entry.get())

            if lower_bound < -5 or upper_bound > 5 or lower_bound >= upper_bound:
                raise ValueError("Bounds must satisfy: -5 <= lower < upper <= 5")

            selection_method = selection_combo.get()
            crossover_method = crossover_combo.get()
            mutation_method = mutation_combo.get()

            history, execution_time = run_genetic_algorithm(
                population_size=population_size,
                generations=generations,
                chromosome_length=chromosome_length,
                crossover_rate=crossover_rate,
                mutation_rate=mutation_rate,
                selection_method=selection_method,
                crossover_method=crossover_method,
                mutation_method=mutation_method
            )

            filename = save_results(
                population_size=population_size,
                generations=generations,
                chromosome_length=chromosome_length,
                crossover_rate=crossover_rate,
                mutation_rate=mutation_rate,
                selection_method=selection_method,
                crossover_method=crossover_method,
                mutation_method=mutation_method,
                best_value=history[-1],
                execution_time=execution_time
            )

            fig = create_convergence_figure(history)

            for widget in plot_frame.winfo_children():
                widget.destroy()

            canvas = FigureCanvasTkAgg(fig, master=plot_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

            # Modernizacja paska narzędzi matplotlib
            toolbar = NavigationToolbar2Tk(canvas, plot_frame)
            toolbar.config(background="#FFFFFF")
            for button in toolbar.winfo_children():
                button.config(background="#FFFFFF", borderwidth=0)
            toolbar.update()

            status_label.config(
                text=(
                    f" ✓ Najlepsza wartość: {history[-1]:.6f}   |   "
                    f"⏱ Czas: {execution_time:.4f}s   |   "
                    f"💾 Zapisano: {filename}"
                )
            )

        except Exception as e:
            messagebox.showerror("Błąd", str(e))

    # ===== MAIN WINDOW =====
    root = tk.Tk()
    root.title("Algorytm Genetyczny - Panel Optymalizacji")
    root.geometry("1500x950")

    # --- PALETA KOLORÓW ---
    BG_COLOR = "#F0F4F9"
    PANEL_BG = "#FFFFFF"
    TEXT_COLOR = "#1E293B"
    ACCENT_COLOR = "#2563EB"
    HOVER_COLOR = "#1D4ED8"
    BORDER_COLOR = "#E2E8F0"

    root.configure(bg=BG_COLOR)

    # Stylizacja TTK - Flat Design
    style = ttk.Style(root)
    if 'clam' in style.theme_names():
        style.theme_use('clam')

    style.configure("Bg.TFrame", background=BG_COLOR)
    style.configure("Card.TFrame", background=PANEL_BG)
    style.configure("TLabel", background=PANEL_BG, foreground=TEXT_COLOR, font=("Segoe UI", 10))
    style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground="#0F172A", background=PANEL_BG)
    style.configure("Section.TLabel", font=("Segoe UI", 9, "bold"), foreground="#64748B", background=PANEL_BG)

    # Pola tekstowe i listy
    style.configure("TEntry", fieldbackground="#F8FAFC", bordercolor=BORDER_COLOR, lightcolor=BORDER_COLOR,
                    darkcolor=BORDER_COLOR, padding=5)
    style.configure("TCombobox", fieldbackground="#F8FAFC", background="#FFFFFF", bordercolor=BORDER_COLOR,
                    arrowcolor=ACCENT_COLOR)

    # przycisk akcji
    style.configure("Action.TButton", font=("Segoe UI", 11, "bold"), background=ACCENT_COLOR, foreground="white",
                    padding=12, borderwidth=0)
    style.map("Action.TButton", background=[("active", HOVER_COLOR)])

    # Kontener główny
    main_container = ttk.Frame(root, style="Bg.TFrame")
    main_container.pack(fill="both", expand=True)

    # ===== LEWA STRONA: WYKRES =====
    # zamiast czarnych ramek - obrys (highlightbackground)
    plot_card = tk.Frame(main_container, bg=PANEL_BG, highlightthickness=1, highlightbackground=BORDER_COLOR)
    plot_card.pack(side="left", fill="both", expand=True, padx=(25, 10), pady=25)

    plot_frame = tk.Frame(plot_card, bg=PANEL_BG)
    plot_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # ===== PRAWA STRONA: PANEL KONTROLNY =====
    control_card = tk.Frame(main_container, bg=PANEL_BG, highlightthickness=1, highlightbackground=BORDER_COLOR,
                            width=380)
    control_card.pack(side="right", fill="y", padx=(10, 25), pady=25)
    control_card.pack_propagate(False)

    content_frame = ttk.Frame(control_card, style="Card.TFrame")
    content_frame.pack(fill="both", expand=True, padx=30, pady=30)

    # --- Zawartość panelu ---
    ttk.Label(content_frame, text="Parametry Algorytmu", style="Header.TLabel").pack(anchor="w", pady=(0, 25))

    def add_entry(parent, label_text, default_value):
        ttk.Label(parent, text=label_text).pack(anchor="w")
        entry = ttk.Entry(parent)
        entry.insert(0, default_value)
        entry.pack(fill="x", pady=(4, 15))
        return entry

    ttk.Label(content_frame, text="USTAWIENIA GŁÓWNE", style="Section.TLabel").pack(anchor="w")
    population_entry = add_entry(content_frame, "Rozmiar populacji", "50")
    generations_entry = add_entry(content_frame, "Liczba pokoleń", "100")
    chromosome_entry = add_entry(content_frame, "Długość chromosomu", "16")

    # separator
    tk.Frame(content_frame, bg=BORDER_COLOR, height=1).pack(fill="x", pady=10)

    ttk.Label(content_frame, text="PRAWDOPODOBIEŃSTWA", style="Section.TLabel").pack(anchor="w")
    crossover_entry = add_entry(content_frame, "Szansa krzyżowania (0-1)", "0.8")
    mutation_entry = add_entry(content_frame, "Szansa mutacji (0-1)", "0.01")

    tk.Frame(content_frame, bg=BORDER_COLOR, height=1).pack(fill="x", pady=10)

    ttk.Label(content_frame, text="GRANICE I METODY", style="Section.TLabel").pack(anchor="w")

    # Zakresy
    bounds_frame = ttk.Frame(content_frame, style="Card.TFrame")
    bounds_frame.pack(fill="x", pady=(0, 15))

    ttk.Label(bounds_frame, text="Min").pack(side="left")
    lower_entry = ttk.Entry(bounds_frame, width=10)
    lower_entry.insert(0, "-5")
    lower_entry.pack(side="left", padx=(8, 20))

    ttk.Label(bounds_frame, text="Max").pack(side="left")
    upper_entry = ttk.Entry(bounds_frame, width=10)
    upper_entry.insert(0, "5")
    upper_entry.pack(side="left", padx=(8, 0))

    # Comboboxy
    ttk.Label(content_frame, text="Metoda selekcji").pack(anchor="w")
    selection_combo = ttk.Combobox(content_frame, values=["best", "roulette", "tournament"], state="readonly")
    selection_combo.set("tournament")
    selection_combo.pack(fill="x", pady=(4, 15))

    ttk.Label(content_frame, text="Metoda krzyżowania").pack(anchor="w")
    crossover_combo = ttk.Combobox(content_frame, values=["one_point", "two_point", "uniform", "grainy"],
                                   state="readonly")
    crossover_combo.set("one_point")
    crossover_combo.pack(fill="x", pady=(4, 15))

    ttk.Label(content_frame, text="Metoda mutacji").pack(anchor="w")
    mutation_combo = ttk.Combobox(content_frame, values=["bit_flip", "boundary", "single_point", "two_point"],
                                  state="readonly")
    mutation_combo.set("bit_flip")
    mutation_combo.pack(fill="x", pady=(4, 25))

    # Przycisk startu
    ttk.Button(content_frame, text="Uruchom Algorytm 🚀", command=run_algorithm, style="Action.TButton",
               cursor="hand2").pack(fill="x", pady=(10, 0))

    # ===== STATUS BAR =====
    # pasek na samym dole
    status_frame = tk.Frame(root, bg="#FFFFFF", highlightthickness=1, highlightbackground=BORDER_COLOR)
    status_frame.pack(side="bottom", fill="x")

    status_label = tk.Label(status_frame, text="  Gotowy do startu", bg="#FFFFFF", fg="#64748B", font=("Segoe UI", 10), pady=10)
    status_label.pack(side="left", padx=10)

    root.mainloop()


if __name__ == "__main__":
    launch_gui()