"""
MedEasy — Medical Simplifier + Translator

Computes overall health status and generates plain-language
explanations in 6 languages.
"""

from data.translations import (
    get_status_label, get_value_status, get_doctor_advice, get_explanation
)
from data.lab_ranges import SUGGESTIONS


class MedicalSimplifier:
    """
    Converts structured analysis results into plain-language output.
    
    compute_status(): derives Good/Fair/Attention/Critical from abnormal ratio
    simplify(): builds the complete explanation + doctor advice
    translate_values(): adds strans (translated status) to each lab value
    """

    STATUS_THRESHOLDS = {
        "Critical":  0.60,  # > 60% abnormal OR any urgent flag
        "Attention": 0.30,  # > 30% abnormal
        "Fair":      0.01,  # any abnormal
        "Good":      0.00,  # all normal
    }

    def compute_status(self, lab_values: list) -> str:
        """
        Determine overall health status.
        
        Args:
            lab_values: List of extracted lab value dicts
        Returns:
            Status key: 'Good' | 'Fair' | 'Attention' | 'Critical'
        """
        if not lab_values:
            return "Fair"

        abnormal = [v for v in lab_values if v["status"] != "Normal"]
        urgent = [v for v in lab_values if v.get("urgent")]

        if urgent:
            return "Critical"

        ratio = len(abnormal) / len(lab_values)

        if ratio > self.STATUS_THRESHOLDS["Critical"]:
            return "Critical"
        if ratio > self.STATUS_THRESHOLDS["Attention"]:
            return "Attention"
        if ratio > self.STATUS_THRESHOLDS["Fair"]:
            return "Fair"
        return "Good"

    def simplify(self, report_type: str, lab_values: list,
                 status_key: str, language: str) -> dict:
        """
        Generate plain-language explanation and doctor advice.
        
        Args:
            report_type: Classified report type name
            lab_values: List of extracted + classified lab values
            status_key: 'Good' | 'Fair' | 'Attention' | 'Critical'
            language: Target language
        Returns:
            dict with: explanation, doctor_advice, status_label
        """
        normal   = [v for v in lab_values if v["status"] == "Normal"]
        abnormal = [v for v in lab_values if v["status"] != "Normal"]

        # Explanation paragraph
        if not lab_values:
            from data.translations import TRANSLATIONS
            no_val_t = TRANSLATIONS.get("no_values_detected", {})
            explanation = no_val_t.get(language, no_val_t.get("English",
                "No numeric lab values could be extracted. "
                "If you uploaded a PDF, try copy-pasting the report text directly. "
                "Format: Hemoglobin: 12.5 g/dL"
            ))
        elif not abnormal:
            explanation = get_explanation(
                "all_good", language,
                report_type=report_type,
                total=len(lab_values),
            )
        else:
            ab_names = ", ".join(v["name"] for v in abnormal[:5])
            explanation = get_explanation(
                "some_abnormal", language,
                report_type=report_type,
                total=len(lab_values),
                normal=len(normal),
                abnormal=len(abnormal),
                list=ab_names,
            )

        # Doctor advice key
        urgent_flags = [v for v in lab_values if v.get("urgent")]
        if urgent_flags:
            advice_key = "emergency"
        elif not abnormal:
            advice_key = "good"
        elif len(abnormal) / max(len(lab_values), 1) <= 0.4:
            advice_key = "soon"
        else:
            advice_key = "asap"

        doctor_advice = get_doctor_advice(advice_key, language)
        status_label  = get_status_label(status_key, language)

        return {
            "explanation":  explanation,
            "doctor_advice": doctor_advice,
            "status_label":  status_label,
        }

    def get_suggestions(self, lab_values: list) -> list:
        """
        Collect unique health suggestions from abnormal lab values.
        
        Args:
            lab_values: List of lab value dicts
        Returns:
            List of suggestion dicts (max 6)
        """
        seen_keys = set()
        suggestions = []

        for v in lab_values:
            if v["status"] in ("High", "Critical High") and v.get("suggestion"):
                s = v["suggestion"]
                key = s["title"]
                if key not in seen_keys:
                    seen_keys.add(key)
                    suggestions.append(s)
            elif v["status"] in ("Low", "Critical Low") and v.get("suggestion"):
                s = v["suggestion"]
                key = s["title"]
                if key not in seen_keys:
                    seen_keys.add(key)
                    suggestions.append(s)

        if not suggestions and lab_values:
            suggestions.append(SUGGESTIONS["ok"])

        return suggestions[:6]

    def get_urgent_flags(self, lab_values: list) -> list:
        """Return list of urgent flag messages for critical values."""
        flags = []
        for v in lab_values:
            if v.get("urgent") and v["status"] != "Normal":
                flags.append(
                    f"{v['name']} is {v['status'].lower()} "
                    f"({v['value']}) — seek immediate medical attention!"
                )
        return flags

    def translate_values(self, lab_values: list, language: str) -> list:
        """Add translated status label (strans) to each lab value."""
        for v in lab_values:
            v["strans"] = get_value_status(v["status"], language)
        return lab_values
