from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import pandas as pd

from curve_import import ColumnMapping, read_curve_tables, validate_curve


COLUMNS = {"energy": "Energie", "yield": "Yield", "yield_err": "Incertitude"}


class CurveImportTest(unittest.TestCase):
    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def text_tables(self, name, content):
        path = self.root / name
        path.write_text(content, encoding="utf-8")
        return read_curve_tables(path, COLUMNS)

    def test_headerless_csv_keeps_first_point(self):
        table, = self.text_tables("curve.csv", "6400,10\n6399,20\n")
        self.assertEqual(table.mapping, ColumnMapping(0, 1))
        curve = validate_curve(table, table.mapping)
        self.assertEqual(curve.energies, [6399, 6400])
        self.assertEqual(curve.yields, [20, 10])
        self.assertEqual(curve.uncertainties, [0, 0])

    def test_three_headerless_columns_require_mapping(self):
        for name, delimiter in (("curve.csv", ","), ("curve.txt", "\t")):
            with self.subTest(name=name):
                table, = self.text_tables(name, delimiter.join(("1", "6400", "10")) + "\n")
                self.assertIsNone(table.mapping)
                curve = validate_curve(table, ColumnMapping(1, 2))
                self.assertEqual(curve.energies, [6400])

    def test_tab_delimited_missing_yield_does_not_shift_uncertainty(self):
        table, = self.text_tables("curve.txt", "Energie\tYield\tIncertitude\n6400\t\t1.2\n")
        self.assertEqual(table.mapping, ColumnMapping(0, 1, 2))
        with self.assertRaisesRegex(ValueError, "Row 2: Yield"):
            validate_curve(table, table.mapping)

    def test_text_import_keeps_comment_and_blank_line_support(self):
        table, = self.text_tables("curve.csv", "# run A\n6400,10 # first point\n\n6401,11\n")
        self.assertEqual(validate_curve(table, table.mapping).yields, [10, 11])
        table, = self.text_tables("curve.dat", "6400 10\n\n6401 11\n")
        self.assertEqual(validate_curve(table, table.mapping).yields, [10, 11])

    def test_known_columns_use_names_and_keep_uncertainty_aligned(self):
        table, = self.text_tables(
            "curve.csv", "Incertitude,extra,Yield,Energie\n1.2,x,10,6400\n2.3,y,20,6399\n"
        )
        curve = validate_curve(table, table.mapping)
        self.assertEqual(curve.yields, [20, 10])
        self.assertEqual(curve.uncertainties, [2.3, 1.2])

    def test_excel_finds_sheets_and_tables_without_requiring_uncertainty(self):
        path = self.root / "curve.xlsx"
        with pd.ExcelWriter(path, engine="openpyxl") as workbook:
            pd.DataFrame([["Notes"], ["Energie", "Yield"], [6400, 15], [],
                          ["Energie", "Yield"], [6401, 16]]).to_excel(
                workbook, sheet_name="Runs", header=False, index=False
            )
            pd.DataFrame([["Other energy", "Other yield"], [6402, 17]]).to_excel(
                workbook, sheet_name="Different layout", header=False, index=False
            )
        first, second, third = read_curve_tables(path, COLUMNS)
        self.assertEqual([(table.sheet, table.first_row) for table in (first, second, third)],
                         [("Runs", 2), ("Runs", 5), ("Different layout", 1)])
        self.assertEqual(validate_curve(second, second.mapping).uncertainties, [0])
        self.assertIsNone(third.mapping)
        self.assertEqual(validate_curve(third, ColumnMapping(0, 1)).yields, [17])

    def test_legacy_excel_selects_the_xls_engine(self):
        with patch("curve_import.pd.ExcelFile") as excel:
            workbook = excel.return_value.__enter__.return_value
            workbook.sheet_names = ["Legacy"]
            workbook.parse.return_value = pd.DataFrame([["Energie", "Yield"], [6400, 10]])
            table, = read_curve_tables(self.root / "curve.xls", COLUMNS)
        excel.assert_called_once_with(self.root / "curve.xls", engine="xlrd")
        self.assertEqual(validate_curve(table, table.mapping).yields, [10])

    def test_duplicate_headers_are_not_mapped_automatically(self):
        table, = self.text_tables("curve.csv", "Energie,Yield,Yield\n6400,10,20\n")
        self.assertIsNone(table.mapping)
        with self.assertRaisesRegex(ValueError, "different column"):
            validate_curve(table, ColumnMapping(0, 0))

    def test_invalid_values_report_the_source_row(self):
        for value, role in (("oops", "Yield"), ("inf", "Yield")):
            with self.subTest(value=value):
                table, = self.text_tables("curve.csv", f"Energie,Yield\n6400,10\n6401,{value}\n")
                with self.assertRaisesRegex(ValueError, f"Row 3: {role}"):
                    validate_curve(table, table.mapping)
        table, = self.text_tables("curve.csv", "Energie,Yield,Incertitude\n6400,10,-1\n")
        with self.assertRaisesRegex(ValueError, "Row 2: Uncertainty"):
            validate_curve(table, table.mapping)
