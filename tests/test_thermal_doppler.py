import json
from pathlib import Path
import tkinter as tk
import unittest
from unittest.mock import patch

import numpy as np

from hyproc.UI import GUI_App
from hyproc.calc_broadening import broadening, thermal_doppler_sd
from hyproc.class_models import Layer, Target
from hyproc.simulation import simulate
from hyproc.simulation_io import validate_temperature


def document():
    layer = {"areal_density": 20, "stopping": 0.1,
             "elements": [{"Z": 1, "percent_at": 100}]}
    return {"reaction": {"Z1": "1", "A1": "1", "Z2": "1", "A2": "1"},
            "resonance": {"E_R": 100, "Gamma": 1, "Sigma": 2},
            "options": {"offset": 0, "beam_width": 1, "straggling_model": "None",
                        "doppler": False, "standard_yield": 10, "manual_k_factor": "",
                        "target_temperature": "100", "standard_temperature": "0"},
            "target": {"layers": [layer]}, "standard": {"layers": [layer]},
            "simulated_curve": {"energy": [100]}, "experimental_curve": {"energy": []}}


class ThermalDopplerTest(unittest.TestCase):
    def test_width_and_absolute_zero(self):
        self.assertAlmostEqual(thermal_doppler_sd(100, 20, 1, 1), 0.0710802, places=6)
        self.assertEqual(thermal_doppler_sd(100, -273.15, 1, 1), 0)
        self.assertAlmostEqual(thermal_doppler_sd(100, 20, 4, 1), 2 * thermal_doppler_sd(100, 20, 1, 1))

    def test_quadrature(self):
        target = Target()
        target["layers"] = [Layer(document()["target"]["layers"][0])]
        kwargs = {"E_R": 100, "Gamma": 1, "sigma_R": 2, "Z1": 1}
        width = thermal_doppler_sd(100, 20, 1, 1)
        a = broadening(100, target, 3, False, "None", temperature_c=20, projectile_mass=1, target_mass=1, **kwargs)
        b = broadening(100, target, np.hypot(3, width), False, "None", **kwargs)
        np.testing.assert_allclose(a[1], b[1])
        np.testing.assert_allclose(a[2], b[2])

    def test_validation(self):
        self.assertEqual(validate_temperature("-273.15", "Target"), -273.15)
        for value in ("", "abc", "nan", "inf", -273.16, True):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "Target temperature"):
                validate_temperature(value, "Target")

    def test_separate_temperatures_defaults_and_manual_k(self):
        doc = document()
        x, y = np.array([0., 1., 2.]), np.ones(3)
        with patch("hyproc.simulation.calc_stopping.calc_stopping_cross_section", return_value=0.1), \
             patch("hyproc.simulation.calc_stopping.assign_stopping", side_effect=lambda t, *a, **k: t), \
             patch("hyproc.simulation.calc_curve.compute_yield", return_value=1), \
             patch("hyproc.simulation.calc_broadening.broadening", return_value=(0, x, y, [], 0)) as calc:
            simulate(doc)
            standard, target = [call.kwargs["temperature_c"] for call in calc.call_args_list]
            self.assertEqual(standard, 0)
            self.assertEqual(target, 100)
            self.assertGreater(calc.call_args.kwargs["projectile_mass"], 0)
            self.assertGreater(calc.call_args.kwargs["target_mass"], 0)
            calc.reset_mock()
            doc["options"].update(manual_k_factor="1", standard_temperature="bad")
            del doc["options"]["target_temperature"]
            simulate(doc)
            self.assertEqual(calc.call_args.kwargs["temperature_c"], 20)
            doc["options"]["target_temperature"] = "bad"
            with self.assertRaisesRegex(ValueError, "Target temperature"):
                simulate(doc)

    def test_gui_defaults_and_k_factor(self):
        path = Path("src/hyproc/settings.example.json").resolve()
        try:
            app = GUI_App(settings_path=path)
        except tk.TclError as error:
            self.skipTest(f"Tk display unavailable: {error}")
        self.addCleanup(app.destroy)
        app.withdraw()
        self.assertEqual(app.target_temperature_entry.get(), "20")
        self.assertEqual(app.standard_temperature_entry.get(), "20")
        app.manual_k_entry.insert(0, "1")
        app.on_manual_k_change()
        self.assertTrue(app.standard_temperature_entry.instate(["disabled"]))
        saved = app._simulation_document(json.loads(path.read_text(encoding="utf-8")))
        self.assertEqual(saved["options"]["standard_temperature"], "20")
        app.manual_k_entry.delete(0, tk.END)
        app.on_manual_k_change()
        self.assertFalse(app.standard_temperature_entry.instate(["disabled"]))
        self.assertEqual(app.standard_temperature_entry.get(), "20")

        saved["target"] = document()["target"]
        saved["standard"] = document()["standard"]
        saved.pop("reaction")
        saved.pop("resonance")
        saved["energy_range"] = {"minimum": 100, "maximum": 101, "step_size": 1}
        saved["options"].pop("target_temperature")
        saved["options"].pop("standard_temperature")
        app.target_temperature_entry.delete(0, tk.END)
        app.target_temperature_entry.insert(0, "75")
        with patch("hyproc.UI.filedialog.askopenfilename", return_value="simulation.json"), \
             patch("hyproc.UI.load_simulation", return_value=saved), \
             patch("hyproc.UI.messagebox.showerror") as error:
            app.load_simulation()
            error.assert_not_called()
            self.assertEqual(app.target_temperature_entry.get(), "20")
            self.assertEqual(app.standard_temperature_entry.get(), "20")
            saved["options"]["target_temperature"] = "-274"
            old_target = app.target
            app.load_simulation()
            error.assert_called_once()
            self.assertIs(app.target, old_target)
            self.assertEqual(app.target_temperature_entry.get(), "20")
