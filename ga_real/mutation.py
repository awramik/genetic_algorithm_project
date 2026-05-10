import random

def mutate_uniform(individual, mutation_rate, lower_bound, upper_bound):
    """Uniform mutation: replaces a gene with a new random value from the domain."""
    mutated = []
    for gene in individual:
        if random.random() < mutation_rate:
            mutated.append(random.uniform(lower_bound, upper_bound))
        else:
            mutated.append(gene)
    return mutated

def mutate_gaussian(individual, mutation_rate, lower_bound, upper_bound, sigma=0.5):
    """Gaussian mutation: adds normally distributed noise N(0, sigma) to the gene."""
    mutated = []
    for gene in individual:
        if random.random() < mutation_rate:
            new_gene = gene + random.gauss(0, sigma)
            new_gene = max(lower_bound, min(new_gene, upper_bound))
            mutated.append(new_gene)
        else:
            mutated.append(gene)
    return mutated

def mutate_population(population, mutation_rate, lower_bound, upper_bound, mutation_type="gaussian", sigma=0.5):
    mutated_pop = []
    for ind in population:
        if mutation_type == "uniform":
            mutated_pop.append(mutate_uniform(ind, mutation_rate, lower_bound, upper_bound))
        else:
            mutated_pop.append(mutate_gaussian(ind, mutation_rate, lower_bound, upper_bound, sigma=sigma))
    return mutated_pop
