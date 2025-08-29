"""
Context handling utilities for maintaining conversation flow and handling edge cases.
"""

from typing import Dict, List, Tuple, Optional
import re

def detect_conversation_shift(user_input: str, current_stage: str) -> Tuple[bool, str]:
    """
    Detect if user is trying to shift the conversation away from the intended flow.
    
    Args:
        user_input: The latest user message
        current_stage: Current stage of conversation
    
    Returns:
        (is_shift, guidance): Whether conversation shift detected and guidance message
    """
    # Only analyze longer messages or those with specific patterns
    # Skip short responses which are likely direct answers
    if len(user_input.split()) <= 5 and not any(char in user_input for char in "?!"):
        return False, ""
        
    # Keywords suggesting conversation drift - must be standalone words
    end_keywords = [" quit ", " exit ", " stop ", " end ", " terminate ", " bye ", " goodbye "]
    help_keywords = [" help ", " confused ", " don't understand ", " what is this ", " what's this "]
    irrelevant_patterns = [
        " weather ", " joke ", " tell me a joke ", " who are you ", " what can you do ",
        " what's your name ", " how are you ", " what is your "
    ]
    
    # Add spaces to make sure we're matching whole words or phrases
    user_input_lower = " " + user_input.lower() + " "
    
    # Check for exit intent - must be explicit phrases
    if any(keyword in user_input_lower for keyword in end_keywords):
        # Skip responses like "I want to end my career in frontend development"
        # by checking if it's mostly just the exit keyword
        exit_word = next((kw for kw in end_keywords if kw in user_input_lower), "").strip()
        if exit_word and len(user_input.split()) <= 3:
            return True, "It seems like you want to end the conversation. If you'd like to continue the interview, please answer the current question."
    
    # Check for help request - must be explicit help requests
    if any(keyword in user_input_lower for keyword in help_keywords):
        if current_stage == "GATHERING_INFO":
            return True, "I'm collecting basic information for your candidate profile. Please provide the requested information so we can proceed to the technical questions."
        elif current_stage == "QA":
            return True, "This is a technical interview. Please answer the question to the best of your abilities."
        return True, "This is an automated interview process. Please answer the questions as they come."
    
    # Check for irrelevant queries - must be predominantly about irrelevant topics
    if any(pattern in user_input_lower for pattern in irrelevant_patterns):
        for pattern in irrelevant_patterns:
            if pattern in user_input_lower and len(user_input.split()) <= len(pattern.split()) + 3:
                return True, "I'm an interview assistant focused on conducting your technical screening. Let's stay focused on the current question."
    
    return False, ""


def format_next_steps() -> str:
    """Generate a message about what happens next after the interview"""
    return """
Thank you for completing this technical screening interview. Here's what happens next:

1. Your responses will be evaluated by our team
2. If your profile matches our requirements, we'll contact you for the next round
3. You should hear back from us within 5 business days

If you have any questions, please contact our HR team at careers@example.com.

Best of luck with your application!
"""
