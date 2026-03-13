from ga.population import create_population
from ga.fitness import evaluate_population
from ga.selection import tournament_selection
from ga.crossover import one_point_crossover
from ga.mutation import mutate
from ga.inversion import inversion
from ga.elitism import elitism

from config import *
import random


def run_genetic_algorithm():

    population = create_population(
        POPULATION_SIZE,
        CHROMOSOME_LENGTH
    )

    best_history = []

    for generation in range(GENERATIONS):

        results = evaluate_population(population)

        best = max(results, key=lambda x: x["fitness"])

        best_history.append(best["value"])

        print(
            f"Generation {generation} | "
            f"Best value: {best['value']:.6f}"
        )

        new_population = []

        elites = elitism(results, elite_size=2)

        new_population.extend(elites)

        parents = tournament_selection(
            results,
            num_parents=POPULATION_SIZE
        )

        while len(new_population) < POPULATION_SIZE:

            p1 = random.choice(parents)
            p2 = random.choice(parents)

            if random.random() < CROSSOVER_RATE:

                child1, child2 = one_point_crossover(p1, p2)

            else:

                child1, child2 = p1.copy(), p2.copy()

            child1 = mutate(child1, MUTATION_RATE)
            child2 = mutate(child2, MUTATION_RATE)

            if random.random() < 0.1:
                child1 = inversion(child1)

            if random.random() < 0.1:
                child2 = inversion(child2)

            new_population.append(child1)

            if len(new_population) < POPULATION_SIZE:
                new_population.append(child2)

        population = new_population

    return best_history
