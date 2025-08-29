import google.generativeai as genai
from config import GOOGLE_API_KEY

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

def generate_question_with_gemini(candidate_info):
    """
    Generate technical questions based on candidate's tech stack & experience.
    Returns a string with questions separated by newlines.
    """
    tech_stack = ", ".join(candidate_info.get("tech_stack", ["Python"]))
    experience = candidate_info.get("experience_years", 0)
    prompt = (
        f"Generate FIVE short, conversational technical interview questions "
        f"for a candidate with {experience} years experience in {tech_stack}. "
        f"Output only the questions, one per line, no numbering or commentary."
    )

    try:
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        response = model.generate_content([
            {"role": "user", "parts": [{"text": prompt}]}
        ])
        questions = response.text.strip()
        
        # Validate response
        if not questions or "[LLM_ERROR]" in questions:
            from fallbacks import get_fallback_questions
            return "\n".join(get_fallback_questions())
            
        # Check if we got at least a reasonable number of lines
        lines = [line for line in questions.split("\n") if line.strip()]
        if len(lines) < 2:  # We should have at least a couple of questions
            from fallbacks import get_fallback_questions
            return "\n".join(get_fallback_questions())
            
        return questions
    except Exception as e:
        from fallbacks import get_fallback_questions
        print(f"LLM Error: {str(e)}")
        return "\n".join(get_fallback_questions())
