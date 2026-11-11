import re
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.cell import Cell
from openpyxl.worksheet.worksheet import Worksheet

from .strings import normalize_cyrillic


SNILS_PATTERN = re.compile(r"\d{3}-\d{3}-\d{3} \d{2}")


def build_snils_map(
    workbook_path:      str | Path,
    name_column_index:  int = 0,
    snils_column_index: int = 6,
    header_row_index:   int = 8,
    data_offset:        int = 2
) -> dict[str, str]:
    """
    Maps each employee's name to their SNILS by parsing the Excel workbook.

    :param workbook_path: Path to the Excel file.
    :type workbook_path: str | Path

    :param name_column_index: Column index for the employee name.
    :type name_column_index: int

    :param snils_column_index: Column index for the SNILS.
    :type snils_column_index: int

    :param header_row_index: Row index containing the headers.
    :type header_row_index: int

    :param data_offset: Number of rows after the header row where data starts.
    :type data_offset: int

    :return: Dictionary mapping names to SNILSes.
    :rtype: dict[str, str]
    """
    if name_column_index < 0:
        raise ValueError(f"Invalid name column index: {name_column_index}")

    if snils_column_index < 0:
        raise ValueError(f"Invalid snils column index: {snils_column_index}")

    book = load_workbook(workbook_path)
    sheet: Worksheet = book._sheets[0]
    rows: list[tuple[Cell, ...]] = list(sheet)

    if header_row_index >= len(rows):
        raise ValueError(
            f"Header row {header_row_index+1} "
            f"does not exist in file {Path(workbook_path).name!r}"
        )

    file_name = Path(workbook_path).name

    result: dict[str, str] = {}
    for row_no, row in enumerate(rows[header_row_index + data_offset:], start=1):
        name  = _validate_name (file_name, row_no, row[name_column_index ])
        snils = _validate_snils(file_name, row_no, row[snils_column_index])

        result[name] = snils

    return result


def _validate_snils(file_name: str, row_no: int, cell: Cell):
    snils = str(cell.value or "").strip()

    if not snils:
        raise ValueError(f"Empty SNILS {cell.value!r} at row {row_no} in file {file_name!r}")

    if not SNILS_PATTERN.fullmatch(snils):
        raise ValueError(f"Invalid SNILS {cell.value!r} at row {row_no} in file {file_name!r}")

    return snils


def _validate_name(file_name: str, row_no: int, cell: Cell):
    name = normalize_cyrillic(str(cell.value or ""))

    if not name:
        raise ValueError(f"Empty employee name {cell.value!r} at row {row_no} in file {file_name!r}")

    return name
