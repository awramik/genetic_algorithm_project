import random


def mutate(individual, mutation_rate):
    """
    Bit flip mutation.
    """

    mutated = individual.copy()

    for i in range(len(mutated)):

        if random.random() < mutation_rate:

            mutated[i] = 1 - mutated[i]

    return mutated


def single_point_mutation(individual):

    import random

    mutated = individual.copy()

    index = random.randint(0, len(individual)-1)

    mutated[index] = 1 - mutated[index]

    return mutated


def two_point_mutation(individual):

    import random

    mutated = individual.copy()

    i1 = random.randint(0, len(individual)-1)
    i2 = random.randint(0, len(individual)-1)

    mutated[i1] = 1 - mutated[i1]
    mutated[i2] = 1 - mutated[i2]

    return mutated


def boundary_mutation(individual):

    import random

    mutated = individual.copy()

    if random.random() < 0.5:
        mutated[0] = 1 - mutated[0]
    else:
        mutated[-1] = 1 - mutated[-1]

    return mutated
