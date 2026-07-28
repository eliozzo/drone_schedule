"""Esegue il setting sperimentale e salva risultati e grafici."""

from __future__ import annotations

import argparse
import csv
import time
from pathlib import Path

from algoritmi.heap_based import heap_based
from algoritmi.ilp import solve_ilp
from algoritmi.models import makespan
from algoritmi.rec import rec
from experimental_setting.generator import generate_instance
from experimental_setting.plots import create_plots


def run_experiments(
    n_values: list[int],
    m_values: list[int],
    instances: int,
    modes: list[str],
    output_dir: Path,
    base_seed: int,
    time_limit: float | None,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "results.csv"
    fields = [
        "mode",
        "n",
        "m",
        "instance",
        "seed",
        "algorithm",
        "makespan",
        "optimal_makespan",
        "ratio",
        "runtime_seconds",
    ]

    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()

        for mode_index, mode in enumerate(modes):
            bidirectional = mode == "bidirectional"
            for n in n_values:
                for m in m_values:
                    for instance_index in range(instances):
                        seed = (
                            base_seed
                            + mode_index * 1_000_000
                            + n * 10_000
                            + m * 100
                            + instance_index
                        )
                        instance = generate_instance(
                            n,
                            m,
                            bidirectional=bidirectional,
                            seed=seed,
                        )

                        start = time.perf_counter()
                        _, optimum = solve_ilp(instance, time_limit=time_limit)
                        ilp_runtime = time.perf_counter() - start
                        writer.writerow(
                            {
                                "mode": mode,
                                "n": n,
                                "m": m,
                                "instance": instance_index,
                                "seed": seed,
                                "algorithm": "ILP",
                                "makespan": optimum,
                                "optimal_makespan": optimum,
                                "ratio": 1.0,
                                "runtime_seconds": ilp_runtime,
                            }
                        )

                        algorithms = [("Heap-Based", heap_based)]
                        if not bidirectional:
                            algorithms.insert(0, ("REC", rec))

                        for name, algorithm in algorithms:
                            start = time.perf_counter()
                            value = makespan(algorithm(instance))
                            runtime = time.perf_counter() - start
                            writer.writerow(
                                {
                                    "mode": mode,
                                    "n": n,
                                    "m": m,
                                    "instance": instance_index,
                                    "seed": seed,
                                    "algorithm": name,
                                    "makespan": value,
                                    "optimal_makespan": optimum,
                                    "ratio": value / optimum,
                                    "runtime_seconds": runtime,
                                }
                            )
                        handle.flush()
                        print(
                            f"{mode}: n={n}, m={m}, "
                            f"istanza={instance_index + 1}/{instances}"
                        )

    create_plots(csv_path, output_dir)
    return csv_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=("unidirectional", "bidirectional", "both"),
        default="both",
    )
    parser.add_argument("--n-values", nargs="+", type=int, default=[5, 10, 15])
    parser.add_argument("--m-values", nargs="+", type=int, default=[10, 20, 30, 40])
    parser.add_argument("--instances", type=int, default=33)
    parser.add_argument("--output-dir", type=Path, default=Path("results"))
    parser.add_argument("--base-seed", type=int, default=2026)
    parser.add_argument("--time-limit", type=float)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    modes = (
        ["unidirectional", "bidirectional"]
        if args.mode == "both"
        else [args.mode]
    )
    csv_path = run_experiments(
        n_values=args.n_values,
        m_values=args.m_values,
        instances=args.instances,
        modes=modes,
        output_dir=args.output_dir,
        base_seed=args.base_seed,
        time_limit=args.time_limit,
    )
    print(f"Risultati salvati in {csv_path}")


if __name__ == "__main__":
    main()
