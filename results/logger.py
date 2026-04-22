import os
import csv
from datetime import datetime


def save_results(
        experiment_name,
        population_size,
        generations,
        chromosome_length,
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
        inversion_rate
):
    os.makedirs("results/logs", exist_ok=True)
    timestamp = datetime.now().strftime("%H-%M-%S")

    base_name = f"{experiment_name}_{timestamp}"

    # 1. Zapis konfiguracji do pliku TXT
    txt_filename = f"results/logs/{base_name}_params.txt"
    with open(txt_filename, "w", encoding="utf-8") as file:
        file.write(f"EKSPERYMENT: {experiment_name}\n")
        file.write("=== KONFIGURACJA EKSPERYMENTU ===\n")
        file.write(f"Cel optymalizacji: {optimization_type}\n")
        file.write(f"Wymiary (N): {dimensions}\n")
        file.write(f"Dziedzina (granice): [{lower_bound}, {upper_bound}]\n\n")

        file.write("=== PARAMETRY ALGORYTMU ===\n")
        file.write(f"Wielkosc populacji: {population_size}\n")
        file.write(f"Liczba pokolen: {generations}\n")
        file.write(f"Dlugosc chromosomu: {chromosome_length} bitow\n")
        file.write(f"Prawdopodobienstwo krzyzowania: {crossover_rate}\n")
        file.write(f"Prawdopodobienstwo mutacji: {mutation_rate}\n")
        file.write(f"Prawdopodobienstwo inwersji: {inversion_rate}\n")
        file.write(f"Rozmiar elity: {elite_size}\n\n")

        file.write("=== METODY ===\n")
        file.write(f"Selekcja: {selection_method}\n")
        file.write(f"Krzyzowanie: {crossover_method}\n")
        file.write(f"Mutacja: {mutation_method}\n\n")

        file.write("=== WYNIKI ===\n")
        file.write(f"Najlepsza znaleziona wartosc: {best_history[-1]:.6f}\n")
        file.write(f"Czas wykonania algorytmu: {execution_time:.4f} s\n")

    # 2. Zapis CSV (zoptymalizowany pod Pythona)
    csv_filename = f"results/logs/{base_name}_history.csv"
    with open(csv_filename, "w", newline='', encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerow(["epoch", "best_value", "average_value"])
        for gen in range(len(best_history)):
            writer.writerow([gen, round(best_history[gen], 6), round(avg_history[gen], 6)])

    return base_name