import numpy as np
from utils.encoding import binary_to_real
from functions.sphere import sphere


def evaluate_individual(individual, dimensions, lower_bound, upper_bound, optimization_type):
    chromosome_length = len(individual)
    segment_length = chromosome_length // dimensions

    real_values = []
    for i in range(dimensions):
        start = i * segment_length
        end = start + segment_length
        gene = individual[start:end]

        real_value = binary_to_real(gene, lower_bound, upper_bound)
        real_values.append(real_value)

    x = np.array(real_values)
    function_value = sphere(x)

    # obsługa Min/Max
    if optimization_type == "Min":
        fitness = 1.0 / (1.0 + function_value)
    else:
        fitness = function_value

    return fitness, function_value, x


def evaluate_population(population, dimensions, lower_bound, upper_bound, optimization_type):
    results = []
    for individual in population:
        fitness, value, x = evaluate_individual(individual, dimensions, lower_bound, upper_bound, optimization_type)
        results.append({
            "chromosome": individual,
            "fitness": fitness,
            "value": value,
            "x": x
        })
    return results