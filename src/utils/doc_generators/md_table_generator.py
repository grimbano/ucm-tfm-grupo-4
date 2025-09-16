
from typing import Any, Dict, List


def convert_to_markdown_table(data: List[Dict[str, Any]]) -> str:
    """
    Converts a list of dictionaries into a Markdown table string.

    Args:
        data: A list of dictionaries, where each dictionary represents a row
                and keys are column headers.

    Returns:
        A string representing the data as a Markdown table.
        Returns an empty string if the input list is empty.
    """
    if not data:
        return ""

    headers = list(data[0].keys())

    header_row = "| " + " | ".join(headers) + " |"
    separator_row = "|---" * len(headers) + "|"

    data_rows = []
    for row in data:
        values = [str(row.get(header, '')) for header in headers]
        data_row = "| " + " | ".join(values) + " |"
        data_rows.append(data_row)

    return "\n".join([header_row, separator_row] + data_rows)