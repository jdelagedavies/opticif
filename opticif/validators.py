"""
This module provides functionality for validating the structure of CSV files used in the CIF optimization and DSM matrix
conversion processes.
"""

import csv
from pathlib import Path
from typing import Union


class CSVStructureError(Exception):
    """Custom exception for CSV file structure errors."""


def validate_node_csv_structure(
    csv_path: Union[str, Path], csv_delimiter: str = ";"
) -> None:
    """
    Checks if the node CSV file structure is valid and contains a non-empty "name" column with no duplicates and no empty
    values.

    Args:
        csv_path (Union[str, Path]): The path to the node CSV file to validate.
        csv_delimiter (str): The csv_delimiter used in the CSV file. Defaults to ";".

    Raises: CSVStructureError: If the node CSV file does not contain a "name" column, contains duplicate names,
    or contains empty values.
    """
    # Check if the CSV file contains a "name" column
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f, delimiter=csv_delimiter)
        if "name" not in reader.fieldnames:
            raise CSVStructureError(
                f"{csv_path} should have a header with a 'name' column."
            )

        # Check if the "name" column contains duplicates or empty values
        names = set()
        for row in reader:
            name = row["name"].strip()
            if not name:
                raise CSVStructureError(
                    f"'{csv_path}' contains an empty value in the 'name' column."
                )
            if name in names:
                raise CSVStructureError(
                    f"'{csv_path}' contains duplicate names in the 'name' column."
                )

            names.add(name)


def validate_matrix_csv_structure(
    matrix_path: Union[str, Path], csv_delimiter: str = ";"
) -> None:
    """
    Checks if the matrix CSV file structure is valid, is square, and is binary (only uses 1s and 0s).

    Args:
        matrix_path (Union[str, Path]): The path to the matrix CSV file to validate.
        csv_delimiter (str): The csv_delimiter used in the CSV file. Defaults to ";".

    Raises:
        CSVStructureError: If the matrix CSV file is not square, is not binary or has any formatting issues.
    """
    with open(matrix_path, "r", encoding="utf-8-sig") as f:
        matrix = list(csv.reader(f, delimiter=csv_delimiter))

    row_count = len(matrix)

    for i, row in enumerate(matrix):
        if len(row) != row_count:
            raise CSVStructureError(
                f"The matrix in '{matrix_path}' is not square. Each row should have the same number of elements as "
                f"the number of rows."
            )

        for j, element in enumerate(row):
            if element not in ["0", "1"]:
                raise CSVStructureError(
                    f"The matrix in '{matrix_path}' is not binary. Found '{element}' at row {i+1}, column {j+1}."
                )