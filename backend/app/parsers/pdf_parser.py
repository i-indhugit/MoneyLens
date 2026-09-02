import pdfplumber
import pypdf
import io
import re
from datetime import datetime
from typing import List, Tuple, Dict, Any, Optional
from app.models.schemas import ParsedTransaction
from app.categorization.engine import categorize_description

# Header and footer keywords to ignore
IGNORE_KEYWORDS = [
    "account statement", "statement of account", "opening balance", "closing balance",
    "page ", "branch", "ifsc", "account number", "account no", "cheque no",
    "transaction details", "date particulars", "total debit", "total credit",
    "customer id", "statement period", "confidential", "bank"
]

# Regex patterns for common date formats in bank statements
DATE_PATTERNS = [
    r'(\d{2}[-/.]\d{2}[-/.]\d{4})',       # 15-03-2026 or 15/03/2026
    r'(\d{4}[-/.]\d{2}[-/.]\d{2})',       # 2026-03-15
    r'(\d{2}[-/\s]\w{3}[-/\s]\d{4})',      # 15-Mar-2026 or 15 Mar 2026
    r'(\w{3}\s\d{2},\s\d{4})'             # Mar 15, 2026
]

class BaseBankParser:
    """Base extensible class for bank statement parsing."""
    bank_name = "Generic Bank Parser"

    def can_parse(self, text_sample: str) -> bool:
        return True

    def parse(self, pdf_bytes: bytes, db = None) -> Tuple[List[ParsedTransaction], List[str], float]:
        raise NotImplementedError

class GenericPDFStatementParser(BaseBankParser):
    bank_name = "Generic Multi-Bank PDF Parser"

    def parse(self, pdf_bytes: bytes, db = None) -> Tuple[List[ParsedTransaction], List[str], float]:
        warnings: List[str] = []
        parsed_txs: List[ParsedTransaction] = []

        raw_tables_extracted = False
        text_lines: List[str] = []

        try:
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                for page_idx, page in enumerate(pdf.pages):
                    # Try table extraction first
                    tables = page.extract_tables()
                    if tables and len(tables) > 0:
                        for table in tables:
                            if not table or len(table) < 2:
                                continue
                            headers = [str(cell).strip().lower() if cell else "" for cell in table[0]]
                            for row in table[1:]:
                                if not row or all(not cell for cell in row):
                                    continue
                                row_str = " ".join([str(c).strip() for c in row if c])
                                # Skip header or balance summary rows
                                if any(k in row_str.lower() for k in IGNORE_KEYWORDS):
                                    continue
                                tx = self._try_parse_line(row_str, idx=len(parsed_txs), page=page_idx, db=db)
                                if tx:
                                    parsed_txs.append(tx)
                                    raw_tables_extracted = True

                    # Also collect text lines as fallback
                    page_text = page.extract_text()
                    if page_text:
                        for line in page_text.split("\n"):
                            line_str = line.strip()
                            if line_str and not any(k in line_str.lower() for k in IGNORE_KEYWORDS):
                                text_lines.append(line_str)

        except Exception as e:
            warnings.append(f"pdfplumber extraction error: {str(e)}. Attempting PyPDF fallback.")

        # Fallback to PyPDF text extraction if tables did not yield results
        if not parsed_txs and text_lines:
            for idx, line in enumerate(text_lines):
                tx = self._try_parse_line(line, idx=idx, page=0, db=db)
                if tx:
                    parsed_txs.append(tx)

        if not parsed_txs and not text_lines:
            # Try PyPDF directly if pdfplumber failed
            try:
                reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
                for page_idx, page in enumerate(reader.pages):
                    t = page.extract_text()
                    if t:
                        for line in t.split("\n"):
                            line_str = line.strip()
                            if line_str and not any(k in line_str.lower() for k in IGNORE_KEYWORDS):
                                tx = self._try_parse_line(line_str, idx=len(parsed_txs), page=page_idx, db=db)
                                if tx:
                                    parsed_txs.append(tx)
            except Exception as e:
                warnings.append(f"PyPDF fallback extraction failed: {str(e)}")

        # Evaluate confidence score
        confidence_avg = 1.0
        if not parsed_txs:
            warnings.append("Could not confidently extract structured transactions from this PDF statement. Please review or try CSV export.")
            confidence_avg = 0.20
        else:
            conf_sum = sum(tx.confidence for tx in parsed_txs)
            confidence_avg = conf_sum / len(parsed_txs)
            if confidence_avg < 0.70:
                warnings.append("Some transactions could not be confidently extracted. Please review the imported data.")

        return parsed_txs, warnings, round(confidence_avg, 2)

    def _try_parse_line(self, line: str, idx: int, page: int, db = None) -> Optional[ParsedTransaction]:
        """Tries to extract (Date, Description, Amount, Type) from a single line string."""
        # Find date
        found_date = None
        date_match = None
        for pattern in DATE_PATTERNS:
            match = re.search(pattern, line)
            if match:
                found_date = match.group(1)
                date_match = match
                break

        if not found_date or not date_match:
            return None

        # Standardize date
        try:
            dt = pd.to_datetime(found_date, errors='coerce')
            date_iso = dt.strftime("%Y-%m-%d") if not pd.isna(dt) else datetime.utcnow().strftime("%Y-%m-%d")
        except Exception:
            date_iso = datetime.utcnow().strftime("%Y-%m-%d")

        # Find amounts in line
        # Remove date part
        line_no_date = line[:date_match.start()] + " " + line[date_match.end():]
        
        # Regex to find currency amounts (e.g. ₹450.00, 1,250.00, 450)
        amount_matches = re.findall(r'₹?\s*([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{2})?|[0-9]+\.[0-9]{2}|[0-9]+)', line_no_date)
        valid_amounts = []
        for am in amount_matches:
            clean_str = am.replace(",", "").strip()
            try:
                val = float(clean_str)
                if val > 0 and val < 10000000:  # reasonable transaction limit
                    valid_amounts.append(val)
            except ValueError:
                pass

        if not valid_amounts:
            return None

        # Last numeric standard is often balance, first/second is transaction amount
        amount = valid_amounts[0]

        # Determine transaction type
        line_lower = line.lower()
        t_type = "expense"
        if any(k in line_lower for k in ["cr", "credit", "deposit", "salary", "refund", "received"]):
            t_type = "income"
        elif any(k in line_lower for k in ["dr", "debit", "withdrawal", "spent", "paid"]):
            t_type = "expense"

        # Extract description: text between date and amounts or remaining text
        desc = line_no_date
        for am in amount_matches:
            desc = desc.replace(am, "")
        # Clean extra spaces & currency symbols
        desc = re.sub(r'[₹$,\-\|\/]', ' ', desc)
        desc = re.sub(r'\s+', ' ', desc).strip()

        if len(desc) < 2:
            desc = "PDF Statement Transaction"

        category, confidence = categorize_description(desc, db=db)

        # PDF parsing confidence is naturally lower than clean CSV
        final_conf = min(confidence, 0.85)

        return ParsedTransaction(
            temp_id=f"pdf-p{page}-{idx}",
            date=date_iso,
            description=desc,
            amount=round(amount, 2),
            transaction_type=t_type,
            category=category,
            confidence=round(final_conf, 2),
            source="pdf",
            warnings=[]
        )

def parse_pdf_content(pdf_bytes: bytes, filename: str = "statement.pdf", db = None) -> Tuple[List[ParsedTransaction], List[str], float]:
    """Top-level function for PDF bank statement parsing."""
    parser = GenericPDFStatementParser()
    return parser.parse(pdf_bytes, db=db)
