"""
MedEasy — Lab Value Extractor

Extracts numeric lab values from cleaned report text and classifies
each against gender-specific normal ranges from the knowledge base.

Pipeline:
  1. Apply two regex patterns (colon-separated + space-separated)
  2. Resolve aliases → canonical key
  3. Look up LAB_RANGES
  4. Compare value → Normal / High / Low / Critical High / Critical Low
  5. Collect suggestion keys for abnormal values
"""

import re
from data.lab_ranges import LAB_RANGES, SUGGESTIONS


# Canonical name aliases (raw string → LAB_RANGES key)
ALIASES = {
    "s. hemoglobin":           "hemoglobin",
    "serum hemoglobin":        "hemoglobin",
    "hemoglobin hb":           "hemoglobin",
    "haemoglobin":             "hemoglobin",
    "hgb":                     "hemoglobin",
    "hb":                      "hemoglobin",
    "s. creatinine":           "creatinine",
    "serum creatinine":        "creatinine",
    "fasting blood sugar":     "glucose",
    "fbs":                     "glucose",
    "blood sugar fasting":     "glucose",
    "rbs":                     "glucose",
    "sgpt":                    "alt",
    "sgot":                    "ast",
    "total bilirubin":         "bilirubin",
    "t. bilirubin":            "bilirubin",
    "serum bilirubin":         "bilirubin",
    "s. uric acid":            "uric acid",
    "serum uric acid":         "uric acid",
    "total cholesterol":       "cholesterol",
    "s. cholesterol":          "cholesterol",
    "platelet count":          "platelets",
    "plt":                     "platelets",
    "wbc count":               "wbc",
    "total wbc":               "wbc",
    "rbc count":               "rbc",
    "vitamin d total":         "vitamin d",
    "vit d":                   "vitamin d",
    "25-oh vitamin d":         "vitamin d",
    "25 oh vitamin d":         "vitamin d",
    "vit b12":                 "vitamin b12",
    "cyanocobalamin":          "vitamin b12",
    "thyroid stimulating hormone": "tsh",
    "free t4":                 "t4",
    "free t3":                 "t3",
    "hdl cholesterol":         "hdl",
    "ldl cholesterol":         "ldl",
    "tgl":                     "triglycerides",
    "trig":                    "triglycerides",
    "blood urea nitrogen":     "bun",
    "serum urea":              "urea",
    "blood urea":              "urea",
    "glycated hemoglobin":     "hba1c",
    "glycosylated hemoglobin": "hba1c",
    "post prandial blood sugar": "ppbs",
    "post prandial glucose":   "ppbs",
    "pcv":                     "hematocrit",
    "alkaline phosphatase":    "alp",
    "erythrocyte sedimentation rate": "esr",
    "c-reactive protein":      "crp",
    "c reactive protein":      "crp",
    # ── REAL-WORLD LAB REPORT ALIASES ─────────────────────────────
    "cardio c-reactive protein":         "hsCRP",
    "cardio crp":                        "hsCRP",
    "hs-crp":                            "hsCRP",
    "apo b":                             "apolipoprotein b",
    "apolipoprotein b apo b":            "apolipoprotein b",
    "lp a":                              "lipoprotein a",
    "lp a serum":                        "lipoprotein a",
    "lipoprotein a lp a":                "lipoprotein a",
    "non-hdl cholesterol":               "non-hdl cholesterol",
    "non hdl cholesterol":               "non-hdl cholesterol",
    "non hdl":                           "non-hdl cholesterol",
    "vldl":                              "vldl cholesterol",
    "ldl cholesterol direct":            "ldl",
    "ldl direct":                        "ldl",
    "ldl cholesterol calculated":        "ldl",
    "eag":                               "estimated average glucose",
    "glucose fasting f plasma":          "glucose",
    "glucose fasting":                   "glucose",
    "hba1c glycosylated hemoglobin":     "hba1c",
    "glycated hemoglobin":               "hba1c",
    "glycosylated hemoglobin":           "hba1c",
    "troponin i high sensitive":         "hs troponin",
    "troponin i serum high sensitive":   "hs troponin",
    "cholesterol total":                 "cholesterol",
    "s. cholesterol":                    "cholesterol",
    # Trailing comma / semicolon variants (real lab PDF artifacts)
    "cardio c-reactive protein ,":       "hsCRP",
    "cardio c-reactive protein , serum": "hsCRP",
    "lipoprotein a ; lp a":              "lipoprotein a",
    "lipoprotein a ; lp a , serum":      "lipoprotein a",
    "lipoprotein a lp a , serum":        "lipoprotein a",
    "hba1c glycosylated hemoglobin , blood": "hba1c",
    "glucose , fasting f , plasma":      "glucose",
    "glucose fasting f , plasma":        "glucose",
    "s. glucose":                        "glucose",
    "s. calcium":                        "calcium",
    "s. sodium":                         "sodium",
    "s. potassium":                      "potassium",
}

# Words to skip as test names (false positive filters)
SKIP_NAMES = {
    "date", "age", "test", "result", "normal", "range", "page", "ref",
    "report", "doctor", "patient", "name", "gender", "sex", "time", "lab",
    "sample", "collected", "reported", "sl", "sr", "id", "no", "unit",
    "value", "method", "remark", "flag", "status",
}


class LabExtractor:
    """
    Extracts and classifies numeric lab values from cleaned report text.
    """

    # Primary: colon/equals separated
    PATTERN_COLON = re.compile(
        r"([A-Za-z][A-Za-z0-9 \(\)./\-]{1,28}?)"
        r"\s*[:=]\s*"
        r"(\d+\.?\d*)"
        r"\s*([A-Za-z%/µ×*.]{0,12})?",
        re.MULTILINE
    )

    # Secondary: space-separated table layout
    PATTERN_SPACE = re.compile(
        r"^([A-Za-z][A-Za-z0-9 \(\).]{1,25}?)"
        r"\s{2,}"
        r"(\d+\.?\d*)"
        r"\s+([A-Za-z%/µ]+)?",
        re.MULTILINE
    )
    # PDF table layout — single-space separated, no colon
    # e.g. "APOLIPOPROTEIN B (Apo B)   46.00   mg/dL"
    PATTERN_PDF = re.compile(
        r"^([A-Za-z][A-Za-z0-9 \(\).,;\-]{2,50}?)"
        r"\s{1,}"
        r"(\d+\.\d{1,3})"
        r"\s*([A-Za-z%/µL]{0,12})?",
        re.MULTILINE
    )


    def extract(self, cleaned_text: str, gender: str = "unknown") -> list:
        """
        Extract and classify all lab values from cleaned text.
        
        Args:
            cleaned_text: Pre-processed report text
            gender: 'male' | 'female' | 'unknown'
        Returns:
            List of result dicts
        """
        results = []
        seen = set()
        matches = []

        # Collect all regex matches from both patterns
        for m in self.PATTERN_COLON.finditer(cleaned_text):
            matches.append((m.group(1), float(m.group(2)), (m.group(3) or "").strip()))
        for m in self.PATTERN_SPACE.finditer(cleaned_text):
            matches.append((m.group(1), float(m.group(2)), (m.group(3) or "").strip()))
        for m in self.PATTERN_PDF.finditer(cleaned_text):
            matches.append((m.group(1), float(m.group(2)), (m.group(3) or "").strip()))

        for raw_name, value, unit in matches:
            if not value or value == 0:
                continue

            # Normalize name
            name = raw_name.strip().lower()
            name = re.sub(r"\s*\(.*?\)\s*", " ", name)  # remove parenthetical
            # Strip trailing punctuation and separators
            name = name.strip(".,;:/()")
            # Remove trailing method/sample names from real lab reports
            name = re.sub(
                r"\s*(immunoturbidimetry|god.pod|gpo.pod|cho.pod|calculated|"
                r"direct|hplc|ngsp|enz\s.*|serum\s*$|plasma\s*$|blood\s*$|"
                r"immunoinhibition|immunoturbidimetry)\s*$",
                "", name, flags=re.IGNORECASE
            ).strip(".,;:/ ")
            name = re.sub(r"\s+", " ", name).strip()

            if len(name) < 2:
                continue
            if name in SKIP_NAMES:
                continue
            if re.match(r"^(age|day|month|year|no|sl|sr|id)\b", name) and value < 200:
                continue

            # Resolve alias → canonical key
            canonical = ALIASES.get(name, name)
            if canonical not in LAB_RANGES:
                # Fuzzy match: find partial overlap with known keys
                best = self._fuzzy_match(name)
                if best:
                    canonical = best
                else:
                    continue

            if canonical in seen:
                continue
            seen.add(canonical)

            # Resolve alias chain
            info = LAB_RANGES[canonical]
            # Unit normalization: some labs report WBC in /uL raw (7200) vs x10³/µL range
            if canonical == "wbc" and value > 100:
                unit_low = unit.lower()
                # /cmm = /mm³ = same as /µL — if raw value > 100, divide by 1000 for x10³
                if any(u in unit_low for u in ["/ul", "/µl", "ul", "µl", "/cmm", "cmm", "/mm"]):
                    value = round(value / 1000, 2)
            # Platelets often reported as 210000 raw vs range 150-400 x10³/µL
            if canonical == "platelets" and value > 10000:
                value = round(value / 1000, 1)
            if canonical == "rbc" and value > 10:
                value = round(value / 1000000, 2)

            if info.get("alias"):
                canonical = info["alias"]
                info = LAB_RANGES.get(canonical, {})
            if not info or info.get("alias"):
                continue

            # Get gender-specific range
            lo, hi = self._get_range(info, gender)

            # Classify
            status = "Normal"
            if info.get("critH") is not None and value > info["critH"]:
                status = "Critical High"
            elif info.get("critL") is not None and value < info["critL"]:
                status = "Critical Low"
            elif hi < 999 and value > hi:
                status = "High"
            elif value < lo:
                status = "Low"

            # Range string for display
            if hi >= 999:
                range_str = f">{lo} {info.get('unit','')}"
            else:
                range_str = f"{lo}–{hi} {info.get('unit','')}"

            # Note
            note = self._note(status, lo, hi, info.get("unit", ""))

            # Suggestion key
            sugg_key = None
            if status in ("High", "Critical High"):
                sugg_key = info.get("suggH")
            elif status in ("Low", "Critical Low"):
                sugg_key = info.get("suggL")

            suggestion = SUGGESTIONS.get(sugg_key) if sugg_key else None

            results.append({
                "name":         info.get("name", canonical.upper()),
                "value":        f"{value} {unit or info.get('unit','')}".strip(),
                "numeric_value": value,
                "unit":         unit or info.get("unit", ""),
                "normal_range": range_str.strip(),
                "status":       status,
                "note":         note,
                "suggestion":   suggestion,
                "urgent":       bool(info.get("urgent")) and status in ("Critical High", "Critical Low"),
            })

        return results

    def _get_range(self, info: dict, gender: str) -> tuple:
        """Return (lo, hi) for this test given gender."""
        if gender == "male" and info.get("male"):
            return tuple(info["male"])
        if gender == "female" and info.get("female"):
            return tuple(info["female"])
        gen = info.get("gen", [0, 999])
        return tuple(gen)

    def _fuzzy_match(self, name: str) -> str:
        """Try to find a matching key in LAB_RANGES via substring."""
        sorted_keys = sorted(
            [k for k, v in LAB_RANGES.items() if not v.get("alias")],
            key=len, reverse=True
        )
        for key in sorted_keys:
            if name.startswith(key) or key.startswith(name) or key in name:
                return key
        return None

    def _note(self, status: str, lo: float, hi: float, unit: str) -> str:
        if status == "Normal":
            return "Within normal range ✓"
        if status == "Critical High":
            return "Critically elevated — seek immediate medical attention!"
        if status == "Critical Low":
            return "Critically low — seek immediate medical attention!"
        if status == "High":
            return f"Above upper limit of {hi} {unit}".strip()
        if status == "Low":
            return f"Below lower limit of {lo} {unit}".strip()
        return ""
