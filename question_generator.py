# question_generator.py
from llm import generate_question_with_gemini
from typing import Dict

BASE_SYSTEM = """
You are a short, conversational interviewer. Given the candidate profile and context,
generate a single short interview question tailored to the candidate's tech stack and experience.
If the previous answer shows confusion/uncertainty (sentiment negative), generate a simpler
or clarifying question. Output only the question, no extra commentary.
"""

def build_prompt(profile: Dict, last_answer: str, sentiment_label: str) -> str:
    experience = profile.get("experience_years", "N/A")
    stack = profile.get("tech_stack", [])
    stack_str = ", ".join(stack) if isinstance(stack, list) else str(stack)
    prev = last_answer if last_answer else "No previous answer."
    sent = sentiment_label if sentiment_label else "NEUTRAL"

    prompt = f"""
Candidate profile:
- Experience (years): {experience}
- Tech stack: {stack_str}

Previous answer:
{prev}

Sentiment label:
{sent}

Instruction:
Generate ONE concise, conversational technical interview question appropriate for the candidate.
Keep it focused, one sentence if possible.
"""
    return prompt

def generate_next_question(profile: Dict, last_answer: str, sentiment_label: str) -> str:
    prompt = build_prompt(profile, last_answer, sentiment_label)
    question = generate_question_with_gemini(prompt)
    # Some basic sanitization: ensure it ends with '?'
    q = question.strip()
    if not q.endswith("?"):
        q = q.rstrip(".") + "?"
    return q
