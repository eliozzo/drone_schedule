"""Strutture dati condivise dagli algoritmi."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)#frozen rende l'oggetto immutabile
class Drone:
    """Un drone che percorre un sottocammino del path graph."""

    id: int
    start_edge: int#primo arco
    length: int#num archi da attraversare
    release: int#slot iniziale
    direction: int = 1#1 sx->dx, -1 dx->sx

    def __post_init__(self) -> None:
        if self.start_edge < 0 or self.length < 1 or self.release < 1:
            raise ValueError("Parametri del drone non validi")
        if self.direction not in (-1, 1):
            raise ValueError("direction deve essere -1 oppure 1")

    @property#il cammino non viene memorizzato esplicitamente ma calcolato a partire da pos,lung e direz
    def edges(self) -> tuple[int, ...]:
        return tuple(
            self.start_edge + self.direction * step
            for step in range(self.length)
        )

    @property
    def last_edge(self) -> int:
        return self.edges[-1]


@dataclass(frozen=True)
class Instance:
    """Istanza DPSP su un path graph con m archi numerati da 0 a m-1."""

    m: int
    drones: tuple[Drone, ...]
    bidirectional: bool = False

    def __post_init__(self) -> None:
        if self.m < 1:
            raise ValueError("m deve essere positivo")
        ids = [drone.id for drone in self.drones]
        if len(ids) != len(set(ids)):
            raise ValueError("Gli id dei droni devono essere unici")
        for drone in self.drones:
            if any(edge < 0 or edge >= self.m for edge in drone.edges):
                raise ValueError(f"Il cammino del drone {drone.id} esce dal grafo")
            if not self.bidirectional and drone.direction != 1:
                raise ValueError("Un'istanza unidirezionale accetta solo direction=1")


Schedule = dict[int, list[int]]#dizionario drone_id:[slot_primo_arco,slot_secondo_arco]
#es 0:[2,3,5]-> significa che il drone 0 percorre i suoi 3 archi agli slot 2,3 e 5


def makespan(schedule: Schedule) -> int:
    return max((time for times in schedule.values() for time in times), default=0)


def validate_schedule(instance: Instance, schedule: Schedule) -> None:
    """Solleva ValueError se lo schedule non è ammissibile."""

    if set(schedule) != {drone.id for drone in instance.drones}:
        raise ValueError("Lo schedule non contiene esattamente tutti i droni")

    occupied: set[tuple[int, int]] = set()
    for drone in instance.drones:
        times = schedule[drone.id]
        if len(times) != drone.length:
            raise ValueError(f"Schedule incompleto per il drone {drone.id}")#ogni drone ha uno slot per ciascun arco
        if times[0] <= drone.release:
            raise ValueError(f"Release time violato dal drone {drone.id}")#devo attraversare dopo la release
        if any(right <= left for left, right in zip(times, times[1:])):
            raise ValueError(f"Ordine del cammino violato dal drone {drone.id}")#strettamente crescenti
        for edge, time in zip(drone.edges, times):
            key = (edge, time)
            if key in occupied:
                raise ValueError(f"Conflitto sull'arco {edge} al tempo {time}")
            occupied.add(key)
