import matplotlib.pyplot as plt


def create_convergence_figure(best_history, avg_history):
    generations = list(range(len(best_history)))

    # Używamy nieco bardziej płaskiego stylu tła
    fig, ax = plt.subplots(figsize=(8, 6), facecolor='#F0F4F9')
    ax.set_facecolor('#FFFFFF')

    # Dwie linie: Najlepszy (ciągła niebieska) i Średnia (przerywana pomarańczowa)
    ax.plot(generations, best_history, label="Najlepszy (Best)", color="#2563EB", linewidth=2.5)
    ax.plot(generations, avg_history, label="Średnia populacji (Average)", color="#F59E0B", linewidth=2, linestyle="--")

    ax.set_title("Konwergencja Algorytmu Genetycznego", fontsize=14, fontweight='bold', color="#0F172A", pad=15)
    ax.set_xlabel("Epoka (Generation)", fontsize=11, color="#1E293B")
    ax.set_ylabel("Wartość funkcji", fontsize=11, color="#1E293B")

    # Elegancka siatka i legenda
    ax.grid(True, linestyle=':', alpha=0.7, color="#94A3B8")
    ax.legend(loc="best", frameon=True, facecolor="#FFFFFF", edgecolor="#E2E8F0")

    # Ukrycie górnej i prawej ramki (Flat Design)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#CBD5E1')
    ax.spines['bottom'].set_color('#CBD5E1')

    fig.tight_layout()
    return fig