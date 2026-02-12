def call_ai(prompt):
    if not API_KEY:
        raise Exception("OPENAI_KEY not set on server")

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

    if r.status_code != 200:
        # Log full error from OpenAI
        raise Exception(f"OpenAI error {r.status_code}: {r.text}")

    data = r.json()
    return data["choices"][0]["message"]["content"]


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
        # Return the actual error to frontend (for debugging)
        return jsonify({"error": str(e)}), 500
