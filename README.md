# MedEasy — Medical Report Simplification System

AI-powered system that converts complex medical lab reports into plain language across 6 Indian languages.

## Quick Start

```bash
pip install flask numpy pdfplumber python-docx werkzeug requests
python run.py
# Open http://localhost:5000
```

## Project Structure

```
medeasy/
├── run.py                    Start server
├── app.py                    Flask API (all routes)
├── requirements.txt
├── nlp/
│   ├── pipeline.py           Master orchestrator (5-stage NLP)
│   ├── tokenizer.py          PDF text normalization
│   ├── ner.py                Named Entity Recognition
│   ├── lab_extractor.py      Lab value extraction + classification
│   └── simplifier.py         Plain language + translation
├── models/
│   ├── tfidf.py              TF-IDF vectorizer (NumPy from scratch)
│   ├── naive_bayes.py        Naive Bayes classifier (from scratch)
│   ├── classifier.py         Report type classifier
│   └── chatbot_engine.py     Intent engine + AI API routing
├── data/
│   ├── lab_ranges.py         50+ tests with normal ranges
│   ├── medical_terms.py      70+ term definitions
│   ├── training_data.py      74 classifier + 119 chatbot samples
│   └── translations.py       6-language templates
├── database/db.py            SQLite: users + reports
├── templates/index.html      Full UI
└── static/css+js             Styles + frontend logic
```

## API Routes

| Method | Route | Description |
|--------|-------|-------------|
| POST | /api/analyze | Analyze report (text or file) |
| POST | /api/chat | MedBot chatbot |
| POST | /api/auth/signup | Register |
| POST | /api/auth/login | Login |
| GET  | /api/history | Report history |
| POST | /api/report/save | Save report |

## MedBot — Free AI Keys

Get a free Groq key at console.groq.com (no credit card needed).
