"""MedEasy Flask Application - All API Routes"""
import os, io, json
from flask import Flask, request, jsonify, session, render_template, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps

from nlp.pipeline import MedEasyPipeline
from models.chatbot_engine import ChatbotEngine, OLLAMA_BASE_URL, OLLAMA_MODEL
from database.db import (
    init_db, create_user, get_user_by_email, get_user_by_id,
    update_user, delete_user, save_report, get_user_reports,
    get_report_by_id, delete_report, get_report_stats,
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "medeasy-dev-secret-2025")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
ALLOWED = {"pdf","txt","docx","doc","rtf","csv","md"}

pipeline = MedEasyPipeline()
chatbot  = ChatbotEngine()
init_db()

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)
    return decorated

def extract_text(file):
    ext = file.filename.rsplit(".",1)[-1].lower() if "." in file.filename else "txt"
    if ext == "pdf":
        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(file.read())) as pdf:
                return "\n".join(p.extract_text() or "" for p in pdf.pages)
        except: return ""
    elif ext in ("docx","doc"):
        try:
            import docx as dx
            doc = dx.Document(io.BytesIO(file.read()))
            return "\n".join(p.text for p in doc.paragraphs)
        except: return ""
    else:
        return file.read().decode("utf-8", errors="ignore")

# build_prompt removed — chatbot_engine.py handles prompt building

@app.route("/")
def index(): return render_template("index.html")

@app.route("/api/analyze", methods=["POST"])
def analyze():
    language = "English"; text = ""
    if request.content_type and "multipart" in request.content_type:
        language = request.form.get("language","English")
        f = request.files.get("file")
        if not f or f.filename.rsplit(".",1)[-1].lower() not in ALLOWED:
            return jsonify({"error":"Invalid file"}), 400
        text = extract_text(f)
        if len(text.strip()) < 10:
            return jsonify({"error":"Could not extract text. Try pasting directly."}), 400
    else:
        data = request.get_json(silent=True) or {}
        language = data.get("language","English")
        text = data.get("text","").strip()
        if not text: return jsonify({"error":"No text provided"}), 400
    try:
        result = pipeline.analyze(text, language)
        result["raw_text_preview"] = text[:200]
        return jsonify(json.loads(json.dumps(result, default=str)))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/chat", methods=["POST"])
def chat():
    """MedBot — powered by Ollama phi3 locally. No API key needed."""
    data = request.get_json(silent=True) or {}
    msg  = data.get("message", "").strip()
    lang = data.get("language", "English")
    ctx  = data.get("report_context")
    if not msg:
        return jsonify({"error": "No message provided"}), 400
    result = chatbot.get_response(msg, ctx, lang)
    return jsonify(result)


@app.route("/api/chat/status")
def chat_status():
    """Check if Ollama is running and phi3 is available."""
    running = chatbot.is_ollama_running()
    try:
        import requests as req
        tags = req.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=3).json()
        models = [m["name"] for m in tags.get("models", [])]
        phi3_ready = any("phi3" in m for m in models)
    except Exception:
        models = []; phi3_ready = False
    return jsonify({
        "ollama_running": running,
        "phi3_ready":     phi3_ready,
        "available_models": models,
        "status": "ready" if (running and phi3_ready) else
                  "ollama_offline" if not running else "phi3_not_pulled",
        "setup": {
            "1_install": "https://ollama.ai",
            "2_pull":    f"ollama pull {OLLAMA_MODEL}",
            "3_serve":   "ollama serve",
        }
    })


@app.route("/api/debug/ollama")
def debug_ollama():
    """Debug helper: from the running server, try to reach the configured Ollama URL
    and return either the models payload or the error text. Useful to debug Render
    network connectivity from the service."""
    import requests as req
    from urllib.parse import urlparse

    base = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    try:
        parsed = urlparse(base)
        target = f"{base.rstrip('/')}/api/tags"
        r = req.get(target, timeout=6)
        return jsonify({
            "url": base,
            "status_code": r.status_code,
            "content_preview": r.text[:2000]
        })
    except Exception as e:
        return jsonify({"url": base, "error": str(e)}), 500


@app.route("/api/chat/stream", methods=["POST"])
def chat_stream():
    """
    Streaming chat via Server-Sent Events.
    Tokens appear as they're generated — much faster perceived latency.
    """
    import requests as req
    from flask import Response, stream_with_context

    data    = request.get_json(silent=True) or {}
    msg     = data.get("message", "").strip()
    lang    = data.get("language", "English")
    ctx     = data.get("report_context")
    if not msg:
        return jsonify({"error": "No message"}), 400

    # Check local response first (instant)
    intent = chatbot.classify_intent(msg)
    local_reply = chatbot.generate_local_response(msg, intent, ctx, lang)
    if local_reply is not None:
        def instant():
            yield f"data: {local_reply}\n\n"
            yield "data: [DONE]\n\n"
        return Response(stream_with_context(instant()),
                        mimetype="text/event-stream",
                        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

    # Stream from Ollama
    system = chatbot.build_system_prompt(lang, ctx)
    def stream_ollama():
        try:
            with req.post(
                f"{OLLAMA_BASE_URL}/api/chat",
                json={
                    "model": OLLAMA_MODEL,
                    "stream": True,
                    "options": {"num_predict": OLLAMA_MAX_TOKENS, "temperature": 0.7, "num_ctx": 2048},
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user",   "content": msg},
                    ]
                },
                stream=True, timeout=45
            ) as resp:
                for line in resp.iter_lines():
                    if line:
                        try:
                            chunk = __import__('json').loads(line)
                            token = chunk.get("message", {}).get("content", "")
                            if token:
                                yield f"data: {token}\n\n"
                        except Exception:
                            pass
                yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: ⚠️ Ollama error: {str(e)[:80]}\n\n"
            yield "data: [DONE]\n\n"

    return Response(stream_with_context(stream_ollama()),
                    mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

@app.route("/api/auth/signup", methods=["POST"])
def signup():
    d = request.get_json(silent=True) or {}
    name,email,pwd = d.get("name","").strip(), d.get("email","").strip().lower(), d.get("password","")
    if not all([name,email,pwd]): return jsonify({"error":"All fields required"}), 400
    if len(pwd)<6: return jsonify({"error":"Password min 6 chars"}), 400
    r = create_user(name, email, generate_password_hash(pwd))
    if r.get("status")=="email_exists": return jsonify({"error":"Email already registered"}), 409
    session["user_id"]=r["id"]; session["user_name"]=name
    return jsonify({"id":r["id"],"name":name,"email":email})

@app.route("/api/auth/login", methods=["POST"])
def login():
    d = request.get_json(silent=True) or {}
    email,pwd = d.get("email","").strip().lower(), d.get("password","")
    user = get_user_by_email(email)
    if not user or not check_password_hash(user["password_hash"],pwd):
        return jsonify({"error":"Invalid email or password"}), 401
    session["user_id"]=user["id"]; session["user_name"]=user["name"]
    return jsonify({"id":user["id"],"name":user["name"],"email":user["email"],"created_at":user["created_at"]})

@app.route("/api/auth/logout", methods=["POST"])
def logout():
    session.clear(); return jsonify({"status":"logged_out"})

@app.route("/api/auth/me")
def me():
    if "user_id" not in session: return jsonify({"error":"Not authenticated"}), 401
    user = get_user_by_id(session["user_id"])
    if not user: session.clear(); return jsonify({"error":"Not found"}), 404
    user.update(get_report_stats(user["id"]))
    return jsonify(user)

@app.route("/api/auth/profile", methods=["PUT"])
@login_required
def update_profile():
    d = request.get_json(silent=True) or {}
    name,email = d.get("name","").strip(), d.get("email","").strip().lower()
    update_user(session["user_id"], name=name or None, email=email or None)
    if name: session["user_name"]=name
    return jsonify({"status":"updated"})

@app.route("/api/auth/password", methods=["PUT"])
@login_required
def change_password():
    d = request.get_json(silent=True) or {}
    pwd = d.get("password","")
    if len(pwd)<6: return jsonify({"error":"Min 6 chars"}), 400
    update_user(session["user_id"], password_hash=generate_password_hash(pwd))
    return jsonify({"status":"updated"})

@app.route("/api/auth/account", methods=["DELETE"])
@login_required
def delete_account():
    delete_user(session["user_id"]); session.clear()
    return jsonify({"status":"deleted"})

@app.route("/api/history")
@login_required
def history():
    return jsonify({"reports": get_user_reports(session["user_id"], 30)})

@app.route("/api/report/<int:rid>")
@login_required
def get_report(rid):
    r = get_report_by_id(rid, session["user_id"])
    if not r: return jsonify({"error":"Not found"}), 404
    return jsonify(r)

@app.route("/api/report/save", methods=["POST"])
@login_required
def save_report_route():
    d = request.get_json(silent=True) or {}
    result = d.get("result"); text = d.get("raw_text","")
    if not result: return jsonify({"error":"No result"}), 400
    rid = save_report(session["user_id"], result, text)
    return jsonify({"id":rid,"status":"saved"})

@app.route("/api/report/<int:rid>", methods=["DELETE"])
@login_required
def delete_report_route(rid):
    delete_report(rid, session["user_id"])
    return jsonify({"status":"deleted"})

@app.route("/api/stats")
@login_required
def stats():
    return jsonify(get_report_stats(session["user_id"]))

if __name__ == "__main__":
    app.run(debug=True)
