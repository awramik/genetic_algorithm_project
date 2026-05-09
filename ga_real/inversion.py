import random


def inversion(individual):

    mutated = individual.copy()

    i1 = random.randint(0, len(individual)-2)
    i2 = random.randint(i1+1, len(individual)-1)

    segment = mutated[i1:i2]

    segment.reverse()

    mutated[i1:i2] = segment

    return mutated
