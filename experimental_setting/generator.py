"""Generatore delle istanze casuali descritte nel setting sperimentale."""

from __future__ import annotations

import random

from algoritmi.models import Drone, Instance


def generate_instance(
    n: int,
    m: int,
    *,
    bidirectional: bool,
    seed: int,
) -> Instance:
    """Genera un'istanza riproducibile

    Release time e lunghezza sono uniformi nelle istanze bidirezionali anche
    la direzione è scelta uniformement
    """

    rng = random.Random(seed)
    drones: list[Drone] = []

    for drone_id in range(n):
        length = rng.randint(1, m)
        release = rng.randint(1, 5)
        direction = rng.choice((-1, 1)) if bidirectional else 1
        if direction == 1:
            start_edge = rng.randint(0, m - length)
        else:
            start_edge = rng.randint(length - 1, m - 1)
        drones.append(
            Drone(
                id=drone_id,
                start_edge=start_edge,
                length=length,
                release=release,
                direction=direction,
            )
        )

    return Instance(m=m, drones=tuple(drones), bidirectional=bidirectional)
