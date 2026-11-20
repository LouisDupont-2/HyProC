import unittest
from unittest.mock import patch

import numpy as np

from hyproc.calc_curve import compute_yield
from hyproc.calc_broadening import broadening
from hyproc.class_models import Layer, Target
from hyproc.simulation import simulate
from hyproc.simulation_io import validate_physics


REACTION = {"Z1": "1", "A1": "1", "Z2": "1", "A2": "1"}
RESONANCE = {"E_R": 100.0, "Gamma": 1.0, "Sigma": 2.0}


def target(thickness, fraction):
    return {"layers": [{"areal_density": thickness, "stopping": 0.1,
                        "elements": [{"Z": 1, "percent_at": fraction},
                                     {"Z": 14, "percent_at": 100 - fraction}]}]}


class OffResonanceTest(unittest.TestCase):
    def test_baseline_covers_layers_beyond_grid(self):
        sample = Target()
        sample["layers"] = [Layer(target(100, 20)["layers"][0]), Layer(target(200, 50)["layers"][0])]
        x = np.array([0.0, 1.0, 2.0])
        y = np.zeros(3)
        self.assertEqual(compute_yield(sample, x, y, 1), 0.0)
        self.assertAlmostEqual(compute_yield(sample, x, y, 1, 0.01), 120.0)

    def test_validation_defaults_and_rejects_invalid_baseline(self):
        self.assertEqual(validate_physics(REACTION, RESONANCE)[1]["Off-resonance"], 0.0)
        for value in (-1, float("nan"), float("inf"), "invalid"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_physics(REACTION, {**RESONANCE, "Off-resonance": value})

    def test_real_broadening_keeps_resonance_unchanged(self):
        sample = Target()
        sample["layers"] = [Layer(target(2000, 100)["layers"][0])]
        args = (100.0, sample, 1.0, False, "None")
        kwargs = {"E_R": 100.0, "Gamma": 1.0, "sigma_R": 2.0, "Z1": 1}
        _, x, y, _, _ = broadening(*args, **kwargs)
        _, xb, yb, _, _ = broadening(*args, **kwargs, off_resonance=0.01)
        np.testing.assert_array_equal(x, xb)
        np.testing.assert_array_equal(y, yb)
        self.assertAlmostEqual(compute_yield(sample, xb, yb, 1, 0.01) -
                               compute_yield(sample, x, y, 1), 2000.0)

    def test_baseline_in_standard_normalization_and_target(self):
        simulation = {
            "reaction": REACTION, "resonance": {**RESONANCE, "Off-resonance": 0.01},
            "options": {"offset": 0, "beam_width": 1, "stopping_model": "SCS-25-Solid",
                        "straggling_model": "None", "doppler": False, "manual_k_factor": "",
                        "standard_yield": 10},
            "standard": target(10, 100), "target": target(20, 50),
            "simulated_curve": {"energy": [100]}, "experimental_curve": {"energy": []},
        }
        x, y = np.array([0., 1., 2.]), np.zeros(3)
        with patch("hyproc.simulation.calc_stopping.calc_stopping_cross_section", return_value=0.1), \
             patch("hyproc.simulation.calc_stopping.assign_stopping", side_effect=lambda t, *a, **k: t), \
             patch("hyproc.simulation.calc_broadening.broadening", return_value=(0, x, y, [], 0)) as broadening:
            result = simulate(simulation)
        self.assertAlmostEqual(result.normalization_factor, 1.0)
        self.assertAlmostEqual(result.yield_values[0], 10.0)
        self.assertEqual(broadening.call_count, 2)
        self.assertTrue(all(call.kwargs["off_resonance"] == 0.01 for call in broadening.call_args_list))


if __name__ == "__main__":
    unittest.main()
