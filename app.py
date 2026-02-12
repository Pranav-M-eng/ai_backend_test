from flask import Flask, request, jsonify
import requests, os
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

API_KEY = os.getenv("OPENAI_KEY")

def call_ai(prompt):
    if not API_KEY:
        return '{"error":"OPENAI_KEY not set on server"}'

    r = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "gpt-4.1-mini",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2
        },
        timeout=30
    )
    return r.json()["choices"][0]["message"]["content"]


@app.route("/")
def home():
    return "Backend is running!"

@app.route("/analyze", methods=["POST", "OPTIONS"])
def analyze():
    if request.method == "OPTIONS":
        return "", 204

    user_arg = request.json.get("text", "")

    prompt = f"""
You are a neutral judge. Analyze this argument and return JSON with:
clarity_score, logical_consistency_score, evidence_score,
engagement_with_opponent_score, fallacies_detected, short_feedback.

Argument:
"{user_arg}"
"""

    result = call_ai(prompt)
    return jsonify({"result": result})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  # Railway provides PORT
    app.run(host="0.0.0.0", port=port)


