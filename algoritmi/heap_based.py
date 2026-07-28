"""Algoritmo Heap-Based."""

from __future__ import annotations

import heapq

from .models import Instance, Schedule, validate_schedule


def heap_based(instance: Instance) -> Schedule:
    """Calcola uno schedule usando una max-heap per ciascun arco

    Le nuove disponibilità prodotte al tempo t vengono inserite nelle heap solo
    al termine del passo evitando che un drone attraversi due archi nello
    stesso slot. Questo rende la procedura valida in entrambe le direzioni
    """

    drones_by_id = {drone.id: drone for drone in instance.drones}
    schedule: Schedule = {drone.id: [] for drone in instance.drones}
    heaps: list[list[tuple[int, int, int]]] = [[] for _ in range(instance.m)]
    waiting = sorted(instance.drones, key=lambda d: (d.release + 1, d.id))#i droni vengono ordinati in base al primo slot in cui possono attraversare un arco
    waiting_index = 0
    time = min((drone.release + 1 for drone in waiting), default=0)

    while waiting_index < len(waiting) or any(heaps):#prima di elaborare uno slot time metto nell'heap tutti i droni ormai disponibili
        while (
            waiting_index < len(waiting)
            and waiting[waiting_index].release + 1 <= time
        ):
            drone = waiting[waiting_index]
            # heapq è una min-heap: residuale negativo = priorità massima, per trasformarlo in max uso segno negativo
            heapq.heappush(
                heaps[drone.start_edge],
                (-drone.length, drone.release, drone.id),
            )
            waiting_index += 1
#nello stesso slot ogni arco puo essere usato da un solo drone
        moves: list[tuple[int, int]] = []
        for edge, heap in enumerate(heaps):
            if heap:
                _, _, drone_id = heapq.heappop(heap)
                moves.append((edge, drone_id))
#registro gli attraversamenti
        for _, drone_id in moves:
            schedule[drone_id].append(time)

        # Inserimento posticipato il drone potrà muoversi di nuovo a t+1.
        for _, drone_id in moves:
            drone = drones_by_id[drone_id]
            position = len(schedule[drone_id])
            if position < drone.length:
                next_edge = drone.edges[position]
                residual = drone.length - position
                heapq.heappush(
                    heaps[next_edge],
                    (-residual, time, drone_id),
                )

        time += 1

    validate_schedule(instance, schedule)
    return schedule
