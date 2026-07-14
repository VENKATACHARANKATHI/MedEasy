"""
MedEasy — NLP Pipeline Orchestrator

Runs all 5 stages in sequence:
  Stage 1: MedicalTokenizer.clean()     — text normalization
  Stage 2: MedicalNER.extract()         — patient entity extraction
  Stage 3: LabExtractor.extract()       — numeric value extraction + classification
  Stage 4: ReportTypeClassifier.predict() — TF-IDF + Naive Bayes classification
  Stage 5: MedicalSimplifier.simplify() — plain language + translation
"""

from nlp.tokenizer import MedicalTokenizer
from nlp.ner import MedicalNER
from nlp.lab_extractor import LabExtractor
from nlp.simplifier import MedicalSimplifier
from models.classifier import ReportTypeClassifier
import time


class MedEasyPipeline:
    """
    Master pipeline that orchestrates all NLP stages.
    
    Usage:
        pipeline = MedEasyPipeline()
        result = pipeline.analyze(text, language="English")
    """

    def __init__(self):
        print("[Pipeline] Initializing components...")
        t0 = time.time()

        self.tokenizer  = MedicalTokenizer()
        self.ner        = MedicalNER()
        self.extractor  = LabExtractor()
        self.classifier = ReportTypeClassifier()   # trains on init
        self.simplifier = MedicalSimplifier()

        print(f"[Pipeline] Ready in {time.time()-t0:.2f}s")

    def analyze(self, raw_text: str, language: str = "English") -> dict:
        """
        Full analysis pipeline.
        
        Args:
            raw_text: Raw report text (from paste, PDF, DOCX, etc.)
            language: Output language ('English'|'Hindi'|'Marathi'|'Bengali'|'Tamil'|'Telugu')
        Returns:
            Complete analysis result dict
        """
        t0 = time.time()

        # ── Stage 1: Clean and normalize ─────────────────────
        cleaned = self.tokenizer.clean(raw_text)

        # ── Stage 2: Named Entity Recognition ────────────────
        patient = self.ner.extract(cleaned)

        # ── Stage 3: Lab value extraction ────────────────────
        lab_values = self.extractor.extract(cleaned, patient["gender"])

        # ── Stage 4: Report type classification ──────────────
        classification = self.classifier.predict(cleaned)

        # ── Stage 5: Simplification + Translation ────────────
        status_key   = self.simplifier.compute_status(lab_values)
        simplified   = self.simplifier.simplify(
            classification["type"], lab_values, status_key, language
        )
        suggestions  = self.simplifier.get_suggestions(lab_values)
        urgent_flags = self.simplifier.get_urgent_flags(lab_values)
        lab_values   = self.simplifier.translate_values(lab_values, language)

        # ── Compute derived counts ────────────────────────────
        normal_values   = [v for v in lab_values if v["status"] == "Normal"]
        abnormal_values = [v for v in lab_values if v["status"] != "Normal"]

        elapsed = round(time.time() - t0, 3)
        print(f"[Pipeline] Analysis done in {elapsed}s | "
              f"{len(lab_values)} values | status={status_key}")

        return {
            # Patient info
            "patient": patient,

            # Report classification
            "report_type":       classification["type"],
            "report_confidence": classification["confidence"],

            # Lab results
            "lab_values":       lab_values,
            "abnormal_values":  abnormal_values,
            "normal_values":    normal_values,
            "total_tests":      len(lab_values),
            "normal_count":     len(normal_values),
            "abnormal_count":   len(abnormal_values),
            "urgent_flags":     urgent_flags,

            # Overall status
            "status_key":   status_key,
            "status_label": simplified["status_label"],

            # Plain language
            "explanation":   simplified["explanation"],
            "doctor_advice": simplified["doctor_advice"],
            "suggestions":   suggestions,

            # Meta
            "language":    language,
            "elapsed_sec": elapsed,
        }
