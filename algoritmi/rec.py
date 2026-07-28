"""Algoritmo REC"""

from __future__ import annotations

from .models import Instance, Schedule, validate_schedule


def rec(instance: Instance) -> Schedule:
    """Calcola REC per un'istanza unidirezionale."""

    if instance.bidirectional or any(d.direction != 1 for d in instance.drones):
        raise ValueError("REC è definito solo per istanze unidirezionali")

    #riga 1) ultimo arco decrescente, poi primo arco decrescente.
    drones = sorted(
        instance.drones,
        key=lambda d: (d.last_edge, d.start_edge),
        reverse=True,
    )
    schedule: Schedule = {drone.id: [] for drone in instance.drones}#risultato in costruzione
    used_by_edge: list[set[int]] = [set() for _ in range(instance.m)]#slot già occupati sull'arco j
    previous_time = {drone.id: drone.release for drone in instance.drones}#ultimo slot assegnato al drone i
#usare un set rende veloce vedere se uno slot è già assegnato
    for edge in range(instance.m):
        starters = [d for d in drones if d.start_edge == edge]#per ogni arco individua quelli che partono da quell'arco
        for drone in drones:
            if edge not in drone.edges:
                continue
#calcolo alpha
            position = edge - drone.start_edge
            residual = drone.length - position
            alpha = sum(other.length > residual for other in starters)
            #calcolo slot minimo t = max{S[i,j-1]+1,a[i,j] + 1}
            lower_bound = max(
                previous_time[drone.id] + 1,
                alpha + drone.release,
            )
            time = lower_bound
            while time in used_by_edge[edge]:#se lo slot è già occupato rec prova il successivo
                time += 1
#aggiorno strutture
            schedule[drone.id].append(time)
            previous_time[drone.id] = time
            used_by_edge[edge].add(time)

    validate_schedule(instance, schedule)
    return schedule
