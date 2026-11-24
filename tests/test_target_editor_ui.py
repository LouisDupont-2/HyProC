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
