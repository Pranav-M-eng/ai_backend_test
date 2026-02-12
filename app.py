from flask import Flask, request, jsonify
import requests, os
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

API_KEY = os.getenv("OPENAI_KEY")

def call_ai(prompt):
    if not API_KEY:
        raise Exception("OPENAI_KEY not set on server")

    r = requests.post(
        "https://api.openai.com/v1/responses",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "gpt-4.1-mini",
            "input": prompt
        },
        timeout=60
    )

    if r.status_code != 200:
        # Return the actual OpenAI error to logs
        raise Exception(f"OpenAI error {r.status_code}: {r.text}")

    data = r.json()

    # Safely extract text from Responses API
    text_parts = []
    for item in data.get("output", []):
        for content in item.get("content", []):
            if content.get("type") == "output_text":
                text_parts.append(content.get("text", ""))

    if not text_parts:
        raise Exception(f"No text output from OpenAI: {data}")

    return "".join(text_parts)



@app.route("/")
def home():
    return "Backend is running!"


@app.route("/analyze", methods=["POST", "OPTIONS"])
def analyze():
    if request.method == "OPTIONS":
        return "", 204

    try:
        body = request.get_json(force=True)
        user_arg = body.get("text", "")

        prompt = f"""
You are a neutral judge. Analyze this argument and return JSON with:
clarity_score, logical_consistency_score, evidence_score,
engagement_with_opponent_score, fallacies_detected, short_feedback.

Argument:
"{user_arg}"
"""
        result = call_ai(prompt)
        return jsonify({"result": result})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

