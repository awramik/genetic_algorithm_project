def elitism(results, elite_size):

    sorted_results = sorted(
        results,
        key=lambda x: x["fitness"],
        reverse=True
    )

    elites = []

    for i in range(elite_size):

        elites.append(sorted_results[i]["chromosome"])

    return elites
