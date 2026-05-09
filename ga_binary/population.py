import random


def create_individual(chromosome_length):
    """
    Create a single individual (chromosome).
    """
    return [random.randint(0, 1) for _ in range(chromosome_length)]

def create_population(population_size, chromosome_length):
    """
    Create initial population.
    """
    population = []

    for _ in range(population_size):
        individual = create_individual(chromosome_length)
        population.append(individual)

    return population
