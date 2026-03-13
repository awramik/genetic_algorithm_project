import random


def one_point_crossover(parent1, parent2):

    length = len(parent1)

    point = random.randint(1, length - 1)

    child1 = parent1[:point] + parent2[point:]
    child2 = parent2[:point] + parent1[point:]

    return child1, child2


def two_point_crossover(parent1, parent2):

    length = len(parent1)

    p1 = random.randint(1, length - 2)
    p2 = random.randint(p1 + 1, length - 1)

    child1 = (
        parent1[:p1]
        + parent2[p1:p2]
        + parent1[p2:]
    )

    child2 = (
        parent2[:p1]
        + parent1[p1:p2]
        + parent2[p2:]
    )

    return child1, child2


def uniform_crossover(parent1, parent2):

    import random

    child1 = []
    child2 = []

    for g1, g2 in zip(parent1, parent2):

        if random.random() < 0.5:

            child1.append(g1)
            child2.append(g2)

        else:

            child1.append(g2)
            child2.append(g1)

    return child1, child2


def grainy_crossover(parent1, parent2, grain_size=2):

    child1 = []
    child2 = []

    for i in range(0, len(parent1), grain_size):

        if random.random() < 0.5:

            child1 += parent1[i:i+grain_size]
            child2 += parent2[i:i+grain_size]

        else:

            child1 += parent2[i:i+grain_size]
            child2 += parent1[i:i+grain_size]

    return child1, child2
