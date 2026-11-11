import json
from pathlib import Path
from tempfile import TemporaryDirectory
import tkinter as tk
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from curve_import import CurveTable
from dialog_import import CurveImportDialog

with patch("settings_config.ensure_settings", return_value=str(Path("settings.example.json").resolve())):
    from UI import GUI_App


class LoadCurveTest(unittest.TestCase):
    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.file = Path(directory.name) / "curve.csv"
        settings = Path(directory.name) / "settings.json"
        settings.write_text(json.dumps({"import_curve": {"columns": {
            "energy": "Energy", "yield": "Yield", "yield_err": "Uncertainty",
        }}}), encoding="utf-8")
        self.app = SimpleNamespace(
            settings_path=settings, exp_energy=[6300], ec_yield=[9], ec_yErr=[2],
            rescale_excitation_curve=Mock(),
        )

    def load(self, content, dialog_result=None):
        self.file.write_text(content, encoding="utf-8")
        with (patch("UI.filedialog.askopenfilename", return_value=str(self.file)),
              patch("UI.CurveImportDialog") as preview,
              patch("UI.messagebox.showerror") as error):
            preview.return_value.show.return_value = dialog_result
            GUI_App.load_curve(self.app)
        return preview, error

    def assert_previous_curve(self):
        self.assertEqual((self.app.exp_energy, self.app.ec_yield, self.app.ec_yErr), ([6300], [9], [2]))
        self.app.rescale_excitation_curve.assert_not_called()

    def test_recognized_layout_loads_without_preview(self):
        preview, error = self.load("Energy,Yield\n6401,8\n6400,4\n")
        preview.assert_not_called()
        error.assert_not_called()
        self.assertEqual((self.app.exp_energy, self.app.ec_yield, self.app.ec_yErr), ([6400, 6401], [4, 8], [0, 0]))
        self.app.rescale_excitation_curve.assert_called_once()

    def test_ambiguous_layout_preserves_previous_curve_when_cancelled(self):
        preview, error = self.load("1,6400,8\n2,6401,9\n")
        preview.assert_called_once()
        self.assertEqual(preview.call_args.args[2], str(self.file))
        preview.return_value.show.assert_called_once()
        error.assert_not_called()
        self.assert_previous_curve()

    def test_validation_failure_preserves_previous_curve(self):
        preview, error = self.load("Energy,Yield\n6400,invalid\n")
        preview.assert_not_called()
        self.assertIn("Row 2: Yield", error.call_args.args[1])
        self.assert_previous_curve()


class CurvePreviewTest(unittest.TestCase):
    def test_preview_selects_sheet_table_and_distinct_columns(self):
        try:
            root = tk.Tk()
        except tk.TclError as error:
            self.skipTest(f"Tk display unavailable: {error}")
        self.addCleanup(root.destroy)
        root.withdraw()
        headers = ("Index", "Energy", "Yield")
        tables = [
            CurveTable("First", 1, headers, ((2, (1, 6300, 3)),), None, True),
            CurveTable("Second", 1, headers, ((2, (1, 6400, 4)),), None, True),
            CurveTable("Second", 5, headers, ((6, (1, 6401, 6)),), None, True),
        ]
        dialog = CurveImportDialog(root, tables, str(Path("measurements") / "sample.xlsx"))
        self.assertEqual(dialog.title(), "Import Excitation Curve — sample.xlsx")
        dialog.sheet_picker.current(1)
        dialog._select_sheet()
        dialog.table_picker.current(1)
        dialog._select_table()
        item, = dialog.samples.get_children()
        self.assertEqual(tuple(map(int, dialog.samples.item(item, "values"))), (6, 1, 6401, 6))
        self.assertEqual(dialog.samples.heading("source_row", "text"), "Source row")
        self.assertEqual(dialog.samples.heading("data_0", "text"), "Column 1: Index")
        self.assertEqual(dialog.energy_picker["values"][1:], (
            "Column 1: Index", "Column 2: Energy", "Column 3: Yield",
        ))

        dialog.energy_picker.current(2)
        dialog.yield_picker.current(2)
        with patch("dialog_import.messagebox.showerror") as error:
            dialog._confirm()
        self.assertIsNone(dialog.result)
        self.assertIn("different column", error.call_args.args[1])
        dialog.yield_picker.current(3)
        dialog._confirm()
        self.assertEqual(dialog.result.energies, [6401])
        self.assertEqual(dialog.result.yields, [6])
        self.assertEqual(dialog.result.uncertainties, [0])
