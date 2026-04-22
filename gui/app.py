import tkinter as tk
from tkinter import ttk, messagebox
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from ga.genetic_algorithm import run_genetic_algorithm
from visualization.plotting import create_convergence_figure
from results.logger import save_results


def launch_gui():
    # --- LOGIKA WĄTKÓW I CALLBACKÓW ---

    def finalize_ui(best_history, avg_history, execution_time, filename):
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
            text=f" ✅ Sukces! Wynik: {best_history[-1]:.6f}  |  ⏱ Czas: {execution_time:.4f}s  |  💾 Plik: {filename}",
            fg="#059669"
        )
        start_button.config(state="normal", text="START OPTYMALIZACJI 🧬🚀")
        progress_bar.configure(value=0)

    def handle_error(error_msg):
        status_label.config(text=" ❌ Błąd silnika obliczeniowego", fg="#DC2626")
        messagebox.showerror("Błąd krytyczny", f"Wystąpił błąd podczas obliczeń:\n{error_msg}")
        start_button.config(state="normal", text="START OPTYMALIZACJI 🧬🚀")
        progress_bar.configure(value=0)

    def calculation_thread_worker(params):
        try:
            def progress_updater(current, total):
                val = (current / total) * 100
                root.after(0, lambda: progress_bar.configure(value=val))

            best_history, avg_history, execution_time = run_genetic_algorithm(
                population_size=params['population_size'],
                generations=params['generations'],
                dimensions=params['dimensions'],
                bits_per_variable=params['bits_per_variable'],
                crossover_rate=params['crossover_rate'],
                mutation_rate=params['mutation_rate'],
                selection_method=params['selection_method'],
                crossover_method=params['crossover_method'],
                mutation_method=params['mutation_method'],
                lower_bound=params['lower_bound'],
                upper_bound=params['upper_bound'],
                optimization_type=params['optimization_type'],
                elite_size=params['elite_size'],
                inversion_rate=params['inversion_rate'],
                progress_callback=progress_updater
            )

            filename = save_results(
                experiment_name=params['experiment_name'],
                population_size=params['population_size'],
                generations=params['generations'],
                chromosome_length=params['dimensions'] * params['bits_per_variable'],
                crossover_rate=params['crossover_rate'],
                mutation_rate=params['mutation_rate'],
                selection_method=params['selection_method'],
                crossover_method=params['crossover_method'],
                mutation_method=params['mutation_method'],
                best_history=best_history,
                avg_history=avg_history,
                execution_time=execution_time,
                optimization_type=params['optimization_type'],
                dimensions=params['dimensions'],
                lower_bound=params['lower_bound'],
                upper_bound=params['upper_bound'],
                elite_size=params['elite_size'],
                inversion_rate=params['inversion_rate']
            )

            root.after(0, lambda: finalize_ui(best_history, avg_history, execution_time, filename))

        except Exception as e:
            root.after(0, lambda: handle_error(str(e)))

    def run_algorithm():
        try:
            pop_size = int(population_entry.get())
            if pop_size < 2: raise ValueError("Populacja musi mieć min. 2 osobników.")
            gens = int(generations_entry.get())
            dims = int(dimensions_entry.get())
            c_rate = float(crossover_entry.get())
            m_rate = float(mutation_entry.get())
            elite = int(elite_entry.get())
            if elite >= pop_size: raise ValueError("Elita musi być mniejsza od populacji.")

            params = {
                "experiment_name": exp_name_entry.get().replace(" ", "_") or "eksperyment",
                "population_size": pop_size,
                "generations": gens,
                "dimensions": dims,
                "bits_per_variable": int(bits_entry.get()),
                "crossover_rate": c_rate,
                "mutation_rate": m_rate,
                "inversion_rate": float(inversion_entry.get()),
                "elite_size": elite,
                "lower_bound": float(lower_entry.get()),
                "upper_bound": float(upper_entry.get()),
                "optimization_type": opt_type_combo.get(),
                "selection_method": selection_combo.get(),
                "crossover_method": crossover_combo.get(),
                "mutation_method": mutation_combo.get()
            }

            start_button.config(state="disabled", text="🧬 OBLICZENIA W TOKU...")
            status_label.config(text=" ⏳ Trwają obliczenia... Aplikacja pozostaje responsywna.", fg="#1E40AF")

            calc_thread = threading.Thread(target=calculation_thread_worker, args=(params,), daemon=True)
            calc_thread.start()

        except Exception as e:
            messagebox.showerror("Błąd danych", f"Sprawdź parametry:\n{str(e)}")

    # ===== KONSTRUKCJA UI =====
    root = tk.Tk()
    root.title("SGA Pro - Optymalizacja Hypersphere")
    root.geometry("1600x950")

    BG_COLOR, PANEL_BG, BORDER_COLOR = "#F1F5F9", "#FFFFFF", "#E2E8F0"
    TEXT_MAIN, TEXT_MUTED = "#0F172A", "#64748B"
    ACCENT_COLOR, ACCENT_HOVER = "#1E40AF", "#1E3A8A"
    ENTRY_BG, HEADER_BG = "#EFF6FF", "#1E293B"

    root.configure(bg=BG_COLOR)
    style = ttk.Style(root)
    style.theme_use('clam')

    # STYL SCROLLBARA
    style.configure("Vertical.TScrollbar", gripcount=0, background="#CBD5E1",
                    troughcolor=PANEL_BG, bordercolor=PANEL_BG, arrowcolor=PANEL_BG)

    style.configure("TEntry", fieldbackground=ENTRY_BG, foreground=TEXT_MAIN, bordercolor=BORDER_COLOR, padding=6)

    # STYL COMBOBOXÓW
    style.configure("TCombobox", fieldbackground=ENTRY_BG, background=PANEL_BG, bordercolor=BORDER_COLOR,
                    arrowcolor=ACCENT_COLOR, padding=6)
    style.map("TCombobox", fieldbackground=[("readonly", ENTRY_BG)])
    root.option_add("*TCombobox*Listbox.background", PANEL_BG)
    root.option_add("*TCombobox*Listbox.selectBackground", ACCENT_COLOR)

    # STYL PROGRESS BAR
    style.configure("SGA.Horizontal.TProgressbar", troughcolor=BG_COLOR, bordercolor=BORDER_COLOR,
                    background=ACCENT_COLOR, thickness=12)

    # HEADER
    top_header = tk.Frame(root, bg=HEADER_BG, height=65)
    top_header.pack(side="top", fill="x")
    tk.Label(top_header, text="🧬 ALGORYTM GENETYCZNY (SGA) • Optymalizacja Hypersphere",
             bg=HEADER_BG, fg="white", font=("Segoe UI", 14, "bold")).pack(side="left", padx=35, pady=18)

    main_container = tk.Frame(root, bg=BG_COLOR)
    main_container.pack(fill="both", expand=True)

    # WYKRES
    plot_card = tk.Frame(main_container, bg=PANEL_BG, highlightthickness=1, highlightbackground=BORDER_COLOR)
    plot_card.pack(side="left", fill="both", expand=True, padx=(35, 15), pady=35)
    plot_frame = tk.Frame(plot_card, bg=PANEL_BG)
    plot_frame.pack(fill="both", expand=True, padx=25, pady=25)

    # Placeholder
    fig_p, ax_p = plt.subplots(figsize=(8, 5), facecolor=PANEL_BG)
    ax_p.text(0.5, 0.5, 'Skonfiguruj parametry i rozpocznij ewolucję ', ha='center', va='center', color=TEXT_MUTED,
              fontweight='bold', fontsize=13)
    ax_p.axis('off')
    canvas_p = FigureCanvasTkAgg(fig_p, master=plot_frame)
    canvas_p.draw()
    canvas_p.get_tk_widget().pack(fill="both", expand=True)

    # PANEL STEROWANIA
    control_card = tk.Frame(main_container, bg=PANEL_BG, highlightthickness=1, highlightbackground=BORDER_COLOR)
    control_card.pack(side="right", fill="y", padx=(15, 35), pady=35)

    canvas = tk.Canvas(control_card, bg=PANEL_BG, highlightthickness=0, width=380)
    scrollbar = ttk.Scrollbar(control_card, orient="vertical", command=canvas.yview, style="Vertical.TScrollbar")
    scrollable_frame = tk.Frame(canvas, bg=PANEL_BG)

    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=380)
    canvas.configure(yscrollcommand=scrollbar.set)

    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    # Formularz
    def add_input(parent, label, default, is_section=False):
        if is_section:
            tk.Label(parent, text=label, bg=PANEL_BG, fg=ACCENT_COLOR, font=("Segoe UI", 9, "bold")).pack(anchor="w",
                                                                                                          pady=(15, 5))
        else:
            tk.Label(parent, text=label, bg=PANEL_BG, fg=TEXT_MAIN, font=("Segoe UI", 10)).pack(anchor="w")
        entry = ttk.Entry(parent);
        entry.insert(0, default);
        entry.pack(fill="x", pady=(0, 12))
        return entry

    cont = tk.Frame(scrollable_frame, bg=PANEL_BG)
    cont.pack(fill="both", expand=True, padx=30, pady=20)

    tk.Label(cont, text="⚙️ Konfiguracja Parametrów ", bg=PANEL_BG, fg=ACCENT_COLOR, font=("Segoe UI", 16, "bold")).pack(
        anchor="w", pady=(0, 20))

    exp_name_entry = add_input(cont, "NAZWA EKSPERYMENTU", "eksperyment_1", True)
    population_entry = add_input(cont, "POPULACJA", "50", True)
    generations_entry = add_input(cont, "Liczba pokoleń", "100")
    dimensions_entry = add_input(cont, "Wymiary N", "5")
    bits_entry = add_input(cont, "Bity (Precyzja)", "16")
    crossover_entry = add_input(cont, "OPERATORY", "0.8", True)
    mutation_entry = add_input(cont, "Prawd. mutacji", "0.01")
    inversion_entry = add_input(cont, "Prawd. inwersji", "0.1")
    elite_entry = add_input(cont, "Rozmiar elity", "2")

    tk.Label(cont, text="CEL I ZAKRES", bg=PANEL_BG, fg=ACCENT_COLOR, font=("Segoe UI", 9, "bold")).pack(anchor="w",
                                                                                                         pady=(15, 5))
    rf = tk.Frame(cont, bg=PANEL_BG);
    rf.pack(fill="x")
    lower_entry = ttk.Entry(rf, width=10);
    lower_entry.insert(0, "-5");
    lower_entry.pack(side="left")
    tk.Label(rf, text=" do ", bg=PANEL_BG).pack(side="left")
    upper_entry = ttk.Entry(rf, width=10);
    upper_entry.insert(0, "5");
    upper_entry.pack(side="left")

    opt_type_combo = ttk.Combobox(cont, values=["Min", "Max"], state="readonly")
    opt_type_combo.set("Min");
    opt_type_combo.pack(fill="x", pady=(10, 15))

    tk.Label(cont, text="METODYKA", bg=PANEL_BG, fg=ACCENT_COLOR, font=("Segoe UI", 9, "bold")).pack(anchor="w",
                                                                                                     pady=(15, 5))
    selection_combo = ttk.Combobox(cont, values=["tournament", "roulette", "best"], state="readonly")
    selection_combo.set("tournament");
    selection_combo.pack(fill="x", pady=5)
    crossover_combo = ttk.Combobox(cont, values=["one_point", "two_point", "uniform", "grainy"], state="readonly")
    crossover_combo.set("one_point");
    crossover_combo.pack(fill="x", pady=5)
    mutation_combo = ttk.Combobox(cont, values=["bit_flip", "boundary", "single_point", "two_point"], state="readonly")
    mutation_combo.set("bit_flip");
    mutation_combo.pack(fill="x", pady=(5, 25))

    start_button = tk.Button(cont, text="START OPTYMALIZACJI 🧬🚀", command=run_algorithm,
                             bg=ACCENT_COLOR, fg="white", font=("Segoe UI", 11, "bold"), pady=15, bd=0, cursor="hand2")
    start_button.pack(fill="x", pady=(0, 20))

    progress_bar = ttk.Progressbar(cont, style="SGA.Horizontal.TProgressbar", mode="determinate")
    progress_bar.pack(fill="x", pady=(5, 10))

    # STATUS BAR
    status_frame = tk.Frame(root, bg=PANEL_BG, highlightthickness=1, highlightbackground=BORDER_COLOR)
    status_frame.pack(side="bottom", fill="x")
    status_label = tk.Label(status_frame, text=" 🟢 System gotowy do pracy", bg=PANEL_BG, fg=TEXT_MUTED,
                            font=("Segoe UI", 10), pady=12)
    status_label.pack(side="left", padx=10)

    root.mainloop()


if __name__ == "__main__": launch_gui()