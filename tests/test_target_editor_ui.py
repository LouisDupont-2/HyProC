import tkinter as tk
from tkinter import ttk
from unittest.mock import Mock

from hyproc.UI_geometry import TargetEditorTab


def test_shared_tabs_have_matching_layout_and_standard_layer_controls_disabled():
    root = tk.Tk()
    root.withdraw()
    try:
        app = Mock()
        target = TargetEditorTab(ttk.Frame(root), app)
        standard = TargetEditorTab(ttk.Frame(root), app, standard=True)

        def shape(widget):
            return (widget.winfo_class(), tuple(shape(child) for child in widget.winfo_children()))

        assert shape(target.target_frame) == shape(standard.target_frame)
        assert target.layer_listbox.cget('state') == 'normal'
        assert standard.layer_listbox.cget('state') == 'disabled'
        assert not target.AD_entry.instate(['disabled'])
        assert standard.AD_entry.instate(['disabled'])
        for name in ('add_layer_button', 'remove_layer_button', 'up_button', 'down_button', 'duplicate_button'):
            assert not getattr(target, name).instate(['disabled'])
            button = getattr(standard, name)
            assert button.instate(['disabled'])
            button.invoke()
        app.on_add_layer_click.assert_not_called()
        standard.add_element_button.invoke()
        target.add_element_button.invoke()
        assert app.on_add_element_click.call_args_list == [
            (( ), {'target_type': 'std'}), ((), {})
        ]
        assert not standard.element_Z_entry.instate(['disabled'])
        assert not standard.composition_percent_entry.instate(['disabled'])
    finally:
        root.destroy()


def test_standard_layer_display_and_controls_survive_manual_k_toggle():
    from pathlib import Path
    from hyproc.UI import GUI_App

    app = GUI_App(settings_path=Path('src/hyproc/settings.example.json').resolve())
    app.withdraw()
    try:
        def check_standard():
            layer = app.std_target['layers'][0]
            assert app.Std_layer_listbox.size() == 1
            assert str(layer['areal_density']) in app.Std_layer_listbox.get(0)
            assert app.Std_AD_entry.get() == str(layer['areal_density'])
            assert app.Std_layer_listbox.cget('state') == 'disabled'
            assert app.Std_AD_entry.instate(['disabled'])
            for name in ('add_layer_button', 'remove_layer_button', 'up_button', 'down_button', 'duplicate_button'):
                assert getattr(app, 'Std_' + name).instate(['disabled'])
            assert not app.Std_add_element_button.instate(['disabled'])

        assert app.std_target['layers'][0]['areal_density'] == 1500.0
        assert app.Std_AD_entry.get() == '1500.0'
        check_standard()
        app.manual_k_entry.insert(0, '1')
        app.on_manual_k_change()
        app.manual_k_entry.delete(0, tk.END)
        app.on_manual_k_change()
        app.std_target['layers'][0]['areal_density'] = 1500
        app.refresh_Std_list()
        check_standard()
    finally:
        app.destroy()
