import numpy as np
from utils.encoding import binary_to_real
from functions.sphere import sphere
from config import LOWER_BOUND, UPPER_BOUND, DIMENSIONS


def evaluate_individual(individual):
    """
    Evaluate fitness of a single individual.
    """

    chromosome_length = len(individual)
    segment_length = chromosome_length // DIMENSIONS

    real_values = []

    for i in range(DIMENSIONS):

        start = i * segment_length
        end = start + segment_length

        gene = individual[start:end]

        real_value = binary_to_real(gene, LOWER_BOUND, UPPER_BOUND)

        real_values.append(real_value)

    x = np.array(real_values)

    function_value = sphere(x)

    fitness = 1 / (1 + function_value)

    return fitness, function_value, x


def evaluate_population(population):

    results = []

    for individual in population:

        fitness, value, x = evaluate_individual(individual)

        results.append({
            "chromosome": individual,
            "fitness": fitness,
            "value": value,
            "x": x
        })

    return results
