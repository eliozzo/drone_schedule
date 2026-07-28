"""Grafici del rapporto tra makespan algoritmico e ottimo ILP."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def _plot_group(
    data: pd.DataFrame,
    x_column: str,
    output: Path,
) -> None:
    # L'ILP è il denominatore del rapporto: viene mostrata con la baseline
    # tratteggiata, non come una linea duplicata nei dati.
    valid = data.dropna(subset=["ratio"])
    valid = valid[valid["algorithm"] != "ILP"]
    grouped = (
        valid.groupby(["mode", "algorithm", x_column], as_index=False)["ratio"]
        .mean()
        .sort_values(x_column)
    )

    fig, ax = plt.subplots(figsize=(8, 5))
    for (mode, algorithm), values in grouped.groupby(["mode", "algorithm"]):
        label = f"{algorithm} - {mode}"
        ax.plot(values[x_column], values["ratio"], marker="o", label=label)

    ax.axhline(1.0, color="black", linestyle="--", linewidth=1, label="Ottimo ILP")
    ax.set_xlabel("Numero di droni n" if x_column == "n" else "Numero di archi m")
    ax.set_ylabel("Rapporto makespan algoritmo / makespan ottimo")
    ax.set_xticks(sorted(valid[x_column].unique()))
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output, dpi=180)
    plt.close(fig)


def create_plots(csv_path: Path, output_dir: Path | None = None) -> None:
    data = pd.read_csv(csv_path)
    output_dir = output_dir or csv_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    _plot_group(data, "n", output_dir / "ratio_vs_n.png")
    _plot_group(data, "m", output_dir / "ratio_vs_m.png")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path", type=Path)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    create_plots(args.csv_path, args.output_dir)


if __name__ == "__main__":
    main()
