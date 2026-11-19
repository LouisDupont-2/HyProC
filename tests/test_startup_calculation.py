import json
from pathlib import Path
import tkinter as tk
import unittest

from hyproc.UI import GUI_App


class StartupCalculationTest(unittest.TestCase):
    def test_fresh_app_builds_calculation_document(self):
        settings_path = Path("src/hyproc/settings.example.json").resolve()
        try:
            app = GUI_App(settings_path=settings_path)
        except tk.TclError as error:
            self.skipTest(f"Tk display unavailable: {error}")
        self.addCleanup(app.destroy)
        app.withdraw()
        settings = json.loads(settings_path.read_text(encoding="utf-8"))
        document = app._simulation_document(settings)
        self.assertEqual(document["options"]["manual_k_factor"], "")
