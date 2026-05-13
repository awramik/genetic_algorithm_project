import os
import customtkinter as ctk
from tkinter import messagebox
import threading
import inspect
import platform
import subprocess
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from gui.view import MainView
from ga_binary.genetic_algorithm import run_genetic_algorithm as run_binary_ga
from ga_real.genetic_algorithm import run_genetic_algorithm as run_real_ga
from visualization.plotting import create_convergence_figure
from results.logger import save_results

PARAM_MAP = {
    "One-Point": "one_point", "Two-Point": "two_point", "Uniform": "uniform", "Grainy": "grainy",
    "Bit-Flip": "bit_flip", "Boundary": "boundary", "Single-Point": "single_point",
    "Arithmetic": "arithmetic", "Linear": "linear", "BLX-α": "blx_alpha", "BLX-α-β": "blx_alpha_beta", "Averaging": "averaging",
    "Gaussian": "gaussian", "Best": "best", "Roulette": "roulette", "Tournament": "tournament"
}

class GeneticAlgorithmController:
    def __init__(self, root):
        self.root = root
        self.root.title("Genetic Algorithm Dashboard")
        self.root.geometry("1500x1000")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # 1. VIEW
        self.view = MainView(self.root)

        # 2. LOGIC
        self.view.start_button.configure(command=self.on_run_click)
        self.view.notebook.configure(command=self.on_tab_change)
        self.view.open_logs_btn.configure(command=self.open_logs_folder)
        self.view.update_visibility()

    def open_logs_folder(self):
        """Opens logs folder"""
        path = os.path.abspath("results/logs")
        if not os.path.exists(path):
            os.makedirs(path)

        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":  # macOS
            subprocess.Popen(["open", path])
        else:  # Linux
            subprocess.Popen(["xdg-open", path])

    def on_tab_change(self):
        """Handles logic when the user switches tabs."""
        tab_name = self.view.notebook.get()
        tab_mapping = {"Binary (P1)": 0, "Real (P2)": 1, "Comparison": 2}
        active_tab = tab_mapping.get(tab_name, 0)

        # 1. Reset progress bar
        self.view.progress_bar.set(0)

        # 2. Reset status label
        self.view.status_label.configure(text="Ready. Select parameters and run.")

        # 3. CLEAR RESULTS CONSOLE
        self.view.results_console.configure(state="normal")
        self.view.results_console.delete("1.0", "end")
        self.view.results_console.insert("1.0", "Run the evolution to see the results...")
        self.view.results_console.configure(state="disabled")

        # 4. Matchup Board
        if active_tab == 2:
            self.update_matchup_board()

        self.view.update_visibility()

    def update_matchup_board(self):
        b_cross = self.view.cross_combo_bin.get()
        b_mut = self.view.mut_combo_bin.get()
        b_bits = self.view.bits_entry.get()

        r_cross = self.view.cross_combo_real.get()
        r_mut = self.view.mut_combo_real.get()

        # bin card
        bin_text = f"• Crossover: {b_cross}\n• Mutation:  {b_mut} ({b_bits} bits)"
        self.view.bin_stats.configure(text=bin_text)

        # real card
        real_text = f"• Crossover: {r_cross}"
        if "BLX" in r_cross:
            alpha = self.view.alpha_entry.get()
            if r_cross == "BLX-α-β":
                beta = self.view.beta_entry.get()
                real_text += f" (α={alpha}, β={beta})"
            else:
                real_text += f" (α={alpha})"

        real_text += f"\n• Mutation:  {r_mut}"
        if r_mut == "Gaussian":
            real_text += f" (σ={self.view.sigma_entry.get()})"

        self.view.real_stats.configure(text=real_text)

    def set_ui_state(self, state):
        entries = [
            self.view.pop_entry, self.view.gen_entry, self.view.dim_entry,
            self.view.cr_entry, self.view.mr_entry, self.view.lb_entry,
            self.view.ub_entry, self.view.elite_entry, self.view.exp_name_entry,
            self.view.bits_entry, self.view.inv_entry, self.view.alpha_entry,
            self.view.beta_entry, self.view.sigma_entry
        ]
        for entry in entries:
            entry.configure(state=state)

        combos = [
            self.view.opt_combo, self.view.selection_combo,
            self.view.cross_combo_bin, self.view.mut_combo_bin,
            self.view.cross_combo_real, self.view.mut_combo_real
        ]
        for combo in combos:
            combo.configure(state=state)

        if state == "disabled":
            self.root.config(cursor="watch")
        else:
            self.root.config(cursor="")

    def get_and_validate_params(self, tab_index):
        errors = []
        p = {}

        def validate_field(entry, field_name, cast_type, min_val=None, max_val=None):
            entry.configure(border_color=["#979DA2", "#565B5E"])
            raw_value = entry.get().strip()

            if not raw_value:
                errors.append(f"{field_name}: field cannot be empty.")
                entry.configure(border_color="red")
                return None

            try:
                val = cast_type(raw_value)
                if min_val is not None and val < min_val:
                    errors.append(f"{field_name}: value must be at least {min_val}.")
                    entry.configure(border_color="red")
                    return None
                if max_val is not None and val > max_val:
                    errors.append(f"{field_name}: value cannot exceed {max_val}.")
                    entry.configure(border_color="red")
                    return None
                return val
            except ValueError:
                errors.append(f"{field_name}: invalid format (expected a number).")
                entry.configure(border_color="red")
                return None

        p['pop'] = validate_field(self.view.pop_entry, "Population size", int, min_val=2)
        p['gen'] = validate_field(self.view.gen_entry, "Generations", int, min_val=1)
        p['dim'] = validate_field(self.view.dim_entry, "Dimensions", int, min_val=1)
        p['cr'] = validate_field(self.view.cr_entry, "Crossover rate (CR)", float, min_val=0.0, max_val=1.0)
        p['mr'] = validate_field(self.view.mr_entry, "Mutation rate (MR)", float, min_val=0.0, max_val=1.0)
        p['lb'] = validate_field(self.view.lb_entry, "Lower bound (LB)", float)
        p['ub'] = validate_field(self.view.ub_entry, "Upper bound (UB)", float)
        p['elite'] = validate_field(self.view.elite_entry, "Elite size", int, min_val=0)

        p['opt'] = self.view.opt_combo.get()
        p['sel'] = PARAM_MAP[self.view.selection_combo.get()]

        self.view.exp_name_entry.configure(border_color=["#979DA2", "#565B5E"])
        p['exp_name'] = self.view.exp_name_entry.get().strip()
        if not p['exp_name']:
            errors.append("Experiment name: field cannot be empty.")
            self.view.exp_name_entry.configure(border_color="red")

        if p['lb'] is not None and p['ub'] is not None and p['lb'] >= p['ub']:
            errors.append("Bounds: Lower bound must be strictly less than upper bound.")
            self.view.lb_entry.configure(border_color="red")
            self.view.ub_entry.configure(border_color="red")

        if p['elite'] is not None and p['pop'] is not None and p['elite'] >= p['pop']:
            errors.append("Elite size: must be smaller than total population size.")
            self.view.elite_entry.configure(border_color="red")

        if tab_index in [0, 2]:
            p['bits'] = validate_field(self.view.bits_entry, "Bits per variable", int, min_val=1)
            p['inv'] = validate_field(self.view.inv_entry, "Inversion rate", float, min_val=0.0, max_val=1.0)
            p['cross_bin'] = PARAM_MAP[self.view.cross_combo_bin.get()]
            p['mut_bin'] = PARAM_MAP[self.view.mut_combo_bin.get()]

            if p['bits'] is not None and p['dim'] is not None:
                chrom_len = p['bits'] * p['dim']
                if p['cross_bin'] == "two_point" and chrom_len < 3:
                    errors.append("Two-Point Crossover: requires total chromosome length >= 3.")
                    self.view.bits_entry.configure(border_color="red")

        if tab_index in [1, 2]:
            p['cross_real'] = PARAM_MAP[self.view.cross_combo_real.get()]
            p['mut_real'] = PARAM_MAP[self.view.mut_combo_real.get()]

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

        if errors:
            error_list = "\n".join([f"• {e}" for e in errors])
            messagebox.showerror("Validation Error", f"Cannot start the algorithm. Please correct:\n\n{error_list}")
            return None

        if p['lb'] < -5.0 or p['ub'] > 5.0:
            proceed = messagebox.askyesno("Domain Warning", "The recommended domain is [-5.0, 5.0]. Proceed?")
            if not proceed:
                return None

        return p

    def on_run_click(self):
        tab_name = self.view.notebook.get()
        active_tab = {"Binary (P1)": 0, "Real (P2)": 1, "Comparison": 2}.get(tab_name, 0)

        params = self.get_and_validate_params(active_tab)
        if params is None:
            return

        self.set_ui_state("disabled")
        self.view.start_button.configure(state="disabled", text="Evolution in progress... ⏳")
        self.view.progress_bar.set(0)
        threading.Thread(target=self.execute_ga, args=(active_tab, params), daemon=True).start()

    def update_progress(self, val):
        self.view.progress_bar.set(val / 100.0)

    def parse_results(self, raw):
        if isinstance(raw, dict):
            return raw
        return {"best_history": raw[0], "avg_history": raw[1], "execution_time": raw[2], "best_value": raw[0][-1] if raw[0] else 0, "best_individual": "No individual data"}

    def smart_logger(self, results, params, ga_type):
        try:
            pool = {
                'ga_type': ga_type, 'std_history': results.get('std_history', []), 'best_individual': results.get('best_individual'), 'best_history': results['best_history'],
                'avg_history': results['avg_history'], 'execution_time': results['execution_time'], 'selection_method': params.get('sel'),
                'crossover_method': params.get('cross'), 'alpha': params.get('alpha'), 'beta': params.get('beta'), 'mutation_method': params.get('mut'),
                'sigma': params.get('sigma'), 'population_size': params.get('pop'), 'generations': params.get('gen'), 'dimensions': params.get('dim'),
                'chromosome_length': params.get('bits') * params.get('dim') if params.get('bits') and params.get('dim') else None,
                'crossover_rate': params.get('cr'), 'mutation_rate': params.get('mr'), 'lower_bound': params.get('lb'),
                'upper_bound': params.get('ub'), 'optimization_type': params.get('opt'), 'elite_size': params.get('elite'),
                'inversion_rate': params.get('inv'), 'experiment_name': params.get('exp_name')
            }
            sig = inspect.signature(save_results)
            kwargs = {param: pool.get(param, None) for param in sig.parameters.keys()}
            return save_results(**kwargs)
        except Exception as e:
            print(f"Logger Error: {e}")
            return f"log_{params.get('exp_name', 'error')}_{ga_type.lower()}.csv"

    def execute_ga(self, tab_index, p):
        try:
            last_val = [-1]
            if tab_index == 0:
                def cb(c, t):
                    val = int((c / t) * 100)
                    if val > last_val[0]:
                        last_val[0] = val
                        self.root.after(0, lambda v=val: self.update_progress(v))
                raw = run_binary_ga(p['pop'], p['gen'], p['dim'], p['bits'], p['cr'], p['mr'], p['sel'], p['cross_bin'], p['mut_bin'], p['lb'], p['ub'], p['opt'], p['elite'], p['inv'], cb)
                res = self.parse_results(raw)
                p_log = p.copy(); p_log['cross'] = p['cross_bin']; p_log['mut'] = p['mut_bin']
                filename = self.smart_logger(res, p_log, "Binary")
                self.root.after(0, lambda: self.finalize_single(res, "Binary (P1)", filename))

            elif tab_index == 1:
                def cb(c, t):
                    val = int((c / t) * 100)
                    if val > last_val[0]:
                        last_val[0] = val
                        self.root.after(0, lambda v=val: self.update_progress(v))
                raw = run_real_ga(p['pop'], p['gen'], p['dim'], p['cr'], p['mr'], p['sel'], p['cross_real'], p['mut_real'], p['lb'], p['ub'], p['opt'], p['elite'], alpha=p['alpha'], beta=p['beta'], sigma=p['sigma'], progress_callback=cb)
                res = self.parse_results(raw)
                p_log = p.copy(); p_log['cross'] = p['cross_real']; p_log['mut'] = p['mut_real']
                filename = self.smart_logger(res, p_log, "Real")
                self.root.after(0, lambda: self.finalize_single(res, "Real (P2)", filename))

            elif tab_index == 2:
                def cb_b(c, t):
                    val = int((c / t) * 50)
                    if val > last_val[0]:
                        last_val[0] = val
                        self.root.after(0, lambda v=val: self.update_progress(v))
                res_bin = self.parse_results(run_binary_ga(p['pop'], p['gen'], p['dim'], p['bits'], p['cr'], p['mr'], p['sel'], p['cross_bin'], p['mut_bin'], p['lb'], p['ub'], p['opt'], p['elite'], p['inv'], cb_b))

                def cb_r(c, t):
                    val = int(50 + (c / t) * 50)
                    if val > last_val[0]:
                        last_val[0] = val
                        self.root.after(0, lambda v=val: self.update_progress(v))
                res_real = self.parse_results(run_real_ga(p['pop'], p['gen'], p['dim'], p['cr'], p['mr'], p['sel'], p['cross_real'], p['mut_real'], p['lb'], p['ub'], p['opt'], p['elite'], alpha=p['alpha'], beta=p['beta'], sigma=p['sigma'], progress_callback=cb_r))
                self.root.after(0, lambda: self.finalize_comparison(res_bin, res_real))

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.root.after(0, lambda: messagebox.showerror("Execution Error", f"A critical error occurred:\n{str(e)}"))
            self.root.after(0, self.reset_ui)

    def finalize_single(self, results, ga_type, filename):
        try:
            plt.close('all')
            for widget in self.view.plot_panel.winfo_children(): widget.destroy()
            fig = create_convergence_figure(results['best_history'], results['avg_history'])
            canvas = FigureCanvasTkAgg(fig, master=self.view.plot_panel)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

            toolbar = NavigationToolbar2Tk(canvas, self.view.plot_panel)
            toolbar.config(background="#E8EFEA", bd=0)
            toolbar.update()

            self.view.results_console.configure(state="normal")
            self.view.results_console.delete("1.0", "end")

            best_val = results['best_value']
            chrom = results.get('best_individual', "---")
            chrom_str = ", ".join([f"{x:.4f}" for x in chrom]) if isinstance(chrom, list) else str(chrom)

            msg = f"🏆 Best Value (Fitness): {best_val:.8f}\n"
            msg += f"🕒 Execution Time: {results['execution_time']:.3f} s\n"
            msg += f"📁 Logs: {filename}\n"
            msg += f"🧬 Winning Chromosome:\n[{chrom_str}]\n"

            self.view.results_console.insert("end", msg)
            self.view.results_console.configure(state="disabled")

            status_msg = f"✅ {ga_type} Success! Best value: {results['best_value']:.6f}"
            self.view.status_label.configure(text=status_msg, text_color="green")

        except Exception as e:
            print(f"Error in finalize_single: {e}")
        finally:
            self.view.start_button.configure(state="normal", text="START EVOLUTION")
            self.view.progress_bar.set(1.0)
            self.reset_ui()
            self.root.after(1500, lambda: self.view.progress_bar.set(0))

    def finalize_comparison(self, res_bin, res_real):
        try:
            plt.close('all')
            for widget in self.view.plot_panel.winfo_children(): widget.destroy()

            fig, ax = plt.subplots(figsize=(6, 4), facecolor='#E8EFEA')
            ax.set_facecolor('#E8EFEA')
            ax.plot(res_bin['best_history'], label="Binary Encoding (P1)", color="#1E3628", linewidth=2.5)
            ax.plot(res_real['best_history'], label="Real Encoding (P2)", color="#A65D37", linewidth=2.5, linestyle="--")
            ax.set_title("Convergence Comparison", fontsize=14, fontweight='bold', color="#1A2421", pad=15)
            ax.set_xlabel("Epoch (Generation)", fontsize=11, color="#2C3E35")
            ax.set_ylabel("Funcion value", fontsize=11, color="#2C3E35")
            ax.grid(True, linestyle=":", alpha=0.8, color="#B5C7BC")
            ax.legend()
            fig.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=self.view.plot_panel)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

            toolbar = NavigationToolbar2Tk(canvas, self.view.plot_panel)
            toolbar.config(background="#E8EFEA", bd=0)
            toolbar.update()

            self.view.results_console.configure(state="normal")
            self.view.results_console.delete("1.0", "end")

            def format_chrom(chrom):
                if isinstance(chrom, list) and len(chrom) > 0 and isinstance(chrom[0], float):
                    return ", ".join([f"{x:.4f}" for x in chrom])
                return str(chrom)

            msg = f"💻 BINARY ALGORITHM:\n"
            msg += f"🏆 Best Value (Fitness): {res_bin.get('best_value', 0):.8f}\n"
            msg += f"🕒 Execution Time: {res_bin.get('execution_time', 0):.3f} s\n"
            msg += f"🧬 Winning Chromosome:\n[{format_chrom(res_bin.get('best_individual', 'No data'))}]\n\n"

            msg += f"📈 REAL-CODED ALGORITHM:\n"
            msg += f"🏆 Best Value (Fitness): {res_real.get('best_value', 0):.8f}\n"
            msg += f"🕒 Execution Time: {res_real.get('execution_time', 0):.3f} s\n"
            msg += f"🧬 Winning Chromosome:\n[{format_chrom(res_real.get('best_individual', 'No data'))}]\n"

            diff = abs(res_bin.get('best_value', 0) - res_real.get('best_value', 0))
            self.view.status_label.configure(text=f"✅ Comparison finished! Value difference: {diff:.6f}", text_color="green")

            self.view.results_console.insert("end", msg)
            self.view.results_console.configure(state="disabled")

        except Exception as e:
            print(f"Error in finalize_comparison: {e}")
        finally:
            self.view.start_button.configure(state="normal", text="START EVOLUTION")
            self.view.progress_bar.set(1.0)
            self.reset_ui()
            self.root.after(1500, lambda: self.view.progress_bar.set(0))

    def reset_ui(self):
        self.set_ui_state("normal")
        self.view.start_button.configure(state="normal", text="START EVOLUTION 🧬")
        self.view.progress_bar.set(1.0)
        self.view.update_visibility()

    def on_closing(self):
        """Hard memory cleanup when exiting the application."""

        plt.close('all')
        self.root.quit()
        self.root.destroy()


# def launch_gui():
#     ctk.set_appearance_mode("System")
#     ctk.set_default_color_theme("blue")
#     root = ctk.CTk()
#     app = GeneticAlgorithmController(root)
#     root.mainloop()


def launch_gui():
    ctk.set_appearance_mode("System")
    theme_path = os.path.join(os.path.dirname(__file__), "green_mode.json")

    try:
        ctk.set_default_color_theme(theme_path)
    except Exception as e:
        print(f"Could not load the motif from {theme_path}. Error: {e}")
        ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    app = GeneticAlgorithmController(root)
    root.mainloop()


if __name__ == "__main__":
    launch_gui()
