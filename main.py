from ga.genetic_algorithm import run_genetic_algorithm
from visualization.plotting import plot_convergence


def main():

    history = run_genetic_algorithm()

    plot_convergence(history)
