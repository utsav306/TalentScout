from llm import generate_question_with_gemini
from context_handler import detect_conversation_shift, format_next_steps
from intent_analyzer import analyze_intent
from ai_context import analyze_response_context_with_gemini

FIELDS = [
    "full_name",
    "email",
    "phone",
    "experience_years",
    "desired_positions",
    "location",
    "tech_stack"
]

# Fallback responses for unexpected inputs
FALLBACK_RESPONSES = [
    "I'm not sure I understand. Could you please respond to the current question?",
    "Let's stay focused on the interview. Please answer the current question.",
    "I need your response to the current question to proceed with the interview.",
    "To continue with the interview process, please answer the question I've asked.",
    "I'm here to help with your technical screening. Could you please answer the question?"
]

def handle_profile_answer(session_state, user_input):
    """
    Collect candidate info sequentially.
    When tech_stack is provided, generate 5 tech questions via Gemini.
    """
    # Get the current field being asked for
    current_field = None
    for field in FIELDS:
        if field not in session_state.candidate_info:
            current_field = field
            break
            
    # Skip context checking for short, simple answers that are clearly valid
    if current_field == "full_name" and 1 <= len(user_input.split()) <= 5:
        # Skip context check for names (1-5 words)
        pass
    elif current_field == "email" and "@" in user_input and "." in user_input:
        # Skip context check for valid-looking emails
        pass
    elif current_field == "phone" and any(c.isdigit() for c in user_input) and len(user_input) <= 15:
        # Skip context check for phone numbers
        pass
    else:
        # For more complex fields or longer inputs, use AI-powered context analysis
        
        # Create prompt specific to the field being asked
        prompt = f"Please provide your {current_field.replace('_', ' ')}"
        
        # Use AI to check if the response is appropriate for the current field
        ai_context_analysis = analyze_response_context_with_gemini(
            question=prompt,
            answer=user_input,
            stage="GATHERING_INFO"
        )
        
        # If the AI detects the response is off-topic with high confidence, provide guidance
        if not ai_context_analysis.get("on_topic", True) and ai_context_analysis.get("confidence", 0) > 0.6:
            guidance = ai_context_analysis.get("guidance", "Let's stay focused on the interview.")
            field_name = current_field.replace('_', ' ') if current_field else "information"
            return f"{guidance}\n\nPlease provide your {field_name}."
    
    # Normal profile collection flow
    for field in FIELDS:
        if field not in session_state.candidate_info:
            # Validate input based on field type
            if field == "experience_years":
                try:
                    # Attempt to convert to int
                    session_state.candidate_info[field] = int(user_input)
                except ValueError:
                    # Try to extract numbers if user provided text like "5 years"
                    import re
                    numbers = re.findall(r'\d+', user_input)
                    if numbers:
                        session_state.candidate_info[field] = int(numbers[0])
                    else:
                        session_state.candidate_info[field] = 0

            elif field == "email":
                # Simple email validation
                if "@" in user_input and "." in user_input:
                    session_state.candidate_info[field] = user_input.strip()
                else:
                    return "That doesn't look like a valid email address. Please provide a valid email."

            elif field == "desired_positions":
                # Simple validation to avoid false positives in context handling
                # Accept any reasonable text as a position
                session_state.candidate_info[field] = user_input.strip()

            elif field == "tech_stack":
                # Split tech stack by comma
                techs = [t.strip() for t in user_input.split(",")]
                session_state.candidate_info[field] = techs

                # --- Prepare candidate info for Gemini ---
                profile_for_prompt = {
                    "experience_years": session_state.candidate_info.get("experience_years", 0),
                    "desired_position": session_state.candidate_info.get("desired_positions", ""),
                    "tech_stack": techs
                }

                # Generate 5 tech questions with a progress indicator in app.py
                print("Generating interview questions...")
                questions_text = generate_question_with_gemini(profile_for_prompt)
                print("Questions generated successfully")

                # Split into list assuming one question per line
                questions = [q.strip() for q in questions_text.split("\n") if q.strip()]

                # Initialize queues
                session_state.qa_queue = questions
                session_state.qa_history = []
                session_state.qa_pairs = []  # Store Q&A pairs for context

            else:
                session_state.candidate_info[field] = user_input.strip()

            return field  # Return the field just filled


def handle_qa(session_state, user_answer):
    """
    Pop next question from queue, return follow-up and next question.
    """
    # Get the current question if available
    current_question = session_state.current_question if hasattr(session_state, "current_question") else "interview question"
    
    # Use AI-powered context analyzer to check if response is on-topic
    ai_context_analysis = analyze_response_context_with_gemini(
        question=current_question,
        answer=user_answer,
        stage=session_state.stage
    )
    
    # If the AI detects the response is off-topic with high confidence, provide guidance
    if not ai_context_analysis.get("on_topic", True) and ai_context_analysis.get("confidence", 0) > 0.7:
        guidance = ai_context_analysis.get("guidance", "Let's stay focused on the interview. Please answer the current question.")
        return guidance, session_state.current_question  # Return guidance + repeat current question
    
    # Fall back to rule-based analysis for very short answers
    if len(user_answer.split()) < 3:
        # Very short answers might not be proper responses to technical questions
        # But avoid flagging simple answers to yes/no questions
        if current_question and not any(q in current_question.lower() for q in ["yes or no", "have you", "do you", "did you"]):
            return "Could you please elaborate on your answer? Technical questions typically require more detailed responses.", session_state.current_question
            
    # Store the answer if everything is valid
    if hasattr(session_state, "current_question") and session_state.current_question:
        # Add the Q&A pair to history if not already there
        qa_pair = {
            "question": session_state.current_question,
            "answer": user_answer
        }
        if hasattr(session_state, "qa_pairs"):
            session_state.qa_pairs.append(qa_pair)
        else:
            session_state.qa_pairs = [qa_pair]
    
    # We've already stored the answer above, so no need to repeat that
    followup = "Thanks for your answer!"
    next_question = None

    # Ensure queue exists
    if not hasattr(session_state, "qa_queue"):
        session_state.qa_queue = []

    if not hasattr(session_state, "qa_history"):
        session_state.qa_history = []

    if session_state.qa_queue:
        next_question = session_state.qa_queue.pop(0)
        session_state.qa_history.append(next_question)
    else:
        session_state.stage = "CONCLUDED"
        next_question = None
        # Don't add the full closing message here, just a simple acknowledgment
        # The app.py will handle the detailed closing message
        followup = "Thank you for completing the interview!"

    return followup, next_question
