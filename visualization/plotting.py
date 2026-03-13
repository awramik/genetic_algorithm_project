import matplotlib.pyplot as plt


def plot_convergence(history):

    generations = list(range(len(history)))

    plt.figure(figsize=(8,5))

    plt.plot(generations, history)

    plt.xlabel("Generation")
    plt.ylabel("Best function value")

    plt.title("Genetic Algorithm Convergence")

    plt.grid(True)

    plt.show()
