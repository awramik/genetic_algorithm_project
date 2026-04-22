from ga.population import create_population
from ga.fitness import evaluate_population
from ga.selection import (
    best_selection,
    roulette_selection,
    tournament_selection
)
from ga.crossover import (
    one_point_crossover,
    two_point_crossover,
    uniform_crossover,
    grainy_crossover
)
from ga.mutation import (
    mutate,
    boundary_mutation,
    single_point_mutation,
    two_point_mutation
)
from ga.inversion import inversion
from ga.elitism import elitism

import random
import time


def run_genetic_algorithm(
        population_size,
        generations,
        chromosome_length,
        crossover_rate,
        mutation_rate,
        selection_method,
        crossover_method,
        mutation_method,
        elite_size=2,
        inversion_rate=0.1
):

    start_time = time.time()

    population = create_population(population_size, chromosome_length)

    best_history = []

    for generation in range(generations):

        results = evaluate_population(population)

        best = max(results, key=lambda x: x["fitness"])

        best_history.append(best["value"])

        print(f"Generation {generation} | Best value: {best['value']:.6f}")

        new_population = []

        elites = elitism(results, elite_size)
        new_population.extend(elites)

        # -------- selection --------
        if selection_method == "best":
            parents = best_selection(results, population_size)
        elif selection_method == "roulette":
            parents = roulette_selection(results, population_size)
        else:
            parents = tournament_selection(results, population_size)

        # -------- offspring --------
        while len(new_population) < population_size:

            p1 = random.choice(parents)
            p2 = random.choice(parents)

            # crossover
            if random.random() < crossover_rate:

                if crossover_method == "one_point":
                    child1, child2 = one_point_crossover(p1, p2)

                elif crossover_method == "two_point":
                    child1, child2 = two_point_crossover(p1, p2)

                elif crossover_method == "uniform":
                    child1, child2 = uniform_crossover(p1, p2)

                else:
                    child1, child2 = grainy_crossover(p1, p2)

            else:
                child1, child2 = p1.copy(), p2.copy()

            # mutation
            if mutation_method == "bit_flip":
                child1 = mutate(child1, mutation_rate)
                child2 = mutate(child2, mutation_rate)

            elif mutation_method == "boundary":
                child1 = boundary_mutation(child1)
                child2 = boundary_mutation(child2)

            elif mutation_method == "single_point":
                child1 = single_point_mutation(child1)
                child2 = single_point_mutation(child2)

            else:
                child1 = two_point_mutation(child1)
                child2 = two_point_mutation(child2)

            # inversion
            if random.random() < inversion_rate:
                child1 = inversion(child1)

            if random.random() < inversion_rate:
                child2 = inversion(child2)

            new_population.append(child1)

            if len(new_population) < population_size:
                new_population.append(child2)

        population = new_population

    execution_time = time.time() - start_time

    return best_history, execution_time
