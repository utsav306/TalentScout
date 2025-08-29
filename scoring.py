import google.generativeai as genai
from config import GOOGLE_API_KEY

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

def score_answers_with_gemini(questions, answers):
    """
    Given a list of questions and answers, return a list of scores and feedback for each answer.
    """
    prompt = """
You are an expert technical interviewer. Given the following interview questions and candidate answers, score each answer on a scale of 1-10 for the following parameters: Technical Depth, Clarity, Relevance, and Overall. Also provide a one-sentence feedback for each answer. Return the result as a JSON list, one object per answer, with keys: question, answer, technical_depth, clarity, relevance, overall, feedback.

Questions and Answers:
"""
    for i, (q, a) in enumerate(zip(questions, answers), 1):
        prompt += f"\nQ{i}: {q}\nA{i}: {a}"
    prompt += "\n\nReturn only the JSON list."

    try:
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        response = model.generate_content([
            {"role": "user", "parts": [{"text": prompt}]}
        ])
        return response.text.strip()
    except Exception as e:
        return f"[LLM_ERROR] Could not score answers: {e}"
