import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from hyproc.UI import GUI_App
from hyproc.class_models import Target
from hyproc.simulation_io import make_target, save_simulation


class ChiTargetHistoryTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.settings_path = Path(self.temp.name) / "settings.json"
        self.settings_path.write_text(Path("src/hyproc/settings.example.json").read_text(encoding="utf-8"), encoding="utf-8")
        self.app = GUI_App(settings_path=self.settings_path)
        self.app.withdraw()

    def tearDown(self):
        self.app.destroy()
        self.temp.cleanup()

    def click(self, row, x=0):
        _, y = self.app.ax1.transData.transform((0, row))
        self.app.on_chi_history_click(SimpleNamespace(button=1, x=x, y=y))

    def test_scrolled_row_click_cancel_restore_and_independence(self):
        app = self.app
        app.chi_val = list(range(12))
        app.chi_energy_bounds_history = [None] * 12
        app.chi_target_history = [make_target(Target()) for _ in range(12)]
        app.chi_target_history[6]["layers"][0]["areal_density"] = 456
        app.start_ctr = 2
        app.update_chi_plot()
        self.assertEqual(app.ax1.get_yticklabels()[4].get_text(), "7")
        with patch("hyproc.UI.messagebox.askyesno", return_value=False):
            self.click(4, x=0)
        self.assertNotEqual(app.target["layers"][0]["areal_density"], 456)
        with patch("hyproc.UI.messagebox.askyesno", return_value=True) as confirm:
            self.click(4, x=0)
        self.assertIn("calculation 7", confirm.call_args.args[1])
        self.assertEqual(app.target["layers"][0]["areal_density"], 456)
        app.target["layers"][0]["areal_density"] = 123
        self.assertEqual(app.chi_target_history[6]["layers"][0]["areal_density"], 456)

    def test_round_trip_legacy_invalid_and_reset(self):
        app = self.app
        app.chi_val = [1.0]
        app.chi_energy_bounds_history = [None]
        app.chi_target_history = [make_target(app.target)]
        settings = json.loads(self.settings_path.read_text(encoding="utf-8"))
        document = app._simulation_document(settings)
        document["options"]["track_target_changes"] = True  # Legacy files remain loadable.
        path = Path(self.temp.name) / "simulation.json"

        def load():
            with patch("hyproc.UI.filedialog.askopenfilename", return_value=str(path)):
                app.load_simulation()

        save_simulation(path, document)
        app.chi_target_history = []
        load()
        self.assertEqual(len(app.chi_target_history), 1)
        self.assertEqual(app.chi_target_history[0], app.target)
        self.assertFalse(app._simulation_document(settings)["options"]["track_target_changes"])
        del document["chi_squared_targets"]
        save_simulation(path, document)
        load()
        self.assertEqual(app.chi_target_history, [None])
        with patch("hyproc.UI.messagebox.showinfo") as info:
            self.click(0)
        info.assert_called_once_with("Restore target", "No target was saved for calculation 1.")
        document["chi_squared_targets"] = [{"layers": []}]
        save_simulation(path, document)
        original = app.target
        with patch("hyproc.UI.messagebox.showerror") as error:
            load()
        error.assert_called_once()
        self.assertIs(app.target, original)
        app.reset_chi_history()
        self.assertEqual(app.chi_target_history, [])

    def test_calculation_records_independent_target(self):
        app = self.app
        settings = json.loads(self.settings_path.read_text(encoding="utf-8"))
        settings["save_path"] = self.temp.name
        self.settings_path.write_text(json.dumps(settings), encoding="utf-8")
        app.sim_energy = [100.0]
        app.exp_energy = [100.0]
        app.ec_yield = [1.0]
        result = SimpleNamespace(standard_stopping=None, normalization_factor=1, energy=[100.0], yield_values=[1.0])
        with patch("hyproc.UI._simulate", return_value=result) as simulate, \
             patch.object(app, "_get_stopping_model", return_value="SCS-25-Solid"), \
             patch.object(app, "update_exc_plot"), \
             patch("hyproc.UI.calc_curve.chi_squared_test", return_value=0.0):
            app.Calculation()
        self.assertEqual(len(app.chi_target_history), 1)
        self.assertEqual(app.chi_target_history[0], simulate.call_args.args[0]["target"])
        app.target["layers"][0]["areal_density"] = 42
        self.assertNotEqual(app.chi_target_history[0]["layers"][0]["areal_density"], 42)


if __name__ == "__main__":
    unittest.main()
