import matplotlib.pyplot as plt


def create_convergence_figure(best_history, avg_history):
    generations = list(range(len(best_history)))

    fig, ax = plt.subplots(figsize=(8, 6), facecolor='#E8EFEA')
    ax.set_facecolor('#E8EFEA')

    ax.plot(generations, best_history, label="Best", color="#1E3628", linewidth=2.5)
    ax.plot(generations, avg_history, label="Average", color="#A65D37", linewidth=2, linestyle="--")

    ax.set_title("Genetic Algorithm Convergence", fontsize=14, fontweight='bold', color="#1A2421", pad=15)
    ax.set_xlabel("Epoch (Generation)", fontsize=11, color="#2C3E35")
    ax.set_ylabel("Function value", fontsize=11, color="#2C3E35")

    # legend
    ax.grid(True, linestyle=':', alpha=0.7, color="#B5C7BC")
    ax.legend(loc="best", frameon=True, facecolor="#F1F5F2", edgecolor="#2C3E35")

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#8A9E92')
    ax.spines['bottom'].set_color('#8A9E92')

    fig.tight_layout()
    return fig
