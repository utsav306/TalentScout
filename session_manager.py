"""
Session state management utilities to help with conversation state transitions.
"""

def reset_interview_state(session_state):
    """Reset the interview to start over with a new candidate"""
    session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello! I'm Scout, your AI Hiring Assistant from TalentScout. "
                       "I'll conduct a brief initial screening.\n\nWhat's your full name?"
        }
    ]
    session_state.candidate_info = {}
    session_state.stage = "GATHERING_INFO"
    session_state.current_question = None
    
    # Clear Q&A history
    if hasattr(session_state, "qa_history"):
        session_state.qa_history = []
    if hasattr(session_state, "qa_queue"):
        session_state.qa_queue = []
    if hasattr(session_state, "qa_pairs"):
        session_state.qa_pairs = []
