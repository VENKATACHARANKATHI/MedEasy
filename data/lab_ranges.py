# ─────────────────────────────────────────────────────────────
# MedEasy — Lab Ranges Knowledge Base
# Source: WHO, ICMR standard reference intervals
# ─────────────────────────────────────────────────────────────

LAB_RANGES = {
    # ── COMPLETE BLOOD COUNT ──────────────────────────────────
    "hemoglobin": {
        "name": "Hemoglobin", "unit": "g/dL",
        "male": [13.5, 17.5], "female": [12.0, 15.5], "gen": [12.0, 17.5],
        "critL": 7.0, "critH": 20.0,
        "suggL": "low_hb", "suggH": None, "urgent": False,
    },
    "haemoglobin": {"alias": "hemoglobin"},
    "hgb":         {"alias": "hemoglobin"},
    "hb":          {"alias": "hemoglobin"},

    "wbc": {
        "name": "WBC", "unit": "x10³/µL",
        "gen": [4.0, 10.0], "critL": 2.0, "critH": 30.0,
        "suggL": "low_wbc", "suggH": "high_wbc", "urgent": False,
    },
    "white blood cell": {"alias": "wbc"},
    "total wbc":        {"alias": "wbc"},
    "wbc count":        {"alias": "wbc"},

    "rbc": {
        "name": "RBC", "unit": "x10⁶/µL",
        "male": [4.5, 5.9], "female": [4.1, 5.1], "gen": [4.1, 5.9],
    },
    "rbc count": {"alias": "rbc"},

    "platelets": {
        "name": "Platelets", "unit": "x10³/µL",
        "gen": [150, 400], "critL": 50, "critH": 1000,
        "urgent": False,
    },
    "plt":           {"alias": "platelets"},
    "platelet count": {"alias": "platelets"},

    "hematocrit": {
        "name": "Hematocrit", "unit": "%",
        "male": [41, 53], "female": [36, 46], "gen": [36, 53],
    },
    "pcv": {"alias": "hematocrit"},

    "mcv": {"name": "MCV", "unit": "fL", "gen": [80, 100]},
    "mch": {"name": "MCH", "unit": "pg", "gen": [27, 33]},
    "mchc": {"name": "MCHC", "unit": "g/dL", "gen": [32, 36]},
    "rdw": {"name": "RDW", "unit": "%", "gen": [11.5, 14.5]},

    "neutrophils": {"name": "Neutrophils", "unit": "%", "gen": [40, 70]},
    "lymphocytes": {"name": "Lymphocytes", "unit": "%", "gen": [20, 40]},
    "monocytes":   {"name": "Monocytes", "unit": "%", "gen": [2, 8]},
    "eosinophils": {"name": "Eosinophils", "unit": "%", "gen": [1, 4]},
    "basophils":   {"name": "Basophils", "unit": "%", "gen": [0, 1]},

    # ── DIABETES / SUGAR ─────────────────────────────────────
    "glucose": {
        "name": "Fasting Glucose", "unit": "mg/dL",
        "gen": [70, 99], "critL": 40, "critH": 500,
        "suggH": "high_sugar", "urgent": False,
    },
    "fasting glucose":     {"alias": "glucose"},
    "fasting blood sugar": {"alias": "glucose"},
    "fbs":                 {"alias": "glucose"},
    "blood sugar fasting": {"alias": "glucose"},

    "hba1c": {
        "name": "HbA1c", "unit": "%",
        "gen": [4.0, 5.6], "critH": 14.0,
        "suggH": "high_sugar", "urgent": False,
    },
    "glycated hemoglobin":    {"alias": "hba1c"},
    "glycosylated hemoglobin":{"alias": "hba1c"},

    "ppbs": {
        "name": "Post-Prandial Blood Sugar", "unit": "mg/dL",
        "gen": [70, 140], "suggH": "high_sugar",
    },
    "post prandial blood sugar": {"alias": "ppbs"},
    "post prandial glucose":     {"alias": "ppbs"},

    # ── LIPID PROFILE ─────────────────────────────────────────
    "cholesterol": {
        "name": "Total Cholesterol", "unit": "mg/dL",
        "gen": [0, 200], "suggH": "high_chol",
    },
    "total cholesterol": {"alias": "cholesterol"},
    "s. cholesterol":    {"alias": "cholesterol"},

    "hdl": {
        "name": "HDL Cholesterol", "unit": "mg/dL",
        "male": [40, 999], "female": [50, 999], "gen": [40, 999],
        "suggL": "low_hdl",
    },
    "hdl cholesterol": {"alias": "hdl"},

    "ldl": {
        "name": "LDL Cholesterol", "unit": "mg/dL",
        "gen": [0, 100], "suggH": "high_chol",
    },
    "ldl cholesterol": {"alias": "ldl"},

    "triglycerides": {
        "name": "Triglycerides", "unit": "mg/dL",
        "gen": [0, 150], "suggH": "high_trig",
    },
    "tgl":  {"alias": "triglycerides"},
    "trig": {"alias": "triglycerides"},
    "vldl": {"name": "VLDL", "unit": "mg/dL", "gen": [0, 30]},

    # ── LIVER FUNCTION ────────────────────────────────────────
    "alt": {
        "name": "ALT (SGPT)", "unit": "U/L",
        "gen": [0, 50], "suggH": "high_liver",
    },
    "sgpt": {"alias": "alt"},

    "ast": {
        "name": "AST (SGOT)", "unit": "U/L",
        "gen": [0, 45], "suggH": "high_liver",
    },
    "sgot": {"alias": "ast"},

    "alp": {
        "name": "ALP", "unit": "U/L",
        "gen": [44, 147], "suggH": "high_liver",
    },
    "alkaline phosphatase": {"alias": "alp"},

    "ggt": {"name": "GGT", "unit": "U/L", "gen": [0, 45], "suggH": "high_liver"},

    "bilirubin": {
        "name": "Total Bilirubin", "unit": "mg/dL",
        "gen": [0.2, 1.2], "critH": 15.0, "suggH": "high_bili",
    },
    "total bilirubin":  {"alias": "bilirubin"},
    "t. bilirubin":     {"alias": "bilirubin"},
    "serum bilirubin":  {"alias": "bilirubin"},

    "direct bilirubin":   {"name": "Direct Bilirubin", "unit": "mg/dL", "gen": [0.0, 0.3]},
    "indirect bilirubin": {"name": "Indirect Bilirubin", "unit": "mg/dL", "gen": [0.1, 0.8]},

    "albumin": {
        "name": "Albumin", "unit": "g/dL",
        "gen": [3.4, 5.4], "critL": 2.0,
    },
    "serum albumin": {"alias": "albumin"},

    "total protein": {"name": "Total Protein", "unit": "g/dL", "gen": [6.0, 8.3]},

    # ── KIDNEY FUNCTION ───────────────────────────────────────
    "creatinine": {
        "name": "Creatinine", "unit": "mg/dL",
        "male": [0.7, 1.2], "female": [0.5, 1.0], "gen": [0.5, 1.2],
        "critH": 10.0, "suggH": "high_creat",
    },
    "s. creatinine":     {"alias": "creatinine"},
    "serum creatinine":  {"alias": "creatinine"},

    "bun": {
        "name": "BUN", "unit": "mg/dL",
        "gen": [7, 20], "suggH": "high_creat",
    },
    "blood urea nitrogen": {"alias": "bun"},

    "urea": {
        "name": "Urea", "unit": "mg/dL",
        "gen": [19, 44], "suggH": "high_creat",
    },
    "serum urea":  {"alias": "urea"},
    "blood urea":  {"alias": "urea"},

    "uric acid": {
        "name": "Uric Acid", "unit": "mg/dL",
        "male": [3.5, 7.2], "female": [2.6, 6.0], "gen": [2.6, 7.2],
        "suggH": "high_uric",
    },
    "s. uric acid":    {"alias": "uric acid"},
    "serum uric acid": {"alias": "uric acid"},

    # ── THYROID ───────────────────────────────────────────────
    "tsh": {
        "name": "TSH", "unit": "mIU/L",
        "gen": [0.4, 4.0], "suggH": "high_tsh",
    },
    "thyroid stimulating hormone": {"alias": "tsh"},

    "t3": {"name": "T3 (Triiodothyronine)", "unit": "ng/mL", "gen": [0.58, 1.59]},
    "free t3": {"alias": "t3"},

    "t4": {"name": "T4 (Thyroxine)", "unit": "µg/dL", "gen": [5.0, 12.0]},
    "free t4":  {"alias": "t4"},
    "thyroxine":{"alias": "t4"},

    # ── VITAMINS & MINERALS ───────────────────────────────────
    "vitamin d": {
        "name": "Vitamin D", "unit": "ng/mL",
        "gen": [30, 100], "critL": 10, "suggL": "low_vitd",
    },
    "vit d":            {"alias": "vitamin d"},
    "vitamin d total":  {"alias": "vitamin d"},
    "25-oh vitamin d":  {"alias": "vitamin d"},
    "25 oh vitamin d":  {"alias": "vitamin d"},

    "vitamin b12": {
        "name": "Vitamin B12", "unit": "pg/mL",
        "gen": [200, 900], "critL": 100, "suggL": "low_b12",
    },
    "vit b12":       {"alias": "vitamin b12"},
    "cyanocobalamin":{"alias": "vitamin b12"},

    "ferritin": {
        "name": "Ferritin", "unit": "ng/mL",
        "male": [12, 300], "female": [12, 150], "gen": [12, 300],
        "critL": 5, "suggL": "low_ferr",
    },
    "serum ferritin": {"alias": "ferritin"},

    "folate": {"name": "Folate", "unit": "ng/mL", "gen": [2.7, 17.0]},
    "folic acid": {"alias": "folate"},

    "iron": {"name": "Serum Iron", "unit": "µg/dL", "male": [65, 175], "female": [50, 170], "gen": [50, 175]},
    "tibc": {"name": "TIBC", "unit": "µg/dL", "gen": [250, 370]},

    # ── ELECTROLYTES ─────────────────────────────────────────
    "sodium": {
        "name": "Sodium", "unit": "mEq/L",
        "gen": [136, 145], "critL": 120, "critH": 160, "urgent": True,
    },
    "serum sodium": {"alias": "sodium"},

    "potassium": {
        "name": "Potassium", "unit": "mEq/L",
        "gen": [3.5, 5.0], "critL": 2.5, "critH": 6.5, "urgent": True,
    },
    "serum potassium": {"alias": "potassium"},

    "calcium": {
        "name": "Calcium", "unit": "mg/dL",
        "gen": [8.5, 10.5], "critL": 6.0, "critH": 13.0, "urgent": True,
    },
    "serum calcium": {"alias": "calcium"},

    "chloride":   {"name": "Chloride", "unit": "mEq/L", "gen": [98, 107]},
    "magnesium":  {"name": "Magnesium", "unit": "mg/dL", "gen": [1.7, 2.2]},
    "phosphorus": {"name": "Phosphorus", "unit": "mg/dL", "gen": [2.5, 4.5]},

    # ── INFLAMMATION ─────────────────────────────────────────
    "esr": {
        "name": "ESR", "unit": "mm/hr",
        "male": [0, 15], "female": [0, 20], "gen": [0, 20],
    },
    "erythrocyte sedimentation rate": {"alias": "esr"},

    "crp": {"name": "CRP", "unit": "mg/L", "gen": [0, 10]},
    "c-reactive protein": {"alias": "crp"},
    "c reactive protein": {"alias": "crp"},

    # ── CARDIAC ──────────────────────────────────────────────
    "troponin": {
        "name": "Troponin I", "unit": "ng/mL",
        "gen": [0, 0.04], "critH": 0.04, "urgent": True,
    },
    "troponin i": {"alias": "troponin"},
    "troponin t": {"name": "Troponin T", "unit": "ng/mL", "gen": [0, 0.01], "critH": 0.01, "urgent": True},

    "ck-mb": {"name": "CK-MB", "unit": "U/L", "gen": [0, 25]},
    "ldh":   {"name": "LDH", "unit": "U/L", "gen": [140, 280]},
    "bnp":   {"name": "BNP", "unit": "pg/mL", "gen": [0, 100], "urgent": True},

    # ── URINE ────────────────────────────────────────────────
    "urine protein":   {"name": "Urine Protein", "unit": "mg/dL", "gen": [0, 14]},
    "urine glucose":   {"name": "Urine Glucose", "unit": "mg/dL", "gen": [0, 0]},
    "urine ph":        {"name": "Urine pH", "unit": "", "gen": [4.5, 8.5]},
    "specific gravity":{"name": "Specific Gravity", "unit": "", "gen": [1.003, 1.030]},
    # ── CARDIAC ADVANCED ─────────────────────────────────────────
    "apolipoprotein b": {
        "name": "Apolipoprotein B (ApoB)", "unit": "mg/dL",
        "gen": [46, 174], "suggH": "high_chol", "suggL": None,
    },
    "apo b":                   {"alias": "apolipoprotein b"},
    "apolipoprotein b apo b":  {"alias": "apolipoprotein b"},
    "hsCRP": {
        "name": "Cardio CRP (hsCRP)", "unit": "mg/L",
        "gen": [0, 0.99], "critH": 10.0, "suggH": "high_crp", "urgent": False,
    },
    "cardio c-reactive protein": {"alias": "hsCRP"},
    "cardio crp":                {"alias": "hsCRP"},
    "hs-crp":                    {"alias": "hsCRP"},
    "lipoprotein a": {
        "name": "Lipoprotein(a) Lp(a)", "unit": "mg/dL",
        "gen": [0, 20], "suggH": "high_chol",
    },
    "lp a":       {"alias": "lipoprotein a"},
    "lp a serum": {"alias": "lipoprotein a"},
    # ── EXTENDED LIPID ────────────────────────────────────────────
    "non-hdl cholesterol": {
        "name": "Non-HDL Cholesterol", "unit": "mg/dL",
        "gen": [0, 130], "suggH": "high_chol",
    },
    "non hdl": {"alias": "non-hdl cholesterol"},
    "vldl cholesterol": {
        "name": "VLDL Cholesterol", "unit": "mg/dL",
        "gen": [0, 30], "suggH": "high_trig",
    },
    "vldl":                       {"alias": "vldl cholesterol"},
    "ldl cholesterol direct":     {"alias": "ldl"},
    "ldl direct":                 {"alias": "ldl"},
    "ldl cholesterol calculated": {"alias": "ldl"},
    # ── DIABETES EXTENDED ─────────────────────────────────────────
    "estimated average glucose": {
        "name": "Estimated Average Glucose (eAG)", "unit": "mg/dL",
        "gen": [70, 99], "suggH": "high_sugar",
    },
    "eag":                           {"alias": "estimated average glucose"},
    "glucose fasting":               {"alias": "glucose"},
    "glucose fasting f plasma":      {"alias": "glucose"},
    "hba1c glycosylated hemoglobin": {"alias": "hba1c"},
    # ── HIGH SENSITIVITY TROPONIN ─────────────────────────────────
    "hs troponin": {
        "name": "High Sensitivity Troponin", "unit": "ng/mL",
        "gen": [0, 0.04], "critH": 0.04, "urgent": True,
    },
    "hs-troponin":               {"alias": "hs troponin"},
    "troponin i high sensitive": {"alias": "hs troponin"},

}

# ── HEALTH SUGGESTIONS ─────────────────────────────────────
SUGGESTIONS = {
    "high_sugar": {
        "icon": "🍬",
        "title": "Control Blood Sugar",
        "detail": "Reduce sugary foods and refined carbohydrates. Eat more vegetables, whole grains, and fiber. Walk 30 minutes daily. Monitor your blood sugar regularly and follow your doctor's medication plan."
    },
    "low_hb": {
        "icon": "🥗",
        "title": "Increase Iron Intake",
        "detail": "Eat iron-rich foods: spinach, lentils, red meat, beetroot, pomegranate, jaggery. Take iron supplements if advised by your doctor. Pair iron-rich foods with Vitamin C for better absorption."
    },
    "high_chol": {
        "icon": "🫀",
        "title": "Heart-Healthy Diet",
        "detail": "Avoid fried foods, butter, processed snacks, and full-fat dairy. Eat oats, nuts, fish, olive oil, and fruits. Exercise 5 days per week and maintain a healthy weight."
    },
    "high_creat": {
        "icon": "💧",
        "title": "Protect Your Kidneys",
        "detail": "Drink 8–10 glasses of water daily. Reduce salt and protein intake. Avoid NSAIDs (painkillers like ibuprofen) without doctor advice. Control blood pressure and diabetes."
    },
    "high_uric": {
        "icon": "🦴",
        "title": "Manage Uric Acid (Gout)",
        "detail": "Avoid red meat, organ meats, shellfish, and alcohol. Drink plenty of water (3L/day). Eat cherries, low-fat dairy, and vegetables. Lose weight if overweight."
    },
    "high_wbc": {
        "icon": "🦠",
        "title": "Possible Infection — See Doctor",
        "detail": "High WBC usually means your body is fighting an infection or inflammation. Rest, stay hydrated, and see your doctor promptly. If you have fever, this is urgent."
    },
    "low_wbc": {
        "icon": "🛡️",
        "title": "Boost Immunity",
        "detail": "Low WBC means reduced infection-fighting ability. Eat zinc-rich foods (pumpkin seeds, chickpeas), get adequate sleep (8 hours), avoid crowds during illness, and follow up with your doctor."
    },
    "high_tsh": {
        "icon": "🦋",
        "title": "Thyroid Care (Hypothyroidism)",
        "detail": "High TSH suggests underactive thyroid. Eat iodine-rich foods (iodized salt, fish, dairy). Take thyroid medication exactly as prescribed. Get TSH checked every 6 months."
    },
    "low_vitd": {
        "icon": "☀️",
        "title": "Increase Vitamin D",
        "detail": "Spend 15–20 minutes in morning sunlight (before 10 AM) daily. Eat fatty fish, egg yolks, and fortified dairy. Ask your doctor about Vitamin D3 supplements (1000–2000 IU/day)."
    },
    "low_b12": {
        "icon": "🥩",
        "title": "Increase Vitamin B12",
        "detail": "Eat eggs, dairy, meat, fish, and fortified cereals. Vegetarians and vegans should take B12 supplements (500–1000 µg daily). B12 deficiency causes fatigue, numbness, and memory issues."
    },
    "high_bili": {
        "icon": "🟡",
        "title": "Liver Health — See Doctor",
        "detail": "High bilirubin may indicate jaundice, liver stress, or bile duct blockage. Avoid alcohol completely. Eat light, easily digestible foods. See your doctor promptly — this needs investigation."
    },
    "high_liver": {
        "icon": "🫀",
        "title": "Protect Your Liver",
        "detail": "Elevated liver enzymes suggest liver stress. Avoid alcohol and fatty foods. Eat turmeric, garlic, leafy greens, and fruits. Avoid unnecessary medications. See your doctor for further evaluation."
    },
    "low_ferr": {
        "icon": "🩸",
        "title": "Iron Deficiency",
        "detail": "Low ferritin means depleted iron stores — often precedes anemia. Eat spinach, lentils, jaggery, red meat, and fortified cereals. Take iron supplements with orange juice (Vitamin C improves absorption)."
    },
    "high_trig": {
        "icon": "🐟",
        "title": "Lower Triglycerides",
        "detail": "Cut sugar, alcohol, white bread, and refined carbs. Eat omega-3 rich foods: fish (salmon, mackerel), flaxseed, walnuts. Exercise regularly. Lose weight if overweight."
    },
    "low_hdl": {
        "icon": "💪",
        "title": "Boost Good Cholesterol (HDL)",
        "detail": "Exercise regularly — even a 30-minute walk helps. Eat avocados, olive oil, nuts, and fatty fish. Quit smoking if you smoke. Reduce refined carbohydrates."
    },
    "ok": {
        "icon": "✅",
        "title": "All Results Normal — Keep It Up!",
        "detail": "Your results are within healthy ranges. Maintain a balanced diet, stay active (30 min/day), drink 8 glasses of water, sleep 7–8 hours, and get regular checkups every 6–12 months."
    },
}


# ══════════════════════════════════════════════════════════════
# NEW ENTRIES — Added for real-world lab report compatibility
# ══════════════════════════════════════════════════════════════

_NEW_LAB = {
    # ── CARDIAC ADVANCED ─────────────────────────────────────────
    "apolipoprotein b": {
        "name": "Apolipoprotein B (ApoB)", "unit": "mg/dL",
        "gen": [46, 174], "suggH": "high_chol", "suggL": None,
    },
    "apo b":                   {"alias": "apolipoprotein b"},
    "apolipoprotein b apo b":  {"alias": "apolipoprotein b"},

    "hsCRP": {
        "name": "Cardio CRP (hsCRP)", "unit": "mg/L",
        "gen": [0, 0.99], "critH": 10.0, "suggH": "high_crp", "urgent": False,
    },
    "cardio c-reactive protein": {"alias": "hsCRP"},
    "cardio crp":                {"alias": "hsCRP"},
    "hs-crp":                    {"alias": "hsCRP"},
    "high sensitivity crp":      {"alias": "hsCRP"},

    "lipoprotein a": {
        "name": "Lipoprotein(a) — Lp(a)", "unit": "mg/dL",
        "gen": [0, 20], "suggH": "high_chol",
    },
    "lp a":       {"alias": "lipoprotein a"},
    "lp a serum": {"alias": "lipoprotein a"},

    # ── EXTENDED LIPID ────────────────────────────────────────────
    "non-hdl cholesterol": {
        "name": "Non-HDL Cholesterol", "unit": "mg/dL",
        "gen": [0, 130], "suggH": "high_chol",
    },
    "non hdl cholesterol": {"alias": "non-hdl cholesterol"},
    "non hdl":             {"alias": "non-hdl cholesterol"},

    "vldl cholesterol": {
        "name": "VLDL Cholesterol", "unit": "mg/dL",
        "gen": [0, 30], "suggH": "high_trig",
    },
    "vldl":                       {"alias": "vldl cholesterol"},
    "ldl cholesterol direct":     {"alias": "ldl"},
    "ldl direct":                 {"alias": "ldl"},
    "ldl cholesterol calculated": {"alias": "ldl"},

    # ── DIABETES EXTENDED ─────────────────────────────────────────
    "estimated average glucose": {
        "name": "Estimated Average Glucose (eAG)", "unit": "mg/dL",
        "gen": [70, 99], "suggH": "high_sugar",
    },
    "eag":                           {"alias": "estimated average glucose"},
    "glucose fasting":               {"alias": "glucose"},
    "glucose fasting f plasma":      {"alias": "glucose"},
    "hba1c glycosylated hemoglobin": {"alias": "hba1c"},
    "glycated hemoglobin":           {"alias": "hba1c"},

    # ── HIGH SENSITIVITY TROPONIN ─────────────────────────────────
    "hs troponin": {
        "name": "High Sensitivity Troponin I", "unit": "ng/mL",
        "gen": [0, 0.04], "critH": 0.04, "urgent": True,
    },
    "hs-troponin":               {"alias": "hs troponin"},
    "troponin i high sensitive": {"alias": "hs troponin"},
    "troponin i serum high sensitive": {"alias": "hs troponin"},
}

LAB_RANGES.update(_NEW_LAB)

# ── NEW SUGGESTIONS ───────────────────────────────────────────────
SUGGESTIONS["high_crp"] = {
    "icon": "❤️",
    "title": "Elevated Cardio CRP — Cardiovascular Risk",
    "detail": (
        "High-sensitivity CRP above 1.0 mg/L indicates cardiovascular inflammation risk. "
        "Eat anti-inflammatory foods (fish, turmeric, olive oil, berries), exercise 30 min/day, "
        "avoid smoking, maintain healthy weight. Retest in 2-3 weeks. "
        "Discuss statin therapy with your doctor if persistently elevated."
    ),
}


# ── ADDITIONAL TESTS for real-world comprehensive reports ─────
_NEW_TESTS_2 = {
    "homocysteine": {
        "name": "Homocysteine", "unit": "µmol/L",
        "gen": [5.0, 15.0], "critH": 30.0, "suggH": "high_homocys",
    },
    "serum homocysteine": {"alias": "homocysteine"},
    "homocysteine serum": {"alias": "homocysteine"},

    "ige": {
        "name": "IgE (Total)", "unit": "IU/mL",
        "gen": [0, 100], "suggH": "high_ige",
    },
    "total ige": {"alias": "ige"},
    "immunoglobulin e": {"alias": "ige"},

    "mpv": {
        "name": "Mean Platelet Volume (MPV)", "unit": "fL",
        "gen": [7.5, 12.5],
    },
    "mean platelet volume": {"alias": "mpv"},

    "psa": {
        "name": "PSA (Prostate Specific Antigen)", "unit": "ng/mL",
        "gen": [0, 4.0], "suggH": "see_doctor",
    },
    "psa prostate specific antigen total": {"alias": "psa"},
    "prostate specific antigen": {"alias": "psa"},

    "rdw sd": {
        "name": "RDW-SD", "unit": "fL",
        "gen": [39, 46],
    },
    "rdw-sd": {"alias": "rdw sd"},

    "rdw cv": {
        "name": "RDW-CV", "unit": "%",
        "gen": [11.6, 14.0],
    },
    "rdw-cv": {"alias": "rdw cv"},
    "rdw": {"alias": "rdw cv"},

    "mchc": {
        "name": "MCHC", "unit": "g/dL",
        "gen": [31.5, 36.5],
    },

    "hematocrit": {
        "name": "Hematocrit (PCV)", "unit": "%",
        "male": [40, 52], "female": [36, 48], "gen": [36, 52],
    },
    "pcv": {"alias": "hematocrit"},
    "packed cell volume": {"alias": "hematocrit"},

    "rbc": {
        "name": "RBC Count", "unit": "million/cmm",
        "male": [4.5, 5.9], "female": [4.0, 5.2], "gen": [4.0, 5.9],
    },
    "rbc count": {"alias": "rbc"},
    "red blood cell": {"alias": "rbc"},

    "hb a": {
        "name": "Haemoglobin A (HbA)", "unit": "%",
        "gen": [96.0, 98.5],
    },
    "hb a2": {
        "name": "Haemoglobin A2 (HbA2)", "unit": "%",
        "gen": [2.0, 3.5], "critH": 3.5, "suggH": "thalassemia",
    },

    "microalbumin": {
        "name": "Microalbumin", "unit": "mg/L",
        "gen": [0, 20], "suggH": "kidney_monitor",
    },
    "microalbumin per urine volume": {"alias": "microalbumin"},
    "urinary microalbumin": {"alias": "microalbumin"},

    "phosphorus": {
        "name": "Phosphorus (Serum)", "unit": "mg/dL",
        "gen": [2.3, 4.7],
    },
    "phosphorus serum": {"alias": "phosphorus"},
    "serum phosphorus": {"alias": "phosphorus"},
}

LAB_RANGES.update(_NEW_TESTS_2)

# New suggestions
SUGGESTIONS["high_homocys"] = {
    "icon": "🧬",
    "title": "Elevated Homocysteine — Cardiovascular Risk",
    "detail": (
        "Homocysteine above 15 µmol/L increases risk of heart disease, stroke, and blood clots. "
        "Increase intake of folate (leafy greens, legumes), Vitamin B6 (chicken, fish, bananas), "
        "and Vitamin B12. Avoid smoking and excessive alcohol. Consult your doctor about B-complex supplements."
    ),
}
SUGGESTIONS["high_ige"] = {
    "icon": "🤧",
    "title": "Elevated IgE — Allergy/Immune Response",
    "detail": (
        "High IgE (>100 IU/mL) suggests allergic disease, asthma, or parasitic infection. "
        "Identify and avoid triggers. Consider allergy testing. "
        "Consult a doctor for antihistamines or allergy management plan."
    ),
}
SUGGESTIONS["thalassemia"] = {
    "icon": "🧬",
    "title": "Abnormal Hemoglobin Pattern — Thalassemia Screening",
    "detail": (
        "Abnormal HbA2 levels may indicate thalassemia trait. "
        "DNA analysis is recommended to confirm. Genetic counselling advised for family planning. "
        "Consult a haematologist."
    ),
}
