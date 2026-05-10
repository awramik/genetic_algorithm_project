
import random
import time
from ga_real.population import create_population
from ga_real.fitness import evaluate_population, evaluate_individual
from ga_real.selection import (
    best_selection,
    roulette_selection,
    tournament_selection
)
from ga_real.crossover import crossover_population
from ga_real.mutation import mutate_population
from ga_real.elitism import elitism


def run_genetic_algorithm(
        population_size,
        generations,
        dimensions,
        crossover_rate,
        mutation_rate,
        selection_method,
        crossover_method,
        mutation_method,
        lower_bound,
        upper_bound,
        optimization_type,
        elite_size,
        alpha=0.5, beta=0.75, sigma=0.5,
        progress_callback=None
):
    start_time = time.time()

    # STEP 1: Initialize the real population
    population = create_population(population_size, dimensions, lower_bound, upper_bound)

    best_history = []
    avg_history = []

    for generation in range(generations):
        # STEP 2: Population Assessment
        evaluated_pop = evaluate_population(population, optimization_type)

        # Sort (for elitism and statistics)
        if optimization_type == "Min":
            evaluated_pop.sort(key=lambda x: x['value'])
        else:
            evaluated_pop.sort(key=lambda x: x['value'], reverse=True)

        # statistics
        best_val = evaluated_pop[0]['value']
        avg_val = sum(ind['value'] for ind in evaluated_pop) / population_size
        best_history.append(best_val)
        avg_history.append(avg_val)

        # STEP 3: Elitism
        elite_individuals = elitism(evaluated_pop, elite_size)

        # STEP 4: Selection
        remaining_size = population_size - len(elite_individuals)
        if selection_method == "best":
            selected_parents = best_selection(evaluated_pop, remaining_size)
        elif selection_method == "roulette":
            selected_parents = roulette_selection(evaluated_pop, remaining_size)
        else:
            selected_parents = tournament_selection(evaluated_pop, remaining_size)

        # STEP 5: Crossover
        fitness_func = lambda ind: evaluate_individual(ind, optimization_type)[0]

        offspring = crossover_population(
            selected_parents,
            crossover_rate,
            crossover_type=crossover_method,
            fitness_func=fitness_func,
            alpha=alpha,
            beta=beta
        )

        # STEP 6: Mutation (uniform or Gauss)
        population = mutate_population(
            offspring,
            mutation_rate,
            lower_bound,
            upper_bound,
            mutation_type=mutation_method,
            sigma=sigma
        )

        # clamping
        for i in range(len(population)):
            population[i] = [max(lower_bound, min(gene, upper_bound)) for gene in population[i]]

        # new population's elite
        population.extend(elite_individuals)
        # ensuring a stable population size
        population = population[:population_size]

        if progress_callback:
            progress_callback(generation + 1, generations)

    end_time = time.time()
    execution_time = end_time - start_time

    # results (the best individual from the last generation)
    final_eval = evaluate_population(population, optimization_type)
    if optimization_type == "Min":
        final_eval.sort(key=lambda x: x['value'])
    else:
        final_eval.sort(key=lambda x: x['value'], reverse=True)

    return {
        "best_individual": final_eval[0]['chromosome'],
        "best_value": final_eval[0]['value'],
        "best_history": best_history,
        "avg_history": avg_history,
        "execution_time": execution_time
    }
