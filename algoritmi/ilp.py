
from __future__ import annotations

from collections import defaultdict

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import lil_matrix

from .models import Instance, Schedule, validate_schedule


def solve_ilp(
    instance: Instance,
    *,
    time_limit: float | None = None,
) -> tuple[Schedule, int]:
    """Restituisce schedule ottimo e makespan
    Usa variabili intere per i tempi una variabile binaria per ogni coppia di
    attraversamenti sullo stesso arco e una variabile di makespan
    """

    operations: list[tuple[int, int, int]] = []
    by_edge: dict[int, list[int]] = defaultdict(list)
    drone_op_indices: dict[int, list[int]] = defaultdict(list)

    for drone in instance.drones:
        for position, edge in enumerate(drone.edges):
            index = len(operations)
            operations.append((drone.id, position, edge))
            by_edge[edge].append(index)
            drone_op_indices[drone.id].append(index)

    conflicts = [
        (left, right)
        for indices in by_edge.values()
        for offset, left in enumerate(indices)
        for right in indices[offset + 1 :]
    ]
    op_count = len(operations)
    conflict_count = len(conflicts)
    makespan_index = op_count + conflict_count
    variable_count = makespan_index + 1

    # Schedule sequenziale sempre ammissibile è un limite superiore sicuro
    horizon = max((d.release for d in instance.drones), default=1) + op_count + 1
    big_m = horizon

    rows: list[dict[int, float]] = []
    lower: list[float] = []
    upper: list[float] = []

    def add_row(coefficients: dict[int, float], lb: float, ub: float) -> None:
        rows.append(coefficients)
        lower.append(lb)
        upper.append(ub)

    for drone in instance.drones:
        indices = drone_op_indices[drone.id]
        add_row({indices[0]: 1.0}, drone.release + 1, np.inf)
        for previous, current in zip(indices, indices[1:]):
            add_row({current: 1.0, previous: -1.0}, 1.0, np.inf)
        add_row({indices[-1]: 1.0, makespan_index: -1.0}, -np.inf, 0.0)

    for conflict_index, (left, right) in enumerate(conflicts):
        binary = op_count + conflict_index
        # t_left < t_right oppure t_right < t_left.
        add_row({left: 1, right: -1, binary: -big_m}, -np.inf, -1)
        add_row(
            {right: 1, left: -1, binary: big_m},
            -np.inf,
            big_m - 1,
        )

    matrix = lil_matrix((len(rows), variable_count), dtype=float)
    for row_index, coefficients in enumerate(rows):
        for column, value in coefficients.items():
            matrix[row_index, column] = value

    objective = np.zeros(variable_count)
    objective[makespan_index] = 1
    integrality = np.ones(variable_count, dtype=int)
    variable_lb = np.ones(variable_count)
    variable_ub = np.full(variable_count, horizon, dtype=float)
    if conflict_count:
        variable_lb[op_count:makespan_index] = 0
        variable_ub[op_count:makespan_index] = 1

    options: dict[str, float | bool] = {"disp": False}
    if time_limit is not None:
        options["time_limit"] = time_limit

    result = milp(
        c=objective,
        integrality=integrality,
        bounds=Bounds(variable_lb, variable_ub),
        constraints=LinearConstraint(
            matrix.tocsr(),
            np.asarray(lower),
            np.asarray(upper),
        ),
        options=options,
    )
    if not result.success or result.x is None:
        raise RuntimeError(f"ILP non risolta all'ottimo: {result.message}")

    schedule: Schedule = {drone.id: [] for drone in instance.drones}
    for index, (drone_id, _, _) in enumerate(operations):
        schedule[drone_id].append(int(round(result.x[index])))

    validate_schedule(instance, schedule)
    optimum = int(round(result.x[makespan_index]))
    return schedule, optimum
