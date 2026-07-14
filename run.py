"""
MedEasy - Medical Report Simplification System
Run with: python run.py
Then open: http://localhost:5000
"""
from app import app

if __name__ == "__main__":
    print("=" * 55)
    print("  MedEasy - Medical Report Simplification System")
    print("=" * 55)
    print("  Server  : http://localhost:5000")
    print("  API Docs: http://localhost:5000/how-it-works")
    print("=" * 55)
    app.run(debug=True, host="0.0.0.0", port=5000)
