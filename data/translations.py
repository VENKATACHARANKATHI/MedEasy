# ─────────────────────────────────────────────────────────────
# MedEasy — Multilingual Translation Templates
# Languages: English, Hindi, Marathi, Bengali, Tamil, Telugu
# ─────────────────────────────────────────────────────────────

TRANSLATIONS = {
    "status_labels": {
        "Good":       {"English": "🟢 Good",            "Hindi": "🟢 अच्छा",        "Marathi": "🟢 चांगले",        "Bengali": "🟢 ভালো",          "Tamil": "🟢 நல்லது",      "Telugu": "🟢 బాగుంది"},
        "Fair":       {"English": "🟡 Fair",            "Hindi": "🟡 ठीक-ठाक",      "Marathi": "🟡 ठीक",          "Bengali": "🟡 মোটামুটি",      "Tamil": "🟡 சாதாரணம்",   "Telugu": "🟡 సాధారణం"},
        "Attention":  {"English": "🟠 Attention Needed","Hindi": "🟠 ध्यान जरूरी",  "Marathi": "🟠 लक्ष द्या",    "Bengali": "🟠 মনোযোগ দরকার", "Tamil": "🟠 கவனம் தேவை","Telugu": "🟠 శ్రద్ధ అవసరం"},
        "Critical":   {"English": "🔴 Critical",        "Hindi": "🔴 गंभीर",        "Marathi": "🔴 गंभीर",        "Bengali": "🔴 গুরুতর",        "Tamil": "🔴 அவசரம்",     "Telugu": "🔴 తీవ్రమైనది"},
    },
    "value_status": {
        "Normal":        {"English": "Normal",        "Hindi": "सामान्य",   "Marathi": "सामान्य",   "Bengali": "স্বাভাবিক",    "Tamil": "இயல்பு",   "Telugu": "సాధారణం"},
        "High":          {"English": "High",          "Hindi": "अधिक",      "Marathi": "जास्त",     "Bengali": "বেশি",         "Tamil": "அதிகம்",  "Telugu": "అధికం"},
        "Low":           {"English": "Low",           "Hindi": "कम",        "Marathi": "कमी",       "Bengali": "কম",           "Tamil": "குறைவு",  "Telugu": "తక్కువ"},
        "Critical High": {"English": "Critical High", "Hindi": "अत्यधिक",   "Marathi": "अतिजास्त",  "Bengali": "অত্যন্ত বেশি", "Tamil": "மிக அதிகம்","Telugu": "చాలా అధికం"},
        "Critical Low":  {"English": "Critical Low",  "Hindi": "अत्यल्प",   "Marathi": "अतिकमी",    "Bengali": "অত্যন্ত কম",   "Tamil": "மிக குறைவு","Telugu": "చాలా తక్కువ"},
    },
    "doctor_advice": {
        "good": {
            "English": "✅ Results look healthy. Keep regular checkups every 6–12 months.",
            "Hindi":   "✅ परिणाम स्वस्थ दिख रहे हैं। हर 6–12 महीने में नियमित जाँच करें।",
            "Marathi": "✅ निकाल निरोगी. दर 6–12 महिन्यांनी तपासणी करा.",
            "Bengali": "✅ ফলাফল সুস্থ। প্রতি 6–12 মাসে চেকআপ করুন।",
            "Tamil":   "✅ முடிவுகள் ஆரோக்கியம். 6–12 மாதங்களில் பரிசோதனை செய்யுங்கள்.",
            "Telugu":  "✅ ఫలితాలు ఆరోగ్యంగా ఉన్నాయి. 6–12 నెలలకు చెకప్ చేయించుకోండి.",
        },
        "soon": {
            "English": "📅 See a doctor within 1–2 weeks. Discuss the flagged values.",
            "Hindi":   "📅 1–2 हफ्तों में डॉक्टर से मिलें। असामान्य मानों पर चर्चा करें।",
            "Marathi": "📅 1–2 आठवड्यांत डॉक्टरांना भेटा.",
            "Bengali": "📅 1–2 সপ্তাহে ডাক্তার দেখান।",
            "Tamil":   "📅 1–2 வாரங்களில் மருத்துவரை சந்தியுங்கள்.",
            "Telugu":  "📅 1–2 వారాల్లో వైద్యుడిని కలవండి.",
        },
        "asap": {
            "English": "🏥 See a doctor within a few days. Multiple abnormal values detected. Bring this report.",
            "Hindi":   "🏥 कुछ दिनों में डॉक्टर से मिलें। कई असामान्य मान हैं। यह रिपोर्ट साथ लाएं।",
            "Marathi": "🏥 काही दिवसांत डॉक्टरांना भेटा. अनेक असामान्य मूल्ये आहेत.",
            "Bengali": "🏥 কয়েকদিনে ডাক্তার দেখান। একাধিক অস্বাভাবিক মান পাওয়া গেছে।",
            "Tamil":   "🏥 சில நாட்களில் மருத்துவரை பாருங்கள். பல அசாதாரண மதிப்புகள்.",
            "Telugu":  "🏥 కొన్ని రోజుల్లో వైద్యుడిని చూడండి. అనేక అసాధారణ విలువలు.",
        },
        "emergency": {
            "English": "⚠️ Seek IMMEDIATE medical attention! Critical values detected. Go to hospital NOW.",
            "Hindi":   "⚠️ तुरंत चिकित्सा सहायता लें! गंभीर मान मिले। अभी अस्पताल जाएं।",
            "Marathi": "⚠️ त्वरित वैद्यकीय मदत घ्या! गंभीर मूल्ये आढळली.",
            "Bengali": "⚠️ অবিলম্বে চিকিৎসা নিন! গুরুতর মান পাওয়া গেছে।",
            "Tamil":   "⚠️ உடனே மருத்துவ உதவி! நெருக்கடியான மதிப்புகள்.",
            "Telugu":  "⚠️ వెంటనే వైద్య సహాయం పొందండి! తీవ్రమైన విలువలు.",
        },
    },
    "explanation": {
        "all_good": {
            "English": "Your {report_type} report has {total} tests — all values are within the normal range. Great news! ✅ Keep up your healthy lifestyle.",
            "Hindi":   "आपकी {report_type} रिपोर्ट में {total} जाँचें हैं — सभी सामान्य सीमा में हैं। बहुत अच्छा! ✅ स्वस्थ जीवनशैली बनाए रखें।",
            "Marathi": "तुमच्या {report_type} अहवालात {total} चाचण्या — सर्व सामान्य मर्यादेत. ✅ निरोगी राहा!",
            "Bengali": "আপনার {report_type} রিপোর্টে {total}টি পরীক্ষা — সব স্বাভাবিক। ✅",
            "Tamil":   "உங்கள் {report_type} அறிக்கையில் {total} சோதனைகள் — அனைத்தும் இயல்பு. ✅",
            "Telugu":  "మీ {report_type} నివేదికలో {total} పరీక్షలు — అన్నీ సాధారణ పరిధిలో. ✅",
        },
        "some_abnormal": {
            "English": "Your {report_type} report has {total} tests: {normal} normal ✅ and {abnormal} needing attention ⚠️. Values outside normal range: {list}. Please follow the suggestions below and consult your doctor.",
            "Hindi":   "आपकी {report_type} रिपोर्ट में {total} जाँचें: {normal} सामान्य ✅ और {abnormal} पर ध्यान जरूरी ⚠️। असामान्य: {list}। नीचे दिए सुझावों का पालन करें और डॉक्टर से मिलें।",
            "Marathi": "तुमच्या {report_type} अहवालात {total} चाचण्या: {normal} सामान्य ✅ आणि {abnormal} लक्ष द्या ⚠️। असामान्य: {list}।",
            "Bengali": "আপনার {report_type} রিপোর্টে {total}টি পরীক্ষা: {normal}টি স্বাভাবিক ✅ এবং {abnormal}টি মনোযোগ প্রয়োজন ⚠️। অস্বাভাবিক: {list}।",
            "Tamil":   "உங்கள் {report_type} அறிக்கையில் {total} சோதனைகள்: {normal} இயல்பு ✅, {abnormal} கவனம் தேவை ⚠️. இயல்பற்றவை: {list}.",
            "Telugu":  "మీ {report_type} నివేదికలో {total} పరీక్షలు: {normal} సాధారణం ✅, {abnormal} శ్రద్ధ అవసరం ⚠️. అసాధారణం: {list}.",
        },
    },
    "no_values_detected": {
        "English": "No numeric lab values could be extracted. If you uploaded a PDF, try copy-pasting the text directly in format: Hemoglobin: 12.5 g/dL",
        "Hindi":   "कोई मान नहीं मिले। PDF से टेक्स्ट सीधे इस प्रकार पेस्ट करें: Hemoglobin: 12.5 g/dL",
        "Marathi": "कोणतीही मूल्ये मिळाली नाहीत. PDF मधील मजकूर थेट पेस्ट करा.",
        "Bengali": "কোনো মান পাওয়া যায়নি। PDF থেকে টেক্সট সরাসরি পেস্ট করুন।",
        "Tamil":   "எண் மதிப்புகள் கண்டறியப்படவில்லை. PDF உரையை நேரடியாக ஒட்டவும்.",
        "Telugu":  "విలువలు కనుగొనబడలేదు. PDF నుండి టెక్స్ట్ నేరుగా paste చేయండి.",
    },
    "interim_report": {
        "English": "⚠️ This is an interim/partial report. Some results are still pending.",
        "Hindi":   "⚠️ यह एक अंतरिम/आंशिक रिपोर्ट है। कुछ परिणाम अभी भी लंबित हैं।",
        "Marathi": "⚠️ हा एक अंतरिम/आंशिक अहवाल आहे. काही निकाल अद्याप प्रलंबित आहेत.",
        "Bengali": "⚠️ এটি একটি অন্তর্বর্তী রিপোর্ট। কিছু ফলাফল এখনও বাকি।",
        "Tamil":   "⚠️ இது இடைக்கால/பகுதி அறிக்கை. சில முடிவுகள் இன்னும் நிலுவையில் உள்ளன.",
        "Telugu":  "⚠️ ఇది తాత్కాలిక నివేదిక. కొన్ని ఫలితాలు ఇంకా పెండింగ్‌లో ఉన్నాయి.",
    },

}

def get_status_label(status_key: str, language: str) -> str:
    labels = TRANSLATIONS["status_labels"].get(status_key, TRANSLATIONS["status_labels"]["Good"])
    return labels.get(language, labels["English"])

def get_value_status(status: str, language: str) -> str:
    labels = TRANSLATIONS["value_status"].get(status, TRANSLATIONS["value_status"]["Normal"])
    return labels.get(language, labels["English"])

def get_doctor_advice(advice_key: str, language: str) -> str:
    advice = TRANSLATIONS["doctor_advice"].get(advice_key, TRANSLATIONS["doctor_advice"]["good"])
    return advice.get(language, advice["English"])

def get_explanation(key: str, language: str, **kwargs) -> str:
    template = TRANSLATIONS["explanation"].get(key, {})
    text = template.get(language, template.get("English", ""))
    for k, v in kwargs.items():
        text = text.replace("{" + k + "}", str(v))
    return text
