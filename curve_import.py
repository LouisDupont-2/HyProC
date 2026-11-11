"""Read experimental curve tables without changing the loaded HyProC curve."""

import csv
from dataclasses import dataclass
import math
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class ColumnMapping:
    energy: int
    yield_: int
    uncertainty: int | None = None


@dataclass(frozen=True)
class CurveTable:
    sheet: str
    first_row: int
    headers: tuple[str, ...]
    rows: tuple[tuple[int, tuple], ...]
    mapping: ColumnMapping | None
    has_header: bool

    def value(self, row: tuple, column: int):
        return row[column] if column < len(row) else None


@dataclass(frozen=True)
class ExperimentalCurve:
    energies: list[float]
    yields: list[float]
    uncertainties: list[float]


def _blank(value):
    return value is None or (isinstance(value, str) and not value.strip()) or pd.isna(value)


def _numeric(value):
    try:
        float(value)
    except (TypeError, ValueError, OverflowError):
        return False
    return True


def _label(value):
    return "" if _blank(value) else str(value).strip()


def _matching_columns(row, names):
    labels = [_label(value).casefold() for value in row]
    return {
        role: [i for i, label in enumerate(labels) if label and label == name]
        for role, name in names.items()
    }


def _configured_header(row, names):
    matches = _matching_columns(row, names)
    return bool(matches["energy"] and matches["yield"])


def _guess_header(block):
    if len(block) < 2:
        return False
    first = block[0][1]
    following = block[1][1]
    return sum(not _blank(value) and not _numeric(value) for value in first) >= 2 and (
        not any(_numeric(value) for value in first)
        and sum(_numeric(value) for value in following) >= 2
    )


def _table(sheet, block, names):
    first_row, first = block[0]
    configured = _configured_header(first, names)
    has_header = configured or _guess_header(block)
    rows = block[1:] if has_header else block
    if not configured and not any(sum(_numeric(value) for value in row) >= 2 for _, row in rows):
        return None
    width = max(len(row) for _, row in block)
    headers = tuple(_label(first[i]) if has_header and i < len(first) else "" for i in range(width))
    mapping = None
    if configured:
        matches = _matching_columns(first, names)
        energy, yields, uncertainty = (matches[role] for role in ("energy", "yield", "yield_err"))
        if len(energy) == len(yields) == 1 and len(uncertainty) <= 1:
            indices = energy + yields + uncertainty
            if len(set(indices)) == len(indices):
                mapping = ColumnMapping(*indices)
    elif not has_header and width == 2:
        mapping = ColumnMapping(0, 1)
    return CurveTable(sheet, first_row, headers, tuple(rows), mapping, has_header)


def _tables_in_sheet(sheet, rows, names):
    block = []
    for line_number, raw in rows:
        row = list(raw)
        while row and _blank(row[-1]):
            row.pop()
        if block and (not row or _configured_header(row, names)):
            table = _table(sheet, block, names)
            if table is not None:
                yield table
            block = []
        if row:
            block.append((line_number, tuple(row)))
    if block:
        table = _table(sheet, block, names)
        if table is not None:
            yield table


def _text_rows(stream, extension):
    if extension == ".csv":
        reader = csv.reader(stream, strict=True)
        while True:
            first_line = reader.line_num + 1
            row = next(reader, None)
            if row is None:
                return
            for i, value in enumerate(row):
                value, comment, _ = value.partition("#")
                if comment:
                    row = [*row[:i], value]
                    break
            if any(value.strip() for value in row):
                yield first_line, row
    else:
        for number, line in enumerate(stream, 1):
            content, _, _ = line.partition("#")
            if content.strip():
                if "\t" in content:
                    # Keep empty cells so later values stay in their columns.
                    yield number, content.rstrip("\r\n").split("\t")
                else:
                    yield number, content.split()


def read_curve_tables(filename, columns):
    """Find candidate tables and propose mappings for recognizable layouts."""
    path = Path(filename)
    extension = path.suffix.lower()
    names = {role: columns[role].strip().casefold() for role in ("energy", "yield", "yield_err")}
    tables = []
    try:
        if extension in (".xls", ".xlsx"):
            engine = "xlrd" if extension == ".xls" else "openpyxl"
            try:
                with pd.ExcelFile(path, engine=engine) as workbook:
                    sheets = [(sheet, workbook.parse(sheet, header=None, dtype=object, keep_default_na=False))
                              for sheet in workbook.sheet_names]
            except OSError:
                raise
            except Exception as error:
                # Excel engines expose different exceptions for malformed workbooks.
                raise ValueError(f"Cannot read workbook {path.name}: {error}") from error
            for sheet, data in sheets:
                rows = enumerate(data.itertuples(index=False, name=None), 1)
                tables.extend(_tables_in_sheet(sheet, rows, names))
        else:
            with path.open(encoding="utf-8-sig", newline="") as stream:
                tables.extend(_tables_in_sheet(path.name, _text_rows(stream, extension), names))
    except (ImportError, csv.Error, UnicodeError) as error:
        raise ValueError(f"Cannot read {path.name}: {error}") from error
    if not tables:
        raise ValueError("No table with energy and yield data was found.")
    return tables


def _number(value, role, row):
    try:
        if isinstance(value, bool):
            raise ValueError
        number = float(value)
        if not math.isfinite(number) or (role == "Uncertainty" and number < 0):
            raise ValueError
    except (TypeError, ValueError, OverflowError) as error:
        expected = "a finite, non-negative number" if role == "Uncertainty" else "a finite number"
        raise ValueError(f"Row {row}: {role} must be {expected}.") from error
    return number


def validate_curve(table, mapping):
    """Return sorted, aligned measurements after validating every selected row."""
    selected = [mapping.energy, mapping.yield_]
    if mapping.uncertainty is not None:
        selected.append(mapping.uncertainty)
    if len(set(selected)) != len(selected) or any(not 0 <= i < len(table.headers) for i in selected):
        raise ValueError("Choose a different column for each field.")
    if not table.rows:
        raise ValueError("The selected table has no data rows.")

    points = []
    for number, row in table.rows:
        energy = _number(table.value(row, mapping.energy), "Energy", number)
        yield_ = _number(table.value(row, mapping.yield_), "Yield", number)
        raw_uncertainty = None if mapping.uncertainty is None else table.value(row, mapping.uncertainty)
        uncertainty = 0.0 if _blank(raw_uncertainty) else _number(raw_uncertainty, "Uncertainty", number)
        points.append((energy, yield_, uncertainty))
    points.sort(key=lambda point: point[0])
    return ExperimentalCurve(*(list(values) for values in zip(*points)))
