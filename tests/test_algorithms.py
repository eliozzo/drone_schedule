import unittest

from algoritmi.heap_based import heap_based
from algoritmi.ilp import solve_ilp
from algoritmi.models import Drone, Instance, makespan, validate_schedule
from algoritmi.rec import rec
from experimental_setting.generator import generate_instance


class AlgorithmTests(unittest.TestCase):
    def test_paper_like_unidirectional_instance(self) -> None:
        instance = Instance(
            m=5,
            drones=(
                Drone(0, 0, 3, 2),
                Drone(1, 0, 1, 1),
                Drone(2, 1, 2, 1),
                Drone(3, 0, 5, 1),
            ),
        )
        _, optimum = solve_ilp(instance)
        rec_schedule = rec(instance)
        heap_schedule = heap_based(instance)
        validate_schedule(instance, rec_schedule)
        validate_schedule(instance, heap_schedule)
        self.assertEqual(makespan(rec_schedule), optimum)
        self.assertEqual(makespan(heap_schedule), optimum)

    def test_random_unidirectional_algorithms_match_ilp(self) -> None:
        for seed in range(8):
            instance = generate_instance(5, 7, bidirectional=False, seed=seed)
            _, optimum = solve_ilp(instance)
            self.assertEqual(makespan(rec(instance)), optimum)
            self.assertEqual(makespan(heap_based(instance)), optimum)

    def test_bidirectional_heap_is_feasible(self) -> None:
        instance = generate_instance(7, 9, bidirectional=True, seed=42)
        schedule = heap_based(instance)
        validate_schedule(instance, schedule)

    def test_bidirectional_directions_are_valid(self) -> None:
        instance = generate_instance(20, 10, bidirectional=True, seed=7)
        self.assertTrue({d.direction for d in instance.drones} <= {-1, 1})
        for drone in instance.drones:
            self.assertTrue(all(0 <= edge < instance.m for edge in drone.edges))


if __name__ == "__main__":
    unittest.main()
