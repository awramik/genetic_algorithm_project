import os
import csv
import json
import uuid
from datetime import datetime


def save_results(
        experiment_name,
        ga_type,
        population_size,
        generations,
        crossover_rate,
        mutation_rate,
        selection_method,
        crossover_method,
        mutation_method,
        best_history,
        avg_history,
        std_history,
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
        sigma=None,
        best_individual=None
):
    os.makedirs("results/logs", exist_ok=True)

    timestamp = datetime.now().strftime("%d-%m--%H-%M")
    run_id = uuid.uuid4().hex[:4]
    base_name = f"{experiment_name}_{ga_type}_{timestamp}_{run_id}"

    # 1. Saving configuration to a JSON file
    json_filename = f"results/logs/{base_name}_params.json"

    # dictionary
    config_dict = {
        "experiment": {
            "name": experiment_name,
            "ga_type": ga_type,
            "optimization": optimization_type,
            "dimensions": dimensions,
            "domain": [lower_bound, upper_bound]
        },
        "parameters": {
            "population_size": population_size,
            "generations": generations,
            "crossover_rate": crossover_rate,
            "mutation_rate": mutation_rate,
            "elite_size": elite_size
        },
        "methods": {
            "selection": selection_method,
            "crossover": crossover_method,
            "mutation": mutation_method
        },
        "results": {
            "best_value": round(best_history[-1], 6) if best_history else None,
            "execution_time_s": round(execution_time, 4),
            "best_individual": best_individual
        },
        "specifics": {}
    }

    # saving specific params only if they exist
    if chromosome_length is not None:
        config_dict["specifics"]["chromosome_length"] = chromosome_length
    if inversion_rate is not None:
        config_dict["specifics"]["inversion_rate"] = inversion_rate
    if alpha is not None:
        config_dict["specifics"]["alpha"] = alpha
    if beta is not None:
        config_dict["specifics"]["beta"] = beta
    if sigma is not None:
        config_dict["specifics"]["sigma"] = sigma

    with open(json_filename, "w", encoding="utf-8") as file:
        json.dump(config_dict, file, indent=4)

    # 2. CSV file
    csv_filename = f"results/logs/{base_name}_history.csv"
    with open(csv_filename, "w", newline='', encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerow(["experiment_name", "ga_type", "epoch", "best_value", "average_value", "std_value"])
        for gen in range(len(best_history)):
            std_val = std_history[gen] if gen < len(std_history) else 0
            writer.writerow([
                experiment_name,
                ga_type,
                gen,
                round(best_history[gen], 6),
                round(avg_history[gen], 6),
                round(std_val, 6)
            ])

    # 3. Global Summary CSV
    summary_dir = "results/summary"
    os.makedirs(summary_dir, exist_ok=True)

    summary_filename = os.path.join(summary_dir, "global_summary.csv")
    file_exists = os.path.isfile(summary_filename)

    with open(summary_filename, "a", newline='', encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=',')
        # create file if it doesn't exist
        if not file_exists:
            writer.writerow([
                "timestamp", "experiment_name", "ga_type", "pop_size",
                "generations", "crossover_method", "mutation_method",
                "execution_time", "best_value"
            ])

        # adding current experiment
        writer.writerow([
            timestamp, experiment_name, ga_type, population_size,
            generations, crossover_method, mutation_method,
            round(execution_time, 4), round(best_history[-1], 6)
        ])

    return base_name
