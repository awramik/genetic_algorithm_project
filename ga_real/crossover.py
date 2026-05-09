import random


def crossover_arithmetic(parent1, parent2):
    """
    Arithmetic crossover.
    Offspring are a linear combination of the parents' genes.
    """
    k = random.random()
    offspring1 = [k * p1 + (1 - k) * p2 for p1, p2 in zip(parent1, parent2)]
    offspring2 = [(1 - k) * p1 + k * p2 for p1, p2 in zip(parent1, parent2)]
    return offspring1, offspring2


def crossover_averaging(parent1, parent2):
    """Averaging crossover: the child is halfway between its parents."""
    offspring = [(p1 + p2) / 2.0 for p1, p2 in zip(parent1, parent2)]

    return offspring, offspring.copy()


def crossover_linear(parent1, parent2, fitness_func=None):
    """
    Linear crossover: creates 3 potential offspring and selects the best 2.
    Z1 = 0.5*P1 + 0.5*P2
    Z2 = 1.5*P1 - 0.5*P2
    Z3 = -0.5*P1 + 1.5*P2
    """
    z1 = [0.5 * p1 + 0.5 * p2 for p1, p2 in zip(parent1, parent2)]
    z2 = [1.5 * p1 - 0.5 * p2 for p1, p2 in zip(parent1, parent2)]
    z3 = [-0.5 * p1 + 1.5 * p2 for p1, p2 in zip(parent1, parent2)]

    candidates = [z1, z2, z3]

    # if there is no fitness, return first two
    if fitness_func is None:
        return z1, z2

    # Sort based on fitness
    candidates.sort(key=lambda x: fitness_func(x), reverse=True)
    return candidates[0], candidates[1]


def crossover_blx_alpha(parent1, parent2, alpha=0.5):
    """
    BLX-alpha crossover: draws a gene from a range expanded by the alpha factor.
    It allows for exploration beyond the range directly defined by the parents.
    """
    offspring1 = []
    offspring2 = []

    for p1, p2 in zip(parent1, parent2):
        dmin, dmax = min(p1, p2), max(p1, p2)
        diff = dmax - dmin

        # range: [dmin - alpha*diff, dmax + alpha*diff]
        lower = dmin - alpha * diff
        upper = dmax + alpha * diff

        offspring1.append(random.uniform(lower, upper))
        offspring2.append(random.uniform(lower, upper))

    return offspring1, offspring2


def crossover_blx_alpha_beta(parent1, parent2, alpha=0.25, beta=0.75):
    """
    Alpha and beta crossover (BLX-alpha-beta).
    The sampling interval is expanded asymmetrically using two parameters: alpha and beta.
    """
    offspring1 = []
    offspring2 = []

    for p1, p2 in zip(parent1, parent2):
        dmin, dmax = min(p1, p2), max(p1, p2)
        diff = dmax - dmin

        # range: [dmin - alpha*diff, dmax + beta*diff]
        lower = dmin - alpha * diff
        upper = dmax + beta * diff

        offspring1.append(random.uniform(lower, upper))
        offspring2.append(random.uniform(lower, upper))

    return offspring1, offspring2


def crossover_population(population, crossover_rate, crossover_type="arithmetic", fitness_func=None):
    new_population = []
    pop_size = len(population)

    # go through the population in pairs
    for i in range(0, pop_size, 2):
        p1 = population[i]
        # protection against odd population numbers
        p2 = population[i + 1] if i + 1 < pop_size else population[0]

        if random.random() < crossover_rate:
            if crossover_type == "arithmetic":
                o1, o2 = crossover_arithmetic(p1, p2)
            elif crossover_type == "averaging":
                o1, o2 = crossover_averaging(p1, p2)
            elif crossover_type == "linear":
                o1, o2 = crossover_linear(p1, p2, fitness_func)
            elif crossover_type == "blx_alfa":
                o1, o2 = crossover_blx_alpha(p1, p2, alpha=0.5)
            elif crossover_type == "blx_alfa_beta":
                o1, o2 = crossover_blx_alpha_beta(p1, p2, alpha=0.25, beta=0.75)
            else:
                o1, o2 = p1.copy(), p2.copy()
            new_population.extend([o1, o2])
        else:
            # no crossover - parents move on
            new_population.extend([p1.copy(), p2.copy()])

    # cut the excess if it adds too much, because of an odd population
    return new_population[:pop_size]
