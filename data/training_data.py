# ─────────────────────────────────────────────────────────────
# MedEasy — Training Data for Naive Bayes + TF-IDF Chatbot
# ─────────────────────────────────────────────────────────────

# ── REPORT CLASSIFIER TRAINING DATA (74 samples, 10 classes) ──
REPORT_TRAINING = [
    # CBC
    ("hemoglobin wbc rbc platelets hematocrit mcv mch mchc differential count", "CBC"),
    ("complete blood count hemoglobin white blood cell red blood cell platelet", "CBC"),
    ("hb wbc rbc plt pcv rdw neutrophil lymphocyte monocyte eosinophil", "CBC"),
    ("anemia hemoglobin low wbc count platelet count differential", "CBC"),
    ("blood count hemoglobin 12.5 wbc 8.5 rbc 4.2 platelets 210", "CBC"),
    ("full blood count fbc hemoglobin packed cell volume mcv mch", "CBC"),
    ("cbc report hemoglobin wbc platelet neutrophils lymphocytes", "CBC"),
    ("hematology report rbc count wbc differential mcv mchc rdw", "CBC"),

    # DIABETES
    ("hba1c fasting blood sugar ppbs glucose insulin diabetes", "DIABETES"),
    ("blood sugar fasting glucose hba1c post prandial diabetes mellitus", "DIABETES"),
    ("diabetes report hba1c 7.8 fasting glucose 145 ppbs 210", "DIABETES"),
    ("glycated hemoglobin blood sugar level glucose tolerance", "DIABETES"),
    ("type 2 diabetes hba1c fasting blood glucose insulin resistance", "DIABETES"),
    ("fbs ppbs hba1c diabetic control glucose monitoring", "DIABETES"),
    ("blood sugar report fasting 118 post prandial 180 hba1c 6.9", "DIABETES"),
    ("diabetic profile hba1c fasting glucose ppbs insulin", "DIABETES"),

    # LIPID
    ("cholesterol hdl ldl triglycerides lipid vldl cardiovascular", "LIPID"),
    ("lipid profile total cholesterol hdl ldl triglycerides", "LIPID"),
    ("cholesterol 220 hdl 45 ldl 155 triglycerides 185 vldl", "LIPID"),
    ("dyslipidemia cholesterol triglycerides hdl ldl ratio", "LIPID"),
    ("cardiac risk cholesterol profile ldl hdl triglycerides", "LIPID"),
    ("lipid panel cholesterol 245 ldl 168 hdl 38 trig 210", "LIPID"),
    ("fasting lipid profile total cholesterol vldl ldl hdl", "LIPID"),
    ("cholesterol report hdl ldl triglycerides cardiovascular risk", "LIPID"),

    # LFT
    ("alt ast alp bilirubin albumin total protein sgpt sgot liver", "LFT"),
    ("liver function test alt sgpt ast sgot bilirubin albumin", "LFT"),
    ("lft sgpt 55 sgot 48 alp 120 bilirubin 1.8 albumin 4.1", "LFT"),
    ("hepatic function sgpt sgot ggt bilirubin albumin liver enzymes", "LFT"),
    ("liver enzymes raised alt bilirubin albumin total protein", "LFT"),
    ("jaundice bilirubin sgpt sgot liver function hepatitis", "LFT"),
    ("liver profile alt ast alp ggt total bilirubin albumin protein", "LFT"),
    ("hepatitis liver function alt sgot bilirubin direct indirect", "LFT"),

    # KFT
    ("creatinine urea bun uric acid gfr egfr renal kidney", "KFT"),
    ("kidney function creatinine serum urea bun uric acid renal", "KFT"),
    ("kft creatinine 1.4 urea 45 uric acid 7.8 gfr 68", "KFT"),
    ("renal function test creatinine urea bun electrolytes kidney", "KFT"),
    ("ckd kidney disease creatinine urea gfr protein urine", "KFT"),
    ("creatinine serum bun uric acid renal function gfr egfr", "KFT"),
    ("kidney panel creatinine urea bun electrolytes calcium phosphorus", "KFT"),
    ("renal profile creatinine clearance uric acid urea egfr", "KFT"),

    # TFT
    ("tsh t3 t4 thyroid thyroxine triiodothyronine hypothyroid", "TFT"),
    ("thyroid function test tsh 6.8 t3 t4 thyroxine", "TFT"),
    ("tft tsh free t3 free t4 thyroid peroxidase antibody", "TFT"),
    ("hypothyroidism tsh elevated t4 low thyroid function", "TFT"),
    ("thyroid profile tsh t3 t4 free thyroxine triiodothyronine", "TFT"),
    ("hyperthyroid tsh low t3 high t4 high graves disease", "TFT"),
    ("thyroid antibodies tsh ft3 ft4 tpo anti-tg", "TFT"),
    ("thyroid panel tsh 0.2 free t4 2.1 free t3 elevated", "TFT"),

    # VITAMINS
    ("vitamin d vitamin b12 ferritin folate iron deficiency", "VITAMINS"),
    ("vit d 14 b12 158 ferritin 8 folate deficiency micronutrient", "VITAMINS"),
    ("micronutrient panel vitamin d b12 ferritin iron folate zinc", "VITAMINS"),
    ("vitamin deficiency vitamin d b12 ferritin calcium iron", "VITAMINS"),
    ("nutritional panel vit d vit b12 ferritin serum iron tibc", "VITAMINS"),
    ("vitamin d3 deficiency folate b12 iron deficiency anemia", "VITAMINS"),
    ("bone health vitamin d calcium phosphorus parathyroid", "VITAMINS"),
    ("vitamin profile b12 folate ferritin iron vit d calcium", "VITAMINS"),

    # METABOLIC
    ("sodium potassium calcium chloride magnesium electrolytes metabolic", "METABOLIC"),
    ("comprehensive metabolic panel sodium potassium calcium co2", "METABOLIC"),
    ("cmp sodium 138 potassium 4.2 calcium 9.1 chloride 101", "METABOLIC"),
    ("electrolyte panel sodium potassium chloride bicarbonate", "METABOLIC"),
    ("basic metabolic panel sodium potassium glucose creatinine", "METABOLIC"),
    ("electrolytes sodium potassium calcium phosphorus magnesium", "METABOLIC"),
    ("bmp glucose bun creatinine sodium potassium chloride co2", "METABOLIC"),
    ("serum electrolytes sodium potassium chloride bicarbonate calcium", "METABOLIC"),

    # URINE
    ("urine protein glucose pH specific gravity wbc rbc casts", "URINE"),
    ("urinalysis urine routine microscopy protein glucose ketone", "URINE"),
    ("urine examination protein nil glucose nil wbc 2-3 rbc", "URINE"),
    ("urine culture sensitivity uti bacteria colony count", "URINE"),
    ("urine rm urine protein microscopy casts epithelial cells", "URINE"),
    ("24 hour urine protein creatinine clearance microalbuminuria", "URINE"),

    # CARDIAC
    ("troponin ck-mb ldh ecg cardiac enzymes heart attack", "CARDIAC"),
    ("cardiac markers troponin i ck-mb 2d echo ejection fraction", "CARDIAC"),
    ("bnp pro-bnp heart failure cardiac troponin elevated", "CARDIAC"),
    ("ecg tmt exercise stress test chest pain cardiac enzymes", "CARDIAC"),
    ("troponin 0.08 ck-mb elevated myocardial infarction", "CARDIAC"),
    ("cardiac panel troponin ck-mb ldh bnp heart biomarkers", "CARDIAC"),
]

# ── CHATBOT INTENT TRAINING DATA (119 examples, 7 intents) ──
CHATBOT_INTENTS = {
    "greeting": [
        "hello", "hi", "hey", "good morning", "namaste",
        "howdy", "hi there", "hey there", "hii", "heyy",
    ],
    "explain_term": [
        "what is hba1c", "what does wbc mean", "explain hemoglobin",
        "what is creatinine", "define platelet", "what is tsh",
        "what does ldl mean", "tell me about cholesterol", "explain vitamin d",
        "what is ferritin", "meaning of alt", "what is troponin",
        "explain uric acid", "what does albumin mean", "what is triglycerides",
        "what is bilirubin", "explain esr", "what is crp", "what is bun",
        "what is mcv", "what does rbc stand for", "what is sodium",
        "what is potassium", "explain calcium", "what is hematocrit",
        "define lymphocytes",
    ],
    "normal_range": [
        "what is normal range for hemoglobin", "is 7.8 hba1c normal",
        "normal blood sugar", "normal wbc count", "normal cholesterol level",
        "hemoglobin normal value", "glucose normal level",
        "platelet count normal range", "creatinine normal value",
        "normal tsh level", "normal vitamin d level", "what should b12 be",
        "normal triglycerides", "normal alt level", "normal range for",
        "what is the normal", "what is normal ferritin", "normal uric acid level",
        "normal sodium level", "normal potassium level", "what is normal bilirubin",
    ],
    "report_summary": [
        "what does my report say", "summarize my report", "what are my results",
        "explain my report", "what is wrong", "which values abnormal",
        "what values are high", "what is low", "overall health status",
        "is my report good or bad", "tell me about my report", "analyze my results",
    ],
    "health_advice": [
        "should i see a doctor", "is this serious", "what should i do",
        "how to improve health", "what food should i eat",
        "how to reduce cholesterol", "how to control blood sugar",
        "how to improve hemoglobin", "what to eat for iron deficiency",
        "how to reduce uric acid", "tips to improve", "how to lower creatinine",
        "lifestyle changes", "diet advice", "home remedy", "what exercise",
        "how to increase platelets", "how to control thyroid",
        "foods for liver health", "how to lower triglycerides",
        "remedies for vitamin d deficiency",
    ],
    "urgent_symptoms": [
        "chest pain", "difficulty breathing", "feeling dizzy",
        "very weak", "heart racing", "cannot breathe", "severe headache",
        "vomiting blood", "numbness in arm", "sweating a lot",
        "feeling faint", "unconscious",
    ],
    "farewell": [
        "bye", "goodbye", "see you", "thanks", "thank you",
        "that is all", "done", "ok thanks", "all good", "appreciate it",
        "thank you so much", "no more questions", "great help",
        "perfect", "nothing else", "you were helpful", "that is everything",
    ],
}

# ── REPORT TYPE CATEGORIES ────────────────────────────────────
REPORT_TYPES = [
    {"name": "CBC - Complete Blood Count",          "keys": ["hemoglobin", "wbc", "rbc", "platelets", "hematocrit", "mcv"],              "primary": ["hemoglobin", "wbc", "platelets"]},
    {"name": "Diabetes / Sugar Panel",              "keys": ["hba1c", "glucose", "fbs", "ppbs", "insulin", "diabetes"],                  "primary": ["hba1c", "fbs", "ppbs", "diabetes"]},
    {"name": "Lipid Profile",                       "keys": ["cholesterol", "hdl", "ldl", "triglycerides", "lipid"],                     "primary": ["hdl", "ldl", "triglycerides"]},
    {"name": "Liver Function Test (LFT)",           "keys": ["alt", "ast", "alp", "bilirubin", "albumin", "sgpt", "sgot"],               "primary": ["sgpt", "sgot", "bilirubin"]},
    {"name": "Kidney Function Test (KFT)",          "keys": ["creatinine", "urea", "bun", "uric acid", "gfr", "renal"],                  "primary": ["creatinine", "urea", "bun"]},
    {"name": "Thyroid Function Test (TFT)",         "keys": ["tsh", "t3", "t4", "thyroxine", "thyroid"],                                 "primary": ["tsh", "thyroid"]},
    {"name": "Vitamin & Mineral Panel",             "keys": ["vitamin d", "vitamin b12", "ferritin", "folate", "vit d", "vit b12"],       "primary": ["vitamin d", "vitamin b12", "ferritin"]},
    {"name": "Comprehensive Metabolic Panel",       "keys": ["sodium", "potassium", "calcium", "magnesium", "chloride"]},
    {"name": "Urine Analysis",                      "keys": ["urine", "protein", "specific gravity", "urinalysis", "ketone"]},
    {"name": "Cardiac Report",                      "keys": ["troponin", "ck-mb", "bnp", "ldh", "cardiac", "ecg"],                              "primary": ["troponin", "cardiac"]},
    # ── New panel types for real-world reports ──
    {"name": "Comprehensive Full Body Panel", "keys": ["comprehensive", "full body", "microalbumin", "homocysteine", "ige", "psa", "electrolyte", "thyroid", "lipid", "liver", "kidney", "rdw", "esr", "alkaline phosphatase", "iron serum"], "primary": ["comprehensive", "full body", "microalbumin", "homocysteine", "ige", "psa"]},
    {"name": "Heart Health Screen",                 "keys": ["apolipoprotein", "hsCRP", "lipoprotein", "glucose fasting", "cardio"], "primary": ["apolipoprotein", "hsCRP"]},
    {"name": "Lipid Profile Advanced",              "keys": ["non-hdl", "vldl", "ldl direct", "apolipoprotein b", "lipoprotein a"], "primary": ["apolipoprotein b", "lipoprotein a"]},
]
