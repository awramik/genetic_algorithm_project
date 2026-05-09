import numpy as np
from functions.sphere import sphere


def evaluate_individual(individual, optimization_type):

    x = np.array(individual)

    # Hypersphere
    function_value = sphere(x)

    # Min/Max
    if optimization_type == "Min":
        fitness = 1.0 / (1.0 + function_value)
    else:
        fitness = function_value

    return fitness, function_value, x


def evaluate_population(population, optimization_type):
    results = []
    for individual in population:
        fitness, value, x = evaluate_individual(individual, optimization_type)
        results.append({
            "chromosome": individual,
            "fitness": fitness,
            "value": value,
            "x": x
        })
    return results
