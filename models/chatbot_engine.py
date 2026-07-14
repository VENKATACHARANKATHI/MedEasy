"""
MedEasy — MedBot Chatbot Engine (Ollama phi3 Backend)

Uses Ollama running locally — NO API KEY required.
Ollama exposes a REST API at http://localhost:11434

Setup:
  1. Install Ollama: https://ollama.ai
  2. Pull model:    ollama pull phi3
  3. Run server:    ollama serve   (auto-starts on most systems)
  4. Start app:     python run.py

Intent classification (always available, no Ollama needed):
  - 119 training examples across 7 intents
  - TF-IDF vectorization + cosine similarity
  - Threshold: 0.12

Ollama integration:
  - Model: phi3  (Microsoft Phi-3, fast + accurate for medical Q&A)
  - Endpoint: POST http://localhost:11434/api/chat
  - No API key, no cost, fully private — runs on your machine
"""

import json
import requests
import numpy as np
from .tfidf import TFIDFVectorizer, cosine_similarity_matrix
from data.training_data import CHATBOT_INTENTS
from data.medical_terms import MEDICAL_TERMS
from data.lab_ranges import LAB_RANGES, SUGGESTIONS

# ── Ollama Configuration ────────────────────────────────────────
OLLAMA_BASE_URL   = "http://localhost:11434"
# phi3:mini is 3.8B params — 4x faster than phi3 (14B) with similar quality for medical Q&A
# Run: ollama pull phi3:mini
# Fallback: phi3 (14B) — slower but more detailed
OLLAMA_MODEL      = "phi3:mini"
OLLAMA_TIMEOUT    = 45
OLLAMA_MAX_TOKENS = 300   # Shorter = faster. Medical answers rarely need more.


class ChatbotEngine:
    """
    MedBot: TF-IDF intent classifier + Ollama phi3 AI backend.
    No API key. No cloud. Runs 100% locally.
    """

    SIMILARITY_THRESHOLD = 0.12

    EMERGENCY_PATTERNS = [
        "chest pain", "heart attack", "cant breathe", "cannot breathe",
        "difficulty breathing", "unconscious", "stroke", "severe bleeding",
        "collapse", "not breathing", "severe chest", "vomiting blood",
        "seizure", "fainting",
    ]

    def __init__(self):
        self.vectorizer     = TFIDFVectorizer(max_features=300)
        self._train_vectors = None
        self._train_labels  = []
        self._train()

    def _train(self):
        corpus, labels = [], []
        for intent, examples in CHATBOT_INTENTS.items():
            for ex in examples:
                corpus.append(ex)
                labels.append(intent)
        self._train_vectors = self.vectorizer.fit_transform(corpus)
        self._train_labels  = labels
        print(f"[Chatbot] Trained on {len(corpus)} examples, {len(CHATBOT_INTENTS)} intents")

    # ── Intent Classification ─────────────────────────────────────

    def classify_intent(self, message: str) -> str:
        msg_lower = message.lower()
        if any(p in msg_lower for p in self.EMERGENCY_PATTERNS):
            return "urgent_symptoms"
        query_vec = self.vectorizer.transform_single(message)
        sims      = cosine_similarity_matrix(query_vec, self._train_vectors)
        best_idx  = int(np.argmax(sims))
        best_sim  = float(sims[best_idx])
        if best_sim < self.SIMILARITY_THRESHOLD:
            return "fallback"
        return self._train_labels[best_idx]

    # ── Ollama ────────────────────────────────────────────────────

    def is_ollama_running(self) -> bool:
        try:
            r = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=3)
            return r.status_code == 200
        except Exception:
            return False

    def build_system_prompt(self, language: str, report_context: dict) -> str:
        if report_context:
            r        = report_context
            patient  = r.get("patient", {})
            abnormal = r.get("abnormal_values", r.get("abnormal", []))
            ab_list  = ", ".join(
                f"{v['name']}: {v['value']} ({v.get('status','')})"
                for v in abnormal[:8]
            ) or "none"
            conditions = ", ".join(patient.get("conditions", [])) or "none"
            suggestions = "; ".join(s["title"] for s in r.get("suggestions", [])[:3])
            report_summary = (
                f"Report: {r.get('report_type','Unknown')} | "
                f"Patient: {patient.get('name','?')}, Age {patient.get('age','?')}, {patient.get('gender','?')} | "
                f"Status: {r.get('status_key','?')} | "
                f"Tests: {r.get('total_tests',0)} total, {r.get('normal_count',0)} normal, {r.get('abnormal_count',0)} abnormal | "
                f"Abnormal values: {ab_list} | "
                f"Conditions: {conditions} | "
                f"Suggestions: {suggestions}"
            )
        else:
            report_summary = "No report analyzed yet."

        return (
            f"You are MedBot, a friendly medical assistant in MedEasy, a medical report simplification system for Indian patients.\n\n"
            f"RULES:\n"
            f"- ALWAYS respond in {language} language\n"
            f"- Be warm, empathetic, use simple words\n"
            f"- When asked about diagnosis or disease, analyze the report and give a direct answer\n"
            f"- Explain lab values in practical, everyday terms\n"
            f"- Give specific, actionable advice (diet, exercise, lifestyle)\n"
            f"- End serious advice with: Please consult your doctor for professional guidance\n"
            f"- Use 1-2 emojis to be friendly\n"
            f"- Keep responses to 3-5 sentences unless detail is requested\n"
            f"- NEVER refuse medical questions\n\n"
            f"PATIENT REPORT:\n{report_summary}"
        )

    def call_ollama(self, message: str, system_prompt: str) -> str:
        """Call Ollama phi3 via local REST API. No API key needed."""
        try:
            resp = requests.post(
                f"{OLLAMA_BASE_URL}/api/chat",
                headers={"Content-Type": "application/json"},
                json={
                    "model":  OLLAMA_MODEL,
                    "stream": False,
                    "options": {
                        "num_predict": OLLAMA_MAX_TOKENS,
                        "temperature": 0.7,
                        "top_p": 0.9,
                    },
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user",   "content": message},
                    ]
                },
                timeout=OLLAMA_TIMEOUT
            )
            resp.raise_for_status()
            data    = resp.json()
            content = data.get("message", {}).get("content") or data.get("response", "")
            return content.strip() if content else "Sorry, I couldn't generate a response. Please try again."

        except requests.exceptions.ConnectionError:
            return (
                "⚠️ **Ollama is not running.** To activate MedBot AI:\n"
                "1. Install Ollama → https://ollama.ai\n"
                "2. Run: `ollama pull phi3`\n"
                "3. Run: `ollama serve`\n\n"
                "I can still answer basic questions about medical terms and normal ranges!"
            )
        except requests.exceptions.Timeout:
            return "⏳ phi3 is taking too long (may be loading). Please try again in a moment."
        except Exception as e:
            return f"⚠️ Ollama error: {str(e)[:100]}"

    # ── Local Knowledge-Base Responses ───────────────────────────

    def generate_local_response(self, message: str, intent: str,
                                report_context: dict, language: str):
        """
        Instant structured response from knowledge base.
        Returns None if Ollama should handle the question.
        """
        t = message.lower()

        if intent == "greeting":
            G = {
                "English": "👋 Hello! I'm **MedBot** powered by **phi3 AI** running locally. Ask me anything about your report, test values, or health — no internet needed!",
                "Hindi":   "👋 नमस्ते! मैं **MedBot** हूँ, **phi3 AI** द्वारा संचालित — बिना इंटरनेट के! रिपोर्ट या स्वास्थ्य के बारे में कुछ भी पूछें।",
                "Marathi": "👋 नमस्कार! मी **MedBot** आहे, **phi3 AI** वापरून — इंटरनेटशिवाय! रिपोर्टबद्दल काहीही विचारा.",
                "Bengali": "👋 নমস্কার! আমি **MedBot**, **phi3 AI** দ্বারা চালিত — ইন্টারনেট ছাড়াই! রিপোর্ট সম্পর্কে যেকোনো প্রশ্ন করুন।",
                "Tamil":   "👋 வணக்கம்! நான் **MedBot**, **phi3 AI** ஆல் இயக்கப்படுகிறேன் — இணையம் தேவையில்லை! உங்கள் அறிக்கை பற்றி கேளுங்கள்.",
                "Telugu":  "👋 నమస్కారం! నేను **MedBot**, **phi3 AI** తో నడుస్తున్నాను — ఇంటర్నెట్ అవసరం లేదు! మీ నివేదిక గురించి అడగండి.",
            }
            return G.get(language, G["English"])

        if intent == "farewell":
            F = {
                "English": "Take care! Follow up with your doctor for any abnormal values. Stay healthy! 🙏",
                "Hindi":   "ख्याल रखें! असामान्य परिणामों के लिए डॉक्टर से मिलें। स्वस्थ रहें! 🙏",
                "Marathi": "काळजी घ्या! असामान्य निकालांसाठी डॉक्टरांना भेटा. निरोगी राहा! 🙏",
                "Bengali": "ভালো থাকুন! অস্বাভাবিক ফলাফলের জন্য ডাক্তার দেখান। 🙏",
                "Tamil":   "கவனமாக! அசாதாரண முடிவுகளுக்கு மருத்துவரை சந்தியுங்கள்! 🙏",
                "Telugu":  "జాగ్రత్తగా! అసాధారణ ఫలితాలకు వైద్యుడిని సంప్రదించండి! 🙏",
            }
            return F.get(language, F["English"])

        if intent == "urgent_symptoms":
            U = {
                "English": "🚨 URGENT: Call emergency services (112) or go to the nearest hospital IMMEDIATELY. Do not wait!",
                "Hindi":   "🚨 तुरंत 112 पर कॉल करें या नजदीकी अस्पताल जाएं! देरी न करें!",
                "Marathi": "🚨 त्वरित 112 वर कॉल करा या जवळच्या रुग्णालयात जा! थांबू नका!",
                "Bengali": "🚨 জরুরি: 112 তে ফোন করুন অথবা অবিলম্বে নিকটস্থ হাসপাতালে যান!",
                "Tamil":   "🚨 அவசரம்: 112 அழையுங்கள் அல்லது உடனே மருத்துவமனைக்கு செல்லுங்கள்!",
                "Telugu":  "🚨 అత్యవసరం: 112 కి కాల్ చేయండి లేదా వెంటనే ఆసుపత్రికి వెళ్ళండి!",
            }
            return U.get(language, U["English"])

        if intent == "explain_term":
            for term in sorted(MEDICAL_TERMS.keys(), key=len, reverse=True):
                if term in t:
                    return f"📖 **{term.upper()}**: {MEDICAL_TERMS[term]}"
            return None  # let Ollama explain unknown terms

        if intent == "normal_range":
            for key in sorted(LAB_RANGES.keys(), key=len, reverse=True):
                info = LAB_RANGES[key]
                if info.get("alias") or key not in t:
                    continue
                u = info.get("unit", "")
                if info.get("male") and info.get("female"):
                    return (f"📊 **{info.get('name', key.upper())}** — "
                            f"Men: {info['male'][0]}–{info['male'][1]} {u} | "
                            f"Women: {info['female'][0]}–{info['female'][1]} {u}")
                elif info.get("gen"):
                    return f"📊 **{info.get('name', key.upper())}** normal range: {info['gen'][0]}–{info['gen'][1]} {u}"
            return None  # let Ollama answer unknown ranges

        if intent == "report_summary" and report_context:
            r  = report_context
            ab = r.get("abnormal_values", r.get("abnormal", []))
            ab_list = ", ".join(
                f"{v['name']} ({v.get('strans', v.get('status',''))})"
                for v in ab[:5]
            )
            return (
                f"📋 **{r.get('report_type', 'Report')}**: "
                f"{r.get('total_tests', 0)} tests — "
                f"{r.get('normal_count', 0)} normal ✅, "
                f"{r.get('abnormal_count', 0)} need attention ⚠️."
                + (f" Flagged: {ab_list}." if ab_list else " All values normal! 🎉")
                + f"\n{r.get('doctor_advice', '')}"
            )

        if intent == "health_advice" and report_context:
            suggestions = report_context.get("suggestions", [])
            if suggestions:
                s = suggestions[0]
                return f"{s['icon']} **{s['title']}**: {s['detail']}"

        # All other intents → Ollama
        return None

    # ── Main Entry Point ──────────────────────────────────────────

    def get_response(self, message: str, report_context: dict,
                     language: str = "English") -> dict:
        """
        Main method called by app.py /api/chat.

        Returns:
            dict: { reply, intent, source }
            source = "local" | "ollama" | "emergency"
        """
        intent = self.classify_intent(message)

        # Emergency → always instant local response
        if intent == "urgent_symptoms":
            return {
                "reply":  self.generate_local_response(message, intent, report_context, language),
                "intent": intent,
                "source": "emergency",
            }

        # Try knowledge-base first (instant)
        local_reply = self.generate_local_response(message, intent, report_context, language)
        if local_reply is not None:
            return {"reply": local_reply, "intent": intent, "source": "local"}

        # Let Ollama phi3 handle it
        system       = self.build_system_prompt(language, report_context)
        ollama_reply = self.call_ollama(message, system)
        return {"reply": ollama_reply, "intent": intent, "source": "ollama"}
