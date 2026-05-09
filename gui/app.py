import tkinter as tk
from tkinter import messagebox
import threading
import traceback
import inspect
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from gui.styles import COLORS, configure_styles
from gui.view import MainView

from ga_binary.genetic_algorithm import run_genetic_algorithm as run_binary_ga
from ga_real.genetic_algorithm import run_genetic_algorithm as run_real_ga
from visualization.plotting import create_convergence_figure
from results.logger import save_results


class GeneticAlgorithmController:
    def __init__(self, root):
        self.root = root
        self.root.title("Genetic Algorithm")
        self.root.geometry("1400x900")
        self.root.configure(bg=COLORS["bg_main"])

        configure_styles()

        # 1. VIEW
        self.view = MainView(self.root)

        # 2. LOGIC
        self.view.start_button.config(command=self.on_run_click)
        self.view.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

    # --- UI EVENTS ---
    def on_tab_change(self, event):
        for widget in self.view.plot_panel.winfo_children():
            widget.destroy()
        self.view.status_label.config(text="Mode changed. Ready for computation.", fg=COLORS["text_muted"])

    def on_run_click(self):
        try:
            lb = float(self.view.lb_entry.get())
            ub = float(self.view.ub_entry.get())
            if lb < -5.0 or ub > 5.0:
                proceed = messagebox.askyesno("Domain Warning",
                                              "The standard domain for Hypersphere is [-5.0, 5.0]. Continue?")
                if not proceed: return
        except ValueError:
            messagebox.showerror("Input Error", "Lower and Upper bounds must be numerical.")
            return

        active_tab = self.view.notebook.index(self.view.notebook.select())
        self.view.start_button.config(state="disabled", text="Evolution in progress... ⏳")
        self.view.progress_bar["value"] = 0
        threading.Thread(target=self.execute_ga, args=(active_tab,), daemon=True).start()

    def update_progress(self, val):
        self.view.progress_bar["value"] = val

    # --- HELPERS ---
    def parse_results(self, raw_data):
        if isinstance(raw_data, dict):
            return {'best_history': raw_data['best_history'], 'avg_history': raw_data['avg_history'],
                    'execution_time': raw_data['execution_time'], 'best_value': raw_data.get('best_value',
                                                                                             raw_data['best_history'][
                                                                                                 -1] if raw_data[
                                                                                                 'best_history'] else 0)}
        elif isinstance(raw_data, tuple):
            return {'best_history': raw_data[0], 'avg_history': raw_data[1], 'execution_time': raw_data[2],
                    'best_value': raw_data[0][-1] if raw_data[0] else 0}
        return raw_data

    def smart_logger(self, results, params, ga_type):
        try:
            pool = {
                'best_history': results['best_history'], 'avg_history': results['avg_history'],
                'execution_time': results['execution_time'],
                'selection_method': params['sel'], 'crossover_method': params['cross'],
                'mutation_method': params['mut'],
                'population_size': params['pop'], 'generations': params['gen'], 'dimensions': params['dim'],
                'bits': params['bits'],
                'bits_per_variable': params['bits'], 'crossover_rate': params['cr'], 'mutation_rate': params['mr'],
                'lower_bound': params['lb'], 'upper_bound': params['ub'], 'optimization_type': params['opt'],
                'elite_size': params['elite'], 'inversion_rate': params['inv'], 'experiment_name': params['exp_name']
            }
            sig = inspect.signature(save_results)
            kwargs = {param: pool.get(param, None) for param in sig.parameters.keys()}
            return save_results(**kwargs)
        except Exception as e:
            print(f"Logger Error: {e}")
            return f"log_{params['exp_name']}_{ga_type.lower()}.csv"

    # --- MAIN LOOP ---
    def execute_ga(self, tab_index):
        try:
            p = {
                'pop': int(self.view.pop_entry.get()), 'gen': int(self.view.gen_entry.get()),
                'dim': int(self.view.dim_entry.get()),
                'cr': float(self.view.cr_entry.get()), 'mr': float(self.view.mr_entry.get()),
                'lb': float(self.view.lb_entry.get()),
                'ub': float(self.view.ub_entry.get()), 'opt': self.view.opt_combo.get(),
                'elite': int(self.view.elite_entry.get()),
                'sel': self.view.selection_combo.get(), 'bits': int(self.view.bits_entry.get()),
                'inv': float(self.view.inv_entry.get()),
                'exp_name': self.view.exp_name_entry.get()
            }

            if tab_index == 0:  # BINARY P1
                p['cross'] = self.view.cross_combo_bin.get();
                p['mut'] = self.view.mut_combo_bin.get()

                def cb(c, t):
                    self.root.after(0, lambda: self.update_progress((c / t) * 100))

                raw = run_binary_ga(p['pop'], p['gen'], p['dim'], p['bits'], p['cr'], p['mr'], p['sel'], p['cross'],
                                    p['mut'], p['lb'], p['ub'], p['opt'], p['elite'], p['inv'], cb)
                res = self.parse_results(raw)
                filename = self.smart_logger(res, p, "Binary")
                self.root.after(0, lambda: self.finalize_single(res, "Binary (P1)", filename))

            elif tab_index == 1:  # REAL P2
                p['cross'] = self.view.cross_combo_real.get();
                p['mut'] = self.view.mut_combo_real.get()

                def cb(c, t):
                    self.root.after(0, lambda: self.update_progress((c / t) * 100))

                raw = run_real_ga(p['pop'], p['gen'], p['dim'], p['cr'], p['mr'], p['sel'], p['cross'], p['mut'],
                                  p['lb'], p['ub'], p['opt'], p['elite'], cb)
                res = self.parse_results(raw)
                filename = self.smart_logger(res, p, "Real")
                self.root.after(0, lambda: self.finalize_single(res, "Real (P2)", filename))

            elif tab_index == 2:  # COMPARISON
                p_bin = p.copy();
                p_bin['cross'] = self.view.cross_combo_bin.get();
                p_bin['mut'] = self.view.mut_combo_bin.get()

                def cb_b(c, t):
                    self.root.after(0, lambda: self.update_progress((c / t) * 50))

                res_bin = self.parse_results(
                    run_binary_ga(p_bin['pop'], p_bin['gen'], p_bin['dim'], p_bin['bits'], p_bin['cr'], p_bin['mr'],
                                  p_bin['sel'], p_bin['cross'], p_bin['mut'], p_bin['lb'], p_bin['ub'], p_bin['opt'],
                                  p_bin['elite'], p_bin['inv'], cb_b))

                p_real = p.copy();
                p_real['cross'] = self.view.cross_combo_real.get();
                p_real['mut'] = self.view.mut_combo_real.get()

                def cb_r(c, t):
                    self.root.after(0, lambda: self.update_progress(50 + (c / t) * 50))

                res_real = self.parse_results(
                    run_real_ga(p_real['pop'], p_real['gen'], p_real['dim'], p_real['cr'], p_real['mr'], p_real['sel'],
                                p_real['cross'], p_real['mut'], p_real['lb'], p_real['ub'], p_real['opt'],
                                p_real['elite'], cb_r))
                self.root.after(0, lambda: self.finalize_comparison(res_bin, res_real))

        except Exception as e:
            traceback.print_exc()
            self.root.after(0, lambda: messagebox.showerror("Execution Error", f"A critical error occurred:\n{str(e)}"))
            self.root.after(0, self.reset_ui)

    # --- RYSOWANIE I ZAKOŃCZENIE ---
    def finalize_single(self, results, ga_type, filename):
        for widget in self.view.plot_panel.winfo_children(): widget.destroy()
        fig = create_convergence_figure(results['best_history'], results['avg_history'])
        canvas = FigureCanvasTkAgg(fig, master=self.view.plot_panel);
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        toolbar = NavigationToolbar2Tk(canvas, self.view.plot_panel)
        toolbar.config(background="#FFFFFF");
        toolbar.update()

        msg = f"✅ {ga_type} Success! Result: {results['best_value']:.6f} | Time: {results['execution_time']:.3f}s | File: {filename}"
        self.view.status_label.config(text=msg, fg=COLORS["success"])
        self.reset_ui()

    def finalize_comparison(self, res_bin, res_real):
        self.view.bin_time_label.config(text=f"Binary Time: {res_bin['execution_time']:.4f} s")
        self.view.real_time_label.config(text=f"Real Time: {res_real['execution_time']:.4f} s")
        for widget in self.view.plot_panel.winfo_children(): widget.destroy()

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.plot(res_bin['best_history'], label="Binary Encoding (P1)", color="red", linewidth=2)
        ax.plot(res_real['best_history'], label="Real Encoding (P2)", color="blue", linewidth=2, linestyle="--")
        ax.set_title("Convergence Comparison: Binary vs Real", fontsize=12, fontweight='bold')
        ax.set_xlabel("Generations");
        ax.set_ylabel("Best Fitness")
        ax.legend();
        ax.grid(True, linestyle=":", alpha=0.7);
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.view.plot_panel);
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        toolbar = NavigationToolbar2Tk(canvas, self.view.plot_panel);
        toolbar.update()

        msg = f"✅ Comparison finished! Value difference: {abs(res_bin['best_value'] - res_real['best_value']):.6f}"
        self.view.status_label.config(text=msg, fg=COLORS["success"])
        self.reset_ui()

    def reset_ui(self):
        self.view.start_button.config(state="normal", text="START EVOLUTION 🧬")
        self.view.progress_bar["value"] = 100


def launch_gui():
    root = tk.Tk()
    app = GeneticAlgorithmController(root)
    root.mainloop()


if __name__ == "__main__":
    launch_gui()
