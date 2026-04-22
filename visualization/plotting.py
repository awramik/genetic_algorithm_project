import matplotlib.pyplot as plt


def create_convergence_figure(history):

    generations = list(range(len(history)))

    fig, ax = plt.subplots(figsize=(8, 6))

    ax.plot(generations, history, linewidth=2)

    ax.set_title("Genetic Algorithm Convergence")
    ax.set_xlabel("Generation")
    ax.set_ylabel("Best Function Value")
    ax.grid(True)

    return fig