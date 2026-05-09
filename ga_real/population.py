import random


import random

def create_individual(dimensions, lower_bound, upper_bound):
    """
    Creates a single individual (a real chromosome).
    Genes are random numbers in the range [lower_bound, upper_bound].
    """
    return [random.uniform(lower_bound, upper_bound) for _ in range(dimensions)]

def create_population(population_size, dimensions, lower_bound, upper_bound):
    """
    Creates the initial population.
    """
    population = []

    for _ in range(population_size):
        individual = create_individual(dimensions, lower_bound, upper_bound)
        population.append(individual)

    return population
