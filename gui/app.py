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
        self.view.cross_combo_real.bind("<<ComboboxSelected>>", lambda e: self.view.update_visibility())
        self.view.mut_combo_real.bind("<<ComboboxSelected>>", lambda e: self.view.update_visibility())
        self.view.update_visibility()

    # --- UI EVENTS ---
    def on_tab_change(self, event):
        for widget in self.view.plot_panel.winfo_children():
            widget.destroy()
        self.view.status_label.config(text="Mode changed. Ready for computation.", fg=COLORS["text_muted"])

    def get_and_validate_params(self, tab_index):
        """Validation of the params"""
        try:
            # 1. shared params
            p = {
                'pop': int(self.view.pop_entry.get()),
                'gen': int(self.view.gen_entry.get()),
                'dim': int(self.view.dim_entry.get()),
                'cr': float(self.view.cr_entry.get()),
                'mr': float(self.view.mr_entry.get()),
                'lb': float(self.view.lb_entry.get()),
                'ub': float(self.view.ub_entry.get()),
                'opt': self.view.opt_combo.get(),
                'elite': int(self.view.elite_entry.get()),
                'sel': self.view.selection_combo.get(),
                'exp_name': self.view.exp_name_entry.get()
            }

            # 2. validation of shared params
            if p['pop'] < 2: raise ValueError("Population size must be at least 2.")
            if p['gen'] < 1: raise ValueError("The number of generations must be at least 1.")
            if p['dim'] < 1: raise ValueError("The number of dimensions must be at least 1.")

            if not (0.0 <= p['cr'] <= 1.0):
                raise ValueError("The crossover probability must be in the range [0, 1].")

            if not (0.0 <= p['mr'] <= 1.0):
                raise ValueError("The mutation probability (MR) must be in the range [0, 1].")

            if p['lb'] >= p['ub']:
                raise ValueError("The lower bound (LB) must be less than the upper bound (UB)")

            if p['elite'] < 0 or p['elite'] >= p['pop']:
                raise ValueError("The size of the elite must be >= 0 and smaller than the total population.")

            # 3. hypersphere domain
            if p['lb'] < -5.0 or p['ub'] > 5.0:
                proceed = messagebox.askyesno("Note on Domain",
                                              "The recommended domain for a Hypersphere function is [-5.0, 5.0].\nAre you sure you want to continue?")
                if not proceed:
                    return None

            # 4. binary params
            if tab_index in [0, 2]:
                p['bits'] = int(self.view.bits_entry.get())
                p['inv'] = float(self.view.inv_entry.get())
                p['cross_bin'] = self.view.cross_combo_bin.get()
                p['mut_bin'] = self.view.mut_combo_bin.get()

                if p['bits'] < 1: raise ValueError("The number of bits per variable must be >= 1.")
                if not (0.0 <= p['inv'] <= 1.0):
                    raise ValueError("The inversion probability must be in the range [0, 1].")

            # 5. real params
            if tab_index in [1, 2]:
                p['cross_real'] = self.view.cross_combo_real.get()
                p['mut_real'] = self.view.mut_combo_real.get()

                # safeguard dynamic params
                if "blx" in p['cross_real']:
                    p['alpha'] = float(self.view.alpha_entry.get())
                    if p['alpha'] < 0: raise ValueError("The Alpha (BLX) parameter should be >= 0.")
                else:
                    p['alpha'] = None

                if "blx_alpha_beta" == p['cross_real']:
                    p['beta'] = float(self.view.beta_entry.get())
                    if p['beta'] < 0: raise ValueError("The Beta (BLX) parameter should be >= 0.")
                else:
                    p['beta'] = None

                if p['mut_real'] == "gaussian":
                    p['sigma'] = float(self.view.sigma_entry.get())
                    if p['sigma'] <= 0: raise ValueError("The Sigma (Gauss) parameter should be > 0.")
                else:
                    p['sigma'] = None

            return p

        except ValueError as e:
            # check for errors
            error_msg = str(e)
            if "could not convert" in error_msg or "invalid literal" in error_msg:
                error_msg = "Make sure all fields contain valid numbers and are not empty."
            messagebox.showerror("Value Validation Error", f"Launch aborted.\n\n{error_msg}")
            return None

    def on_run_click(self):
        active_tab = self.view.notebook.index(self.view.notebook.select())

        # 1. Validation and data fetching from GUI in MAIN THREAD
        params = self.get_and_validate_params(active_tab)

        # 2. If validation fails, 'params' is None and we abort.
        if params is None:
            return

        # 3. Change the view and start the thread with the 'params' dictionary frozen
        self.view.start_button.config(state="disabled", text="Evolution in progress... ⏳")
        self.view.progress_bar["value"] = 0
        threading.Thread(target=self.execute_ga, args=(active_tab, params), daemon=True).start()

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
                'best_history': results['best_history'],
                'avg_history': results['avg_history'],
                'execution_time': results['execution_time'],
                'selection_method': params.get('sel'),
                'crossover_method': params.get('cross'),
                'alpha': params.get('alpha'),
                'beta': params.get('beta'),
                'mutation_method': params.get('mut'),
                'sigma': params.get('sigma'),
                'population_size': params.get('pop'),
                'generations': params.get('gen'),
                'dimensions': params.get('dim'),

                # calculate chromosome length for binary mode only
                'chromosome_length': params.get('bits') * params.get('dim') if params.get('bits') and params.get(
                    'dim') else None,

                'crossover_rate': params.get('cr'),
                'mutation_rate': params.get('mr'),
                'lower_bound': params.get('lb'),
                'upper_bound': params.get('ub'),
                'optimization_type': params.get('opt'),
                'elite_size': params.get('elite'),

                # prevents KeyError in Real mode
                'inversion_rate': params.get('inv'),
                'experiment_name': params.get('exp_name')
            }
            sig = inspect.signature(save_results)
            kwargs = {param: pool.get(param, None) for param in sig.parameters.keys()}
            return save_results(**kwargs)
        except Exception as e:
            print(f"Logger Error: {e}")
            import traceback
            traceback.print_exc()
            return f"log_{params.get('exp_name', 'error')}_{ga_type.lower()}.csv"

    # --- MAIN LOOP ---
    def execute_ga(self, tab_index, p):
        try:
            if tab_index == 0:  # BINARY P1
                def cb(c, t):
                    self.root.after(0, lambda: self.update_progress((c / t) * 100))

                raw = run_binary_ga(p['pop'], p['gen'], p['dim'], p['bits'], p['cr'], p['mr'], p['sel'],
                                    p['cross_bin'], p['mut_bin'], p['lb'], p['ub'], p['opt'], p['elite'], p['inv'], cb)
                res = self.parse_results(raw)

                # copy for logger
                p_log = p.copy()
                p_log['cross'] = p['cross_bin']
                p_log['mut'] = p['mut_bin']
                filename = self.smart_logger(res, p_log, "Binary")
                self.root.after(0, lambda: self.finalize_single(res, "Binary (P1)", filename))

            elif tab_index == 1:  # REAL P2
                def cb(c, t):
                    self.root.after(0, lambda: self.update_progress((c / t) * 100))

                raw = run_real_ga(p['pop'], p['gen'], p['dim'], p['cr'], p['mr'], p['sel'],
                                  p['cross_real'], p['mut_real'], p['lb'], p['ub'], p['opt'], p['elite'],
                                  alpha=p['alpha'], beta=p['beta'], sigma=p['sigma'], progress_callback=cb)
                res = self.parse_results(raw)

                p_log = p.copy()
                p_log['cross'] = p['cross_real']
                p_log['mut'] = p['mut_real']
                filename = self.smart_logger(res, p_log, "Real")
                self.root.after(0, lambda: self.finalize_single(res, "Real (P2)", filename))

            elif tab_index == 2:  # COMPARISON
                def cb_b(c, t):
                    self.root.after(0, lambda: self.update_progress((c / t) * 50))

                res_bin = self.parse_results(
                    run_binary_ga(p['pop'], p['gen'], p['dim'], p['bits'], p['cr'], p['mr'],
                                  p['sel'], p['cross_bin'], p['mut_bin'], p['lb'], p['ub'], p['opt'],
                                  p['elite'], p['inv'], cb_b))

                def cb_r(c, t):
                    self.root.after(0, lambda: self.update_progress(50 + (c / t) * 50))

                res_real = self.parse_results(
                    run_real_ga(p['pop'], p['gen'], p['dim'], p['cr'], p['mr'], p['sel'],
                                p['cross_real'], p['mut_real'], p['lb'], p['ub'], p['opt'],
                                p['elite'], alpha=p['alpha'], beta=p['beta'], sigma=p['sigma'], progress_callback=cb_r))

                self.root.after(0, lambda: self.finalize_comparison(res_bin, res_real))

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.root.after(0, lambda: messagebox.showerror("Execution Error", f"A critical error occurred:\n{str(e)}"))
            self.root.after(0, self.reset_ui)

    # --- DRAW CHART ---
    def finalize_single(self, results, ga_type, filename):
        for widget in self.view.plot_panel.winfo_children(): widget.destroy()
        fig = create_convergence_figure(results['best_history'], results['avg_history'])
        canvas = FigureCanvasTkAgg(fig, master=self.view.plot_panel)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        toolbar = NavigationToolbar2Tk(canvas, self.view.plot_panel)
        toolbar.config(background="#FFFFFF")
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
        ax.set_xlabel("Generations")
        ax.set_ylabel("Best Fitness")
        ax.legend()
        ax.grid(True, linestyle=":", alpha=0.7)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.view.plot_panel)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        toolbar = NavigationToolbar2Tk(canvas, self.view.plot_panel)
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
