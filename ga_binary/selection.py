
import random


def best_selection(results, num_parents):
    """
    Select best individuals based on fitness.
    """

    sorted_results = sorted(
        results,
        key=lambda x: x["fitness"],
        reverse=True
    )

    selected = []

    for i in range(num_parents):
        selected.append(sorted_results[i]["chromosome"])

    return selected


def roulette_selection(results, num_parents):
    """
    Roulette wheel selection.
    """

    fitness_values = [r["fitness"] for r in results]

    total_fitness = sum(fitness_values)

    # if the entire population has fitness = 0, the chances are equal (random selection)
    if total_fitness == 0:
        return [r["chromosome"] for r in random.choices(results, k=num_parents)]

    probabilities = [f / total_fitness for f in fitness_values]

    selected = []

    for _ in range(num_parents):

        r = random.random()
        cumulative = 0

        for i, p in enumerate(probabilities):

            cumulative += p

            if r <= cumulative:
                selected.append(results[i]["chromosome"])
                break

    return selected


def tournament_selection(results, num_parents, tournament_size=3):
    """
    Tournament selection.
    """

    selected = []

    for _ in range(num_parents):

        tournament = random.sample(results, tournament_size)

        best = max(tournament, key=lambda x: x["fitness"])

        selected.append(best["chromosome"])

    return selected
