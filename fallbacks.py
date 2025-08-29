"""
Fallback questions and responses for when the LLM fails or other unexpected situations occur.
"""

DEFAULT_QUESTIONS = [
    "Tell me about your experience with your primary programming language.",
    "Describe a challenging technical problem you've solved recently.",
    "How do you approach debugging a complex issue?",
    "What's your experience with version control systems like Git?",
    "How do you stay updated with the latest developments in technology?"
]

def get_fallback_questions():
    """Return a set of default interview questions if LLM fails"""
    return DEFAULT_QUESTIONS
