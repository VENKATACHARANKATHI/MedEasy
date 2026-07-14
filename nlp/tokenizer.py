"""
MedEasy — Medical Report Tokenizer

Cleans raw report text (including PDF-extracted text) and prepares it
for NER and lab value extraction.
"""

import re


class MedicalTokenizer:
    """
    Cleans and normalizes medical report text.
    
    Key operations:
    - Fix PDF space-joined text (inserts newlines before test names)
    - Normalize whitespace and encoding artifacts
    - Convert lakh notation to numeric
    - Remove thousands commas from numbers
    - Strip normal range columns (e.g. "13-17 g/dL" reference column)
    """

    # Test name keywords that should start on a new line in PDF text
    TEST_NAMES = [
        # Extended list — real lab report test names
        "Apolipoprotein", "APOLIPOPROTEIN", "Lipoprotein", "LIPOPROTEIN",
        "SGOT", "SGPT", "GGT", "ALT", "AST",
        "Cholesterol", "Triglycerides", "HDL", "LDL", "VLDL", "Non-HDL",
        "Hemoglobin", "Haemoglobin", "WBC", "RBC", "Platelet", "Hematocrit",
        "HbA1c", "Hba1c", "Glucose", "Fasting", "Creatinine", "Urea", "BUN",
        "Cholesterol", "HDL", "LDL", "Triglyceride", "ALT", "AST", "ALP",
        "SGPT", "SGOT", "Bilirubin", "Albumin", "TSH", "Vitamin", "Ferritin",
        "Sodium", "Potassium", "Calcium", "ESR", "CRP", "Troponin", "Uric",
        "GGT", "MCH", "MCHC", "MCV", "RDW", "Neutrophil", "Lymphocyte",
        "Monocyte", "Eosinophil", "Insulin", "Folate", "Iron", "TIBC",
        "Magnesium", "Phosphorus", "Chloride",
    ]

    def clean(self, text: str) -> str:
        """
        Full cleaning pipeline.
        
        Args:
            text: Raw text (from PDF, paste, or file)
        Returns:
            Cleaned, normalized text
        """
        text = self._fix_encoding(text)
        text = self._fix_lakh(text)
        text = self._remove_comma_thousands(text)
        text = self._strip_range_columns(text)
        text = self._fix_pdf_space_join(text)
        text = self._normalize_whitespace(text)
        return text

    def check_text_quality(self, text: str) -> dict:
        """
        Detect garbled/encoded PDF text that cannot be analyzed.
        
        Returns:
            dict with: is_garbled (bool), reason (str), readable_ratio (float)
        """
        if not text or len(text) < 10:
            return {"is_garbled": False, "readable_ratio": 1.0, "reason": ""}

        # Count box/replacement characters — sign of font encoding failure
        box_chars = len(re.findall(r"[\uFFFD\u25A1\u25A0\u2610\u2612\u2B1C]", text))
        # Readable = alphanumeric characters
        readable = len(re.findall(r"[A-Za-z0-9]", text))
        readable_ratio = readable / max(len(text), 1)

        if box_chars > 15 or readable_ratio < 0.08:
            return {
                "is_garbled": True,
                "readable_ratio": round(readable_ratio, 3),
                "reason": (
                    "PDF text appears garbled or encoded with a non-standard font. "
                    "Try: Open the PDF → Select All (Ctrl+A) → Copy → Paste the text directly. "
                    "Or convert the PDF to plain text first."
                )
            }
        return {"is_garbled": False, "readable_ratio": round(readable_ratio, 3), "reason": ""}

    def _fix_encoding(self, text: str) -> str:
        """Fix common encoding artifacts from PDF extraction."""
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = text.replace("\u00b5", "u")   # µ → u
        text = text.replace("\u00d7", "x")   # × → x
        text = text.replace("\u2013", "-")   # en-dash → hyphen
        text = text.replace("\u2014", "-")   # em-dash → hyphen
        return text

    def _fix_lakh(self, text: str) -> str:
        """Convert lakh notation: 2.1 lakh → 210000"""
        def replace_lakh(m):
            return str(int(float(m.group(1)) * 100000))
        return re.sub(r"(\d+\.?\d*)\s*lakh", replace_lakh, text, flags=re.IGNORECASE)

    def _remove_comma_thousands(self, text: str) -> str:
        """Remove comma separators in numbers: 12,500 → 12500"""
        return re.sub(r"(\d),(\d{3})", r"\1\2", text)

    def _strip_range_columns(self, text: str) -> str:
        """
        Remove normal range reference columns from table-style reports.
        Example: "13-17 g/dL" or "4000-11000 /uL" gets stripped.
        """
        # Strip reference range columns like "46 - 174", "<200", ">40", "<1.00"
        text = re.sub(r"(?:^|\s)[<>]\d+\.?\d*(?:\s|$)", " ", text, flags=re.M)
        return re.sub(
            r"\b\d+\s*[-\u2013]\s*\d+[\d.]*"
            r"(?:\s*(?:g/dL|mg/dL|/[uU]L|%|U/L|mIU/L|ng/mL|pg/mL|mmol/L|mEq/L|mm/hr))?\b",
            "",
            text
        )

    def _fix_pdf_space_join(self, text: str) -> str:
        """
        PDF.js joins all text items with spaces.
        Insert newlines before known test name keywords to split them.
        """
        for name in self.TEST_NAMES:
            text = re.sub(rf"(?<!\w)({re.escape(name)})", r"\n\1", text)
        # Also normalize tab separators
        text = text.replace("\t", ":")
        return text

    def _normalize_whitespace(self, text: str) -> str:
        """Collapse multiple spaces/blank lines."""
        text = re.sub(r" {2,}", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def extract_number_context(self, text: str) -> list:
        """
        Find all (number, left_context, unit) tuples in text.
        
        Returns:
            List of dicts with keys: value, left, unit
        """
        pattern = re.compile(
            r"([A-Za-z][A-Za-z0-9 \(\)./\-]{1,30}?)"  # left context (test name)
            r"\s*[:=]\s*"                                # separator
            r"(\d+\.?\d*)"                              # numeric value
            r"\s*([A-Za-z%/µ×*.]{0,12})?",              # unit
            re.MULTILINE
        )
        results = []
        for m in pattern.finditer(text):
            results.append({
                "left":  m.group(1).strip(),
                "value": float(m.group(2)),
                "unit":  (m.group(3) or "").strip(),
            })
        return results
