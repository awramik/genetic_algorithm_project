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
        """Handles logic when the user switches tabs."""
        active_tab = self.view.notebook.index(self.view.notebook.select())

        # 1. Reset progress bar
        self.view.progress_bar["value"] = 0

        # 2. Reset status label
        self.view.status_label.config(text="Ready. Select parameters and run.")

        # 3. CLEAR RESULTS CONSOLE (UX Improvement)
        self.view.results_console.config(state="normal")
        self.view.results_console.delete("1.0", tk.END)
        self.view.results_console.insert("1.0", "Run the evolution to see the results...")
        self.view.results_console.config(state="disabled")

        # 4. Dynamic Matchup Board Update (for Comparison Tab)
        if active_tab == 2:  # Comparison Tab
            self.update_matchup_board()

        # 5. Trigger visibility update for Real/Binary params
        self.view.update_visibility()

    def update_matchup_board(self):
        """Gathers current settings and updates the Matchup Board display."""
        # Gather Binary settings
        b_cross = self.view.cross_combo_bin.get()
        b_mut = self.view.mut_combo_bin.get()
        b_bits = self.view.bits_entry.get()

        # Gather Real settings
        r_cross = self.view.cross_combo_real.get()
        r_mut = self.view.mut_combo_real.get()

        # Build Binary string
        binary_part = f"[01] BINARY ALGORITHM:\n" \
                      f"   Crossover: {b_cross}\n" \
                      f"   Mutation:  {b_mut} ({b_bits} bits)\n\n"

        vs_part = f"            VS\n\n"

        # Build Real string with dynamic params
        real_part = f"[ℝ] REAL ALGORITHM:\n" \
                    f"   Crossover: {r_cross}\n"

        # BLX param
        if "blx" in r_cross:
            alpha = self.view.alpha_entry.get()
            if r_cross == "blx_alpha_beta":
                beta = self.view.beta_entry.get()
                real_part += f"   (α={alpha}, β={beta})\n"
            else:
                real_part += f"   (α={alpha})\n"

        real_part += f"   Mutation:  {r_mut}"
        if r_mut == "gaussian":
            real_part += f" (σ={self.view.sigma_entry.get()})"

        full_text = f"{binary_part}{vs_part}{real_part}"

        # Combine everything
        self.view.matchup_info.config(state="normal")
        self.view.matchup_info.delete("1.0", tk.END)
        self.view.matchup_info.insert("1.0", full_text)
        self.view.matchup_info.config(state="disabled")

    def get_and_validate_params(self, tab_index):
        """Fetches, converts, and validates GUI parameters with error aggregation and highlighting."""

        errors = []
        p = {}

        # --- HELPER FUNCTION FOR VISUAL VALIDATION ---
        def validate_field(entry, field_name, cast_type, min_val=None, max_val=None):
            # 1. Reset background to default
            entry.config(bg=COLORS.get("entry_bg", "white"))
            raw_value = entry.get().strip()

            # 2. Check if field is empty
            if not raw_value:
                errors.append(f"{field_name}: field cannot be empty.")
                entry.config(bg=COLORS.get("error_bg", "#ffcccc"))
                return None

            # 3. Conversion and boundary checks
            try:
                val = cast_type(raw_value)
                if min_val is not None and val < min_val:
                    errors.append(f"{field_name}: value must be at least {min_val}.")
                    entry.config(bg=COLORS.get("error_bg", "#ffcccc"))
                    return None
                if max_val is not None and val > max_val:
                    errors.append(f"{field_name}: value cannot exceed {max_val}.")
                    entry.config(bg=COLORS.get("error_bg", "#ffcccc"))
                    return None
                return val
            except ValueError:
                errors.append(f"{field_name}: invalid format (expected a number).")
                entry.config(bg=COLORS.get("error_bg", "#ffcccc"))
                return None

        # === 1. SHARED PARAMETERS ===
        p['pop'] = validate_field(self.view.pop_entry, "Population size", int, min_val=2)
        p['gen'] = validate_field(self.view.gen_entry, "Generations", int, min_val=1)
        p['dim'] = validate_field(self.view.dim_entry, "Dimensions", int, min_val=1)
        p['cr'] = validate_field(self.view.cr_entry, "Crossover rate (CR)", float, min_val=0.0, max_val=1.0)
        p['mr'] = validate_field(self.view.mr_entry, "Mutation rate (MR)", float, min_val=0.0, max_val=1.0)
        p['lb'] = validate_field(self.view.lb_entry, "Lower bound (LB)", float)
        p['ub'] = validate_field(self.view.ub_entry, "Upper bound (UB)", float)
        p['elite'] = validate_field(self.view.elite_entry, "Elite size", int, min_val=0)

        # Text fields / Dropdowns
        p['opt'] = self.view.opt_combo.get()
        p['sel'] = self.view.selection_combo.get()

        self.view.exp_name_entry.config(bg=COLORS.get("entry_bg", "white"))
        p['exp_name'] = self.view.exp_name_entry.get().strip()
        if not p['exp_name']:
            errors.append("Experiment name: field cannot be empty.")
            self.view.exp_name_entry.config(bg=COLORS.get("error_bg", "#ffcccc"))

        # === DEPENDENCY CHECKS ===
        if p['lb'] is not None and p['ub'] is not None and p['lb'] >= p['ub']:
            errors.append("Bounds: Lower bound must be strictly less than upper bound.")
            self.view.lb_entry.config(bg=COLORS.get("error_bg", "#ffcccc"))
            self.view.ub_entry.config(bg=COLORS.get("error_bg", "#ffcccc"))

        if p['elite'] is not None and p['pop'] is not None and p['elite'] >= p['pop']:
            errors.append("Elite size: must be smaller than total population size.")
            self.view.elite_entry.config(bg=COLORS.get("error_bg", "#ffcccc"))

        # === 2. BINARY ALGORITHM PARAMS (Tabs 0 & 2) ===
        if tab_index in [0, 2]:
            p['bits'] = validate_field(self.view.bits_entry, "Bits per variable", int, min_val=1)
            p['inv'] = validate_field(self.view.inv_entry, "Inversion rate", float, min_val=0.0, max_val=1.0)
            p['cross_bin'] = self.view.cross_combo_bin.get()
            p['mut_bin'] = self.view.mut_combo_bin.get()

        # === 3. REAL ALGORITHM PARAMS (Tabs 1 & 2) ===
        if tab_index in [1, 2]:
            p['cross_real'] = self.view.cross_combo_real.get()
            p['mut_real'] = self.view.mut_combo_real.get()

            if "blx" in p['cross_real']:
                p['alpha'] = validate_field(self.view.alpha_entry, "Alpha (BLX)", float, min_val=0.0)
            else:
                p['alpha'] = None

            if p['cross_real'] == "blx_alpha_beta":
                p['beta'] = validate_field(self.view.beta_entry, "Beta (BLX)", float, min_val=0.0)
            else:
                p['beta'] = None

            if p['mut_real'] == "gaussian":
                p['sigma'] = validate_field(self.view.sigma_entry, "Sigma (Gauss)", float, min_val=0.0001)
            else:
                p['sigma'] = None

        # === 4. FINAL VERIFICATION & ERROR DISPLAY ===
        if errors:
            error_list = "\n".join([f"• {e}" for e in errors])
            messagebox.showerror(
                "Validation Error",
                f"Cannot start the algorithm. Please correct the highlighted fields:\n\n{error_list}"
            )
            return None

        # === DOMAIN WARNING ===
        if p['lb'] < -5.0 or p['ub'] > 5.0:
            proceed = messagebox.askyesno(
                "Domain Warning",
                "The recommended domain for the Hypersphere function is [-5.0, 5.0].\nAre you sure you want to proceed with the current bounds?"
            )
            if not proceed:
                return None

        return p

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
    def parse_results(self, raw):
        """Standardizes results into a dictionary format."""
        if isinstance(raw, dict):
            return raw

        return {
            "best_history": raw[0],
            "avg_history": raw[1],
            "execution_time": raw[2],
            "best_value": raw[0][-1] if raw[0] else 0,
            "best_individual": "No individual data"
        }

    def smart_logger(self, results, params, ga_type):
        try:
            pool = {
                'best_individual': results.get('best_individual'),
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
        try:
            for widget in self.view.plot_panel.winfo_children():
                widget.destroy()
            fig = create_convergence_figure(results['best_history'], results['avg_history'])
            canvas = FigureCanvasTkAgg(fig, master=self.view.plot_panel)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            toolbar = NavigationToolbar2Tk(canvas, self.view.plot_panel)
            toolbar.config(background="#FFFFFF")
            toolbar.update()

            # === RESULTS CONSOLE ===
            self.view.results_console.config(state="normal")
            self.view.results_console.delete("1.0", tk.END)

            best_val = results['best_value']
            chrom = results.get('best_individual', "No chromosome data available")
            time_exec = results['execution_time']

            # difference between first and last gen
            improvement = abs(results['best_history'][0] - best_val)

            # chromosome formatting (4 dec places)
            if isinstance(chrom, list) and len(chrom) > 0 and isinstance(chrom[0], float):
                chrom_str = ", ".join([f"{x:.4f}" for x in chrom])
            else:
                chrom_str = str(chrom)

            msg = f"🏆 Best Value (Fitness): {best_val:.6f}\n"
            msg += f"📉 Total Improvement: {improvement:.6f}\n"
            msg += f"⏱ Execution Time: {time_exec:.3f} s \n"
            msg += f"📁 Logs: {filename}\n"
            msg += f"🧬 Winning Chromosome (Solution):\n[{chrom_str}]\n"

            self.view.results_console.insert(tk.END, msg)
            self.view.results_console.config(state="disabled")

            status_msg = f"✅ {ga_type} Success! Result: {results['best_value']:.6f} | Time: {results['execution_time']:.3f}s | File: {filename}"
            self.view.status_label.config(text=status_msg, fg=COLORS["success"])

        except Exception as e:
            print(f"Error in finalize_single: {e}")
            import traceback
            traceback.print_exc()

        finally:
            # Reset UI
            self.view.start_button.config(state="normal", text="START EVOLUTION")
            self.view.progress_bar["value"] = 100
            self.reset_ui()

            self.root.after(1500, lambda: self.view.progress_bar.configure(value=0))

    def finalize_comparison(self, res_bin, res_real):
        try:
            for widget in self.view.plot_panel.winfo_children():
                widget.destroy()

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

            # === FILLING THE RESULTS CONSOLE FOR COMPARISON ===
            self.view.results_console.config(state="normal")
            self.view.results_console.delete("1.0", tk.END)

            def format_chrom(chrom):
                if chrom is None or isinstance(chrom, str):
                    return str(chrom)
                if isinstance(chrom, list) and len(chrom) > 0 and isinstance(chrom[0], float):
                    return ", ".join([f"{x:.4f}" for x in chrom])
                return str(chrom)

            msg = "💻 BINARY ALGORITHM:\n"
            msg += f"   Value: {res_bin.get('best_value', 0):.6f}  |  Time: {res_bin.get('execution_time', 0):.2f} s\n"
            msg += f"   Chromosome: [{format_chrom(res_bin.get('best_individual', 'No data'))}]\n"

            msg += "📈 REAL-CODED ALGORITHM:\n"
            msg += f"   Value: {res_real.get('best_value', 0):.6f}  |  Time: {res_real.get('execution_time', 0):.2f} s\n"
            msg += f"   Chromosome: [{format_chrom(res_real.get('best_individual', 'No data'))}]\n"

            self.view.results_console.insert(tk.END, msg)
            self.view.results_console.config(state="disabled")

            diff = abs(res_bin.get('best_value', 0) - res_real.get('best_value', 0))
            status_msg = f"✅ Comparison finished! Value difference: {diff:.6f}"
            self.view.status_label.config(text=status_msg, fg=COLORS["success"])

        except Exception as e:
            print(f"Error in finalize_comparison: {e}")
            import traceback
            traceback.print_exc()

        finally:
            # Reset UI
            self.view.start_button.config(state="normal", text="START EVOLUTION")
            self.view.progress_bar["value"] = 100
            self.reset_ui()

            def clear_bar():
                self.view.progress_bar["value"] = 0
                self.view.progress_bar.update_idletasks()

            self.root.after(1500, clear_bar)

    def reset_ui(self):
        self.view.start_button.config(state="normal", text="START EVOLUTION 🧬")
        self.view.progress_bar["value"] = 100


def launch_gui():
    root = tk.Tk()
    app = GeneticAlgorithmController(root)
    root.mainloop()


if __name__ == "__main__":
    launch_gui()
