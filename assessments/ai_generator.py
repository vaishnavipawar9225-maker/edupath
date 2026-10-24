"""
Optional: Generate questions using Google Gemini (free tier).
Requires: pip install google-generativeai
Requires: API key from https://aistudio.google.com/apikey
"""
import os
import json
import random
import re


def generate_with_gemini(topic, n=5):
    try:
        import google.generativeai as genai
    except ImportError:
        return None

    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        return None

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = f"""Generate {n} multiple-choice questions about "{topic}".
Format: JSON array only, no markdown, no explanation.
Each item: {{"q": "question", "c": ["A","B","C","D"], "a": 0-3}}
Example: [{{"q":"2+2?","c":["3","4","5","6"],"a":1}}]
Return ONLY the JSON array."""

        response = model.generate_content(prompt)
        text = response.text.strip()

        # Strip markdown fences if Gemini adds them
        text = re.sub(r"^```(?:json)?", "", text)
        text = re.sub(r"```$", "", text)
        text = text.strip()

        data = json.loads(text)

        # Convert to our format: (text, choices, correct_idx, marks)
        return [(item["q"], item["c"], item["a"], 2) for item in data]

    except Exception:
        return None  # fall back to procedural