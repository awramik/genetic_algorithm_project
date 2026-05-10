import os
import csv
from datetime import datetime


def save_results(
        experiment_name,
        population_size,
        generations,
        crossover_rate,
        mutation_rate,
        selection_method,
        crossover_method,
        mutation_method,
        best_history,
        avg_history,
        execution_time,
        optimization_type,
        dimensions,
        lower_bound,
        upper_bound,
        elite_size,
        chromosome_length=None,
        inversion_rate=None,
        alpha=None,
        beta=None,
        sigma=None
):
    os.makedirs("results/logs", exist_ok=True)
    timestamp = datetime.now().strftime("%H-%M-%S")
    base_name = f"{experiment_name}_{timestamp}"

    # 1. Saving configuration to a TXT file
    txt_filename = f"results/logs/{base_name}_params.txt"
    with open(txt_filename, "w", encoding="utf-8") as file:
        file.write(f"EXPERIMENT: {experiment_name}\n")
        file.write("=== EXPERIMENT CONFIGURATION ===\n")
        file.write(f"Optimisation type: {optimization_type}\n")
        file.write(f"Dimensions (N): {dimensions}\n")
        file.write(f"Domain (boundary): [{lower_bound}, {upper_bound}]\n\n")

        file.write("=== ALGORITHM PARAMETERS ===\n")
        file.write(f"Population size: {population_size}\n")
        file.write(f"Generations: {generations}\n")
        file.write(f"Crossover rate: {crossover_rate}\n")
        file.write(f"Mutation rate: {mutation_rate}\n")
        file.write(f"Elite size: {elite_size}\n")

        # specific params for binary chromosome
        if chromosome_length is not None:
            file.write(f"Chromosome length: {chromosome_length} bits\n")
        if inversion_rate is not None:
            file.write(f"Inversion rate: {inversion_rate}\n")

        file.write("\n=== METHODS ===\n")
        file.write(f"Selection: {selection_method}\n")
        file.write(f"Crossover: {crossover_method}\n")

        # specific parameters for BLX crossover
        if alpha is not None:
            file.write(f"  -> BLX Alpha: {alpha}\n")
        if beta is not None:
            file.write(f"  -> BLX Beta: {beta}\n")

        file.write(f"Mutation: {mutation_method}\n")

        # specific parameters for gaussian mutation
        if sigma is not None:
            file.write(f"  -> Gauss Sigma: {sigma}\n")

        file.write("\n=== RESULTS ===\n")
        file.write(f"Best found value: {best_history[-1]:.6f}\n")
        file.write(f"Execution time: {execution_time:.4f} s\n")

    # 2. CSV file
    csv_filename = f"results/logs/{base_name}_history.csv"
    with open(csv_filename, "w", newline='', encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerow(["epoch", "best_value", "average_value"])
        for gen in range(len(best_history)):
            writer.writerow([gen, round(best_history[gen], 6), round(avg_history[gen], 6)])

    return base_name
