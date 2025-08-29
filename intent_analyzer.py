"""
Enhanced AI context analysis to better understand user intent
"""

def analyze_intent(user_input: str, expected_field: str = None) -> dict:
    """
    A more intelligent analyzer to determine the user's intent from their input.
    
    Args:
        user_input: The user's input text
        expected_field: What kind of answer we're expecting (e.g., "name", "email", "tech_stack")
        
    Returns:
        Dict with analysis results including:
        - intent_type: "answer", "question", "off_topic", "meta", etc.
        - confidence: How confident we are in this classification
        - is_relevant: Whether the response is relevant to the expected field
    """
    # Default response
    result = {
        "intent_type": "answer",
        "confidence": 0.8,
        "is_relevant": True
    }
    
    # Clean the input
    text = user_input.strip().lower()
    
    # Check for question patterns
    question_indicators = ["?", "what", "how", "why", "where", "when", "who", "can you", "could you"]
    has_question = "?" in text or any(text.startswith(q) for q in question_indicators)
    
    # Check for command patterns
    command_indicators = ["tell me", "show me", "give me", "i want", "please"]
    has_command = any(c in text for c in command_indicators)
    
    # Check for meta-conversation patterns (talking about the conversation)
    meta_indicators = ["this interview", "this conversation", "talking", "chat", "ask", "question"]
    is_meta = any(m in text for m in meta_indicators)
    
    # Simple relevance check if we know the expected field
    is_relevant = True
    if expected_field:
        if expected_field == "name" and len(text.split()) <= 3:
            # Names are typically 1-3 words
            is_relevant = True
        elif expected_field == "email" and ("@" in text and "." in text):
            # Basic email check
            is_relevant = True
        elif expected_field == "phone" and any(c.isdigit() for c in text):
            # Phone should have digits
            is_relevant = True
        elif expected_field == "tech_stack":
            # Check for common tech terms
            tech_terms = ["javascript", "python", "java", "html", "css", "react", "angular", 
                         "node", "express", "django", "flask", "ruby", "c++", "c#", "php", 
                         "typescript", "sql", "nosql", "mongo", "mysql", "postgres"]
            is_relevant = any(term in text for term in tech_terms)
    
    # Determine intent type
    if has_question:
        result["intent_type"] = "question"
        result["confidence"] = 0.9
    elif has_command:
        result["intent_type"] = "command"
        result["confidence"] = 0.8
    elif is_meta:
        result["intent_type"] = "meta"
        result["confidence"] = 0.7
    else:
        result["intent_type"] = "answer"
    
    # Update relevance
    result["is_relevant"] = is_relevant
    
    return result
