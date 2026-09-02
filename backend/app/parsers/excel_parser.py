import pandas as pd
import io
from typing import List, Tuple, Optional
from app.models.schemas import ParsedTransaction
from app.parsers.csv_parser import parse_csv_content

def get_excel_sheet_names(content_bytes: bytes) -> List[str]:
    """Inspects Excel workbook and returns list of sheet names."""
    try:
        excel_file = pd.ExcelFile(io.BytesIO(content_bytes))
        return excel_file.sheet_names
    except Exception:
        return ["Sheet1"]

def parse_excel_content(
    content_bytes: bytes,
    sheet_name: Optional[str] = None,
    filename: str = "upload.xlsx",
    db = None
) -> Tuple[List[ParsedTransaction], List[str], List[str]]:
    """
    Parses Excel content into normalized ParsedTransaction list.
    Returns (transactions, warnings, available_sheet_names).
    """
    warnings: List[str] = []
    sheet_names: List[str] = []

    try:
        excel_file = pd.ExcelFile(io.BytesIO(content_bytes))
        sheet_names = excel_file.sheet_names

        selected_sheet = sheet_name if (sheet_name and sheet_name in sheet_names) else sheet_names[0]

        df = pd.read_excel(excel_file, sheet_name=selected_sheet)
    except Exception as e:
        warnings.append(f"Failed to read Excel workbook: {str(e)}")
        return [], warnings, []

    if df.empty:
        warnings.append(f"Sheet '{selected_sheet}' is empty.")
        return [], warnings, sheet_names

    # Convert dataframe to CSV string buffer and reuse parse_csv_content logic for consistency
    csv_buf = io.StringIO()
    df.to_csv(csv_buf, index=False)
    csv_bytes = csv_buf.getvalue().encode('utf-8')

    transactions, parse_warnings = parse_csv_content(csv_bytes, filename=filename, db=db)

    # Set source to 'excel'
    for tx in transactions:
        tx.source = "excel"

    warnings.extend(parse_warnings)
    return transactions, warnings, sheet_names
