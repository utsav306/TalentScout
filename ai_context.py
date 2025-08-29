import google.generativeai as genai
from config import GOOGLE_API_KEY

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

def analyze_response_context_with_gemini(question, answer, stage):
    """
    Use Gemini to analyze if the user's answer is staying on topic and addressing the question.
    
    Args:
        question: The question or prompt given to the user
        answer: The user's response
        stage: The current interview stage ('GATHERING_INFO', 'QA', etc.)
        
    Returns:
        dict: Analysis result with 'on_topic', 'guidance', and 'confidence' keys
    """
    # Print progress message for better visibility
    print("Analyzing response context...")
    
    # Skip analysis for very short answers that are likely valid
    if len(answer.split()) <= 3 and not any(x in answer.lower() for x in ["help", "bye", "quit", "exit"]):
        print("Short response detected, skipping context analysis")
        return {"on_topic": True, "confidence": 0.9, "guidance": ""}
    # Skip analysis for very short answers that are likely valid
    if len(answer.split()) <= 3 and not any(x in answer.lower() for x in ["help", "bye", "quit", "exit"]):
        return {"on_topic": True, "confidence": 0.9, "guidance": ""}
        
    try:
        prompt = f"""
You are an AI assistant analyzing responses during a technical interview.
Your goal is to determine if the candidate's response is on-topic or if they are trying to change the subject.

INTERVIEW STAGE: {stage}
QUESTION/PROMPT: "{question}"
USER RESPONSE: "{answer}"

Technical Interview Context:
- The interview is focused on assessing technical skills
- The candidate should be answering questions about their technical knowledge and experience
- Attempts to change topics, evade questions, or discuss unrelated matters are off-topic
- Phrases like "let's talk about something else" indicate off-topic responses

BE STRICT: This is an interview context where candidates should stay focused on answering the question asked.

VERY IMPORTANT:
1. Respond ONLY with JSON format
2. Don't include any explanations outside the JSON structure
3. If the user is clearly trying to change the subject, mark as off-topic with high confidence

Analyze and return a JSON object with:
{{
  "on_topic": boolean,
  "guidance": "A helpful message to guide the user back on topic if they're off-topic",
  "confidence": float between 0.0-1.0
}}
"""
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        response = model.generate_content([
            {"role": "user", "parts": [{"text": prompt}]}
        ])
        
        analysis = response.text.strip()
        
        # Basic fallback in case of JSON parsing issues
        try:
            import json
            result = json.loads(analysis)
            return result
        except:
            # Default response if JSON parsing fails
            return {
                "on_topic": True,  # Default to assuming on-topic to avoid disrupting flow
                "guidance": "Let's stay focused on the interview questions.",
                "confidence": 0.5
            }
            
    except Exception as e:
        print(f"LLM Context Analysis Error: {str(e)}")
        # Fallback response if LLM call fails
        return {
            "on_topic": True,  # Default to assuming on-topic to avoid disrupting flow
            "guidance": "Let's stay focused on the interview questions.",
            "confidence": 0.5
        }
