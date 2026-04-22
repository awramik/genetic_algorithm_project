import os
from datetime import datetime


def save_results(
        population_size,
        generations,
        chromosome_length,
        crossover_rate,
        mutation_rate,
        selection_method,
        crossover_method,
        mutation_method,
        best_value,
        execution_time
):

    os.makedirs("results/logs", exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    filename = f"results/logs/run_{timestamp}.txt"

    with open(filename, "w", encoding="utf-8") as file:
        file.write(f"Population size: {population_size}\n")
        file.write(f"Generations: {generations}\n")
        file.write(f"Chromosome length: {chromosome_length}\n")
        file.write(f"Crossover rate: {crossover_rate}\n")
        file.write(f"Mutation rate: {mutation_rate}\n")
        file.write(f"Selection method: {selection_method}\n")
        file.write(f"Crossover method: {crossover_method}\n")
        file.write(f"Mutation method: {mutation_method}\n\n")

        file.write(f"Best value: {best_value:.6f}\n")
        file.write(f"Execution time: {execution_time:.4f} s\n")

    return filename