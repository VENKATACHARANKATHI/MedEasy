"""
MedEasy — Medical Named Entity Recognizer (Regex-based NER)

Extracts structured entities from raw report text:
  - Patient name, age, gender, date
  - Medical conditions
  - Medications
"""

import re


class MedicalNER:
    """
    Rule-based Named Entity Recognizer for medical reports.
    Uses compiled regex patterns for efficiency.
    """

    # ── Compiled patterns ────────────────────────────────────
    PATTERNS = {
        "name": [
            re.compile(r"(?:patient(?:\s+name)?|name)\s*[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})", re.IGNORECASE),
            re.compile(r"(?:Mr\.|Mrs\.|Ms\.|Dr\.)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)", re.IGNORECASE),
            re.compile(r"(?:for|patient)\s*:\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})", re.IGNORECASE),
        ],
        "age": [
            re.compile(r"(?:age|aged)\s*[:/]\s*(\d{1,3})", re.IGNORECASE),
            re.compile(r"(\d{1,3})\s*(?:yrs?|years?)\s*/?\s*(?:male|female|M|F)\b", re.IGNORECASE),
            re.compile(r"(?:age)\s*:\s*(\d{1,3})", re.IGNORECASE),
        ],
        "gender": [
            re.compile(r"\b(male|female)\b", re.IGNORECASE),
            re.compile(r"\b([MF])\s*/\s*\d|\d\s*/\s*([MF])\b", re.IGNORECASE),
        ],
        "date": [
            re.compile(r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}"),
            re.compile(r"\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}", re.IGNORECASE),
            re.compile(r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}", re.IGNORECASE),
        ],
    }

    # ── Condition patterns ────────────────────────────────────
    CONDITION_PATTERNS = [
        (re.compile(r"\b(?:diabet(?:es|ic|ics)|hyperglycemi|t2dm|type\s*2\s*diabetes)\b", re.IGNORECASE), "diabetes"),
        (re.compile(r"\b(?:an[ae]mi[ac]?|iron.?deficien|low.*hemoglobin|low.*haemoglobin)\b", re.IGNORECASE), "anemia"),
        (re.compile(r"\b(?:hypertens|high.?blood.?pressure)\b", re.IGNORECASE), "hypertension"),
        (re.compile(r"\b(?:hypothyroid|hyperthyroid|thyroid.?disorder|thyroiditis)\b", re.IGNORECASE), "thyroid disorder"),
        (re.compile(r"\b(?:hepat(?:itis|ic)|cirrhosis|liver.?disease|jaundice|fatty.?liver)\b", re.IGNORECASE), "liver disease"),
        (re.compile(r"\b(?:renal|nephro|ckd|kidney.?disease|kidney.?fail|chronic.?kidney)\b", re.IGNORECASE), "kidney disease"),
        (re.compile(r"\b(?:infect(?:ion|ious)|bacteremia|sepsis|bacterial|viral)\b", re.IGNORECASE), "infection"),
        (re.compile(r"\b(?:hypercholes|dyslipid|high.?cholesterol)\b", re.IGNORECASE), "high cholesterol"),
        (re.compile(r"\b(?:gout|hyperuricem)\b", re.IGNORECASE), "gout"),
        (re.compile(r"\b(?:cardiac|coronary|heart.?disease|myocardial)\b", re.IGNORECASE), "cardiac disease"),
        (re.compile(r"\b(?:vitamin.?d.?deficien|hypovitaminosis.?d)\b", re.IGNORECASE), "vitamin D deficiency"),
        (re.compile(r"\b(?:b12.?deficien|vitamin.?b12.?deficien)\b", re.IGNORECASE), "vitamin B12 deficiency"),
        (re.compile(r"\b(?:polycystic|pcos)\b", re.IGNORECASE), "PCOS"),
        (re.compile(r"\b(?:dyslipidemia|hyperlipidemia|hypercholesterol)\b", re.IGNORECASE), "dyslipidemia"),
        (re.compile(r"\b(?:cardiovascular|heart\s*disease|coronary)\b", re.IGNORECASE), "cardiovascular disease"),
        (re.compile(r"\b(?:vitamin\s*d\s*deficien)\b", re.IGNORECASE), "vitamin D deficiency"),
        (re.compile(r"\b(?:b12\s*deficien|cobalamin\s*deficien)\b", re.IGNORECASE), "vitamin B12 deficiency"),
        (re.compile(r"\b(?:iron\s*deficien)\b", re.IGNORECASE), "iron deficiency"),
        (re.compile(r"\b(?:hypercalcemia|hypocalcemia)\b", re.IGNORECASE), "calcium disorder"),
        (re.compile(r"\b(?:tuberculosis|tb)\b", re.IGNORECASE), "tuberculosis"),
    ]

    # ── Medication patterns ───────────────────────────────────
    MEDICATION_PATTERNS = re.compile(
        r"\b(metformin|insulin|glibenclamide|glimepiride|sitagliptin|empagliflozin"
        r"|atorvastatin|rosuvastatin|simvastatin|ezetimibe"
        r"|amlodipine|lisinopril|losartan|enalapril|ramipril|telmisartan"
        r"|levothyroxine|thyroxine|methimazole|carbimazole"
        r"|warfarin|aspirin|clopidogrel|rivaroxaban|apixaban"
        r"|omeprazole|pantoprazole|esomeprazole"
        r"|azithromycin|amoxicillin|ciprofloxacin|doxycycline"
        r"|prednisolone|dexamethasone|methylprednisolone"
        r"|allopurinol|febuxostat|colchicine)\b",
        re.IGNORECASE
    )

    def extract(self, text: str) -> dict:
        """
        Extract all entities from report text.
        
        Returns:
            dict with keys: name, age, gender, date, conditions, medications
        """
        return {
            "name":        self._extract_name(text),
            "age":         self._extract_age(text),
            "gender":      self._extract_gender(text),
            "date":        self._extract_date(text),
            "conditions":  self._extract_conditions(text),
            "medications": self._extract_medications(text),
        }

    def _extract_name(self, text: str) -> str:
        for pattern in self.PATTERNS["name"]:
            m = pattern.search(text)
            if m:
                name = m.group(1).strip()
                # Skip column headers
                if name.lower() in {"name", "result", "test", "normal", "range"}:
                    continue
                # Remove trailing "Age" or "Gender" words captured by greedy match
                name = re.split(r"\s{2,}|\s+(?:Age|Gender|DOB|Date|Lab)\b", name, flags=re.I)[0].strip()
                if len(name) > 2:
                    return name
        return "Unknown"

    def _extract_age(self, text: str) -> str:
        for pattern in self.PATTERNS["age"]:
            m = pattern.search(text)
            if m:
                age = int(m.group(1))
                if 0 < age < 120:
                    return str(age)
        return "Unknown"

    def _extract_gender(self, text: str) -> str:
        for pattern in self.PATTERNS["gender"]:
            m = pattern.search(text)
            if m:
                val = (m.group(1) or m.group(2) or "").lower()
                if val in ("male", "m"):
                    return "male"
                if val in ("female", "f"):
                    return "female"
        return "unknown"

    def _extract_date(self, text: str) -> str:
        for pattern in self.PATTERNS["date"]:
            m = pattern.search(text)
            if m:
                return m.group(0)
        return ""

    def _extract_conditions(self, text: str) -> list:
        found = []
        for pattern, label in self.CONDITION_PATTERNS:
            if pattern.search(text) and label not in found:
                found.append(label)
        return found

    def _extract_medications(self, text: str) -> list:
        meds = self.MEDICATION_PATTERNS.findall(text)
        return list(dict.fromkeys(m.lower() for m in meds))  # deduplicate, preserve order
