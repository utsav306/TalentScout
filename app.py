import streamlit as st
import time
import json
from datetime import datetime
from conversation_manager import handle_profile_answer, handle_qa, FIELDS
from storage import save_candidate
from mail_service import send_thank_you_email_mailjet
from fallbacks import get_fallback_questions
from scoring import score_answers_with_gemini


def main():
    # Initialize session state if not already done
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'is_loading' not in st.session_state:
        st.session_state.is_loading = False
    if 'stage' not in st.session_state:
        st.session_state.stage = "GATHERING_INFO"  # Initial stage
    if 'candidate_info' not in st.session_state:
        st.session_state.candidate_info = {}
    if 'qa_queue' not in st.session_state:
        st.session_state.qa_queue = []
    if 'qa_history' not in st.session_state:
        st.session_state.qa_history = []
    if 'qa_pairs' not in st.session_state:
        st.session_state.qa_pairs = []
    # Always use dark theme
    st.session_state.theme = "dark"
    if 'interview_start_time' not in st.session_state:
        st.session_state.interview_start_time = datetime.now()
    if 'progress' not in st.session_state:
        st.session_state.progress = 0  # Track interview progress
    if 'debug' not in st.session_state:
        st.session_state.debug = True  # Enable debug logging
    
    # Print debug info
    if st.session_state.debug:
        print(f"Session state: stage={st.session_state.stage}, loading={st.session_state.is_loading}")
        print(f"Candidate info: {st.session_state.candidate_info}")
        if hasattr(st.session_state, "qa_queue"):
            print(f"QA queue length: {len(st.session_state.qa_queue)}")
    
    # Start interview if no messages yet
    if not st.session_state.messages:
        welcome_message = "Hi there! 👋 I'm your AI hiring assistant. I'll be conducting your initial screening interview today. Let's start with some basic information.\n\nPlease provide your full name."
        st.session_state.messages.append({"role": "assistant", "content": welcome_message})


# Entry point for the application
if __name__ == "__main__":
    main()

# --- Apply theme based on user preference ---
def apply_theme():
    if st.session_state.theme == "dark":
        # Dark theme
        chat_user_bg = "#2C3333"
        chat_assistant_bg = "#395B64"
        text_color = "#E7F6F2"
        btn_color = "#A5C9CA"
        btn_hover = "#E7F6F2"
        btn_text = "#2C3333"
        background = "#111111"
        header_bg = "#222831"
    else:
        # Light theme (default)
        chat_user_bg = "#E3F2FD"
        chat_assistant_bg = "#F3E5F5"
        text_color = "#333333"
        btn_color = "#42A5F5"
        btn_hover = "#1E88E5"
        btn_text = "#FFFFFF"
        background = "#FFFFFF"
        header_bg = "#F9F9F9"
    
    return chat_user_bg, chat_assistant_bg, text_color, btn_color, btn_hover, btn_text, background, header_bg

# Get theme colors
chat_user_bg, chat_assistant_bg, text_color, btn_color, btn_hover, btn_text, background, header_bg = apply_theme()

# --- Modern UI Styling ---
st.markdown(f"""
<style>
    /* Main background */
    .stApp {{
        background-color: {background};
    }}
    
    /* Header */
    .main .block-container {{
        padding-top: 1rem;
    }}
    
    /* Chat container styling */
    .chat-container {{
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }}
    
    /* Chat messages */
    .stChatMessage {{
        border-radius: 18px;
        margin-bottom: 12px;
        padding: 15px 20px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: 15px;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.1);
        max-width: 85%;
        animation: fadeIn 0.5s;
    }}
    
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    /* User messages */
    .stChatMessage.user {{
        background: {chat_user_bg};
        color: {text_color};
        margin-left: auto;
        border-bottom-right-radius: 5px;
    }}

    /* Assistant messages */
    .stChatMessage.assistant {{
        background: {chat_assistant_bg};
        color: {text_color};
        margin-right: auto;
        border-bottom-left-radius: 5px;
    }}

    /* Buttons */
    .stButton>button {{
        background: {btn_color};
        color: {btn_text};
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        border: none;
        cursor: pointer;
        margin-top: 5px;
        transition: all 0.3s ease;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}

    .stButton>button:hover {{
        background: {btn_hover};
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }}

    /* Download button */
    .stDownloadButton>button {{
        background: #43a047;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        border: none;
        cursor: pointer;
        margin-top: 5px;
        transition: all 0.3s ease;
    }}

    .stDownloadButton>button:hover {{
        background: #2e7d32;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }}
    
    /* Progress bar */
    .stProgress > div > div {{
        background-color: {btn_color};
    }}
    
    /* Header area */
    .header-container {{
        background-color: {header_bg};
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }}
    
    /* Input area */
    .stChatInputContainer {{
        padding-top: 1rem;
        border-top: 1px solid rgba(0,0,0,0.1);
    }}
    
    /* Streamlit elements */
    .css-18e3th9, .css-1d391kg {{
        padding: 1rem 1rem;
    }}
    
    h1, h2, h3, h4 {{
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}
    
    /* Sidebar */
    .css-1lcbmhc .css-1d391kg {{
        background-color: {header_bg};
    }}
</style>
""", unsafe_allow_html=True)

# --- Application Header ---
header_col1, header_col2 = st.columns([1, 5])

with header_col1:
    st.image("https://img.icons8.com/fluency/96/000000/chatbot.png", width=80)

with header_col2:
    st.title("🤖 TalentScout Hiring Assistant")
    st.markdown("<p style='font-size: 1.2rem; opacity: 0.8;'>Welcome! Please answer the questions below to complete the initial screening.</p>", unsafe_allow_html=True)

# --- Create a sidebar for additional info and controls ---
with st.sidebar:
    st.markdown("### Interview Progress")
    
    # Calculate progress based on stage
    if st.session_state.stage == "GATHERING_INFO":
        # Calculate progress based on fields completed
        total_fields = len(FIELDS)
        completed_fields = sum(1 for field in FIELDS if field in st.session_state.candidate_info)
        progress_percentage = int((completed_fields / total_fields) * 50)  # First half is profile collection
    elif st.session_state.stage == "QA":
        # Add the base 50% from profile collection
        qa_progress = 0
        if hasattr(st.session_state, "qa_queue") and hasattr(st.session_state, "qa_history"):
            total_questions = len(st.session_state.qa_queue) + len(st.session_state.qa_history)
            if total_questions > 0:
                qa_progress = int((len(st.session_state.qa_history) / total_questions) * 50)
        progress_percentage = 50 + qa_progress
    else:  # CONCLUDED
        progress_percentage = 100
    
    st.session_state.progress = progress_percentage
    st.progress(st.session_state.progress / 100)
    
    # Show elapsed time
    elapsed_time = datetime.now() - st.session_state.interview_start_time
    minutes = int(elapsed_time.total_seconds() // 60)
    seconds = int(elapsed_time.total_seconds() % 60)
    st.markdown(f"**Time Elapsed:** {minutes}m {seconds}s")
    
    # Display current stage
    stage_name = {
        "GATHERING_INFO": "Profile Collection",
        "QA": "Technical Questions",
        "CONCLUDED": "Interview Completed"
    }.get(st.session_state.stage, st.session_state.stage)
    
    st.markdown(f"**Current Stage:** {stage_name}")
    
    # Theme is always dark, no switcher or reset button
        
# Main content container
st.markdown("<div class='chat-container'>", unsafe_allow_html=True)

# --- Display chat messages ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        
# --- Display a small loading indicator that won't block the UI ---
if st.session_state.is_loading:
    # Minimal loading indicator without animations
    with st.container():
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            # Different messages based on the stage
            if st.session_state.stage == "GATHERING_INFO":
                loading_message = "Processing your information..."
            elif st.session_state.stage == "QA":
                loading_message = "Analyzing your response..."
            elif st.session_state.stage == "CONCLUDED":
                loading_message = "Finalizing your interview..."
            else:
                loading_message = "Processing your response..."
                
            st.markdown(f"""
            <div style="display: flex; align-items: center; justify-content: center; margin: 10px 0;">
                <div class="loading-spinner" style="margin-right: 10px;">
                    <span class="loader"></span>
                </div>
                <div>
                    <p><em>{loading_message}</em></p>
                </div>
            </div>
            <style>
                .loading-spinner {{
                    display: inline-flex;
                    justify-content: center;
                    align-items: center;
                }}
                .loader {{
                    width: 16px;
                    height: 16px;
                    border: 2px solid #f3f3f3;
                    border-top: 2px solid #3498db;
                    border-radius: 50%;
                    animation: spin 1s linear infinite;
                    display: inline-block;
                }}
                @keyframes spin {{
                    0% {{ transform: rotate(0deg); }}
                    100% {{ transform: rotate(360deg); }}
                }}
            </style>
            """, unsafe_allow_html=True)
            # Smaller, non-blocking indicator with no time.sleep

# --- Enhanced chat input with custom placeholder based on current stage ---
chat_placeholder = "Type your response here..."

# Don't show input if we're still processing
if not st.session_state.is_loading:
    if st.session_state.stage == "GATHERING_INFO":
        # Find current field being asked
        current_field = None
        for field in FIELDS:
            if field not in st.session_state.candidate_info:
                current_field = field
                break
        
        if current_field:
            field_prompts = {
                "full_name": "Enter your full name...",
                "email": "Enter your email address...",
                "phone": "Enter your phone number...",
                "experience_years": "Enter your years of experience...",
                "desired_positions": "What positions are you interested in?...",
                "location": "What is your current location?...",
                "tech_stack": "List your technical skills separated by commas..."
            }
            chat_placeholder = field_prompts.get(current_field, chat_placeholder)
    elif st.session_state.stage == "QA":
        chat_placeholder = "Type your answer to the technical question..."
    elif st.session_state.stage == "CONCLUDED":
        chat_placeholder = "Interview completed. Type here for follow-up questions..."

    # Apply the custom placeholder to the chat input
    if prompt := st.chat_input(chat_placeholder):
        # Add user message to chat
        st.chat_message("user").write(prompt)
        # Add to session state
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.user_input = prompt
        st.session_state.is_loading = True
        st.rerun()  # Force a rerun to show the loading indicator

    # Process user input if we have it in session state
if st.session_state.is_loading and hasattr(st.session_state, "user_input"):
    # Simplified processing logic - always process if there's user input
    user_input = st.session_state.user_input
    print(f"Processing input: {user_input}")
    
    # --- Stage: Gathering candidate info ---
    if st.session_state.stage == "GATHERING_INFO":
        print("GATHERING_INFO stage")
        field_or_message = handle_profile_answer(st.session_state, user_input)        # Check if we got a guidance message (context handling) instead of field
        if isinstance(field_or_message, str) and field_or_message in FIELDS:
            field = field_or_message
            fields_order = ["full_name","email","phone","experience_years","desired_positions","location","tech_stack"]
            next_field_idx = fields_order.index(field)

            if next_field_idx + 1 < len(fields_order):
                next_field = fields_order[next_field_idx + 1]
                response = f"Got it! Now please provide your {next_field.replace('_',' ')}."
                st.session_state.messages.append({"role": "assistant", "content": response})
            else:
                # Tech stack collected → start QA
                # Always ensure there are questions in the queue
                if not hasattr(st.session_state, "qa_queue") or not st.session_state.qa_queue:
                    fallback_questions = get_fallback_questions()
                    st.session_state.qa_queue = list(fallback_questions)
                # Pop the first question and start QA
                if st.session_state.qa_queue:
                    first_question = st.session_state.qa_queue.pop(0)
                    st.session_state.current_question = first_question
                    if not hasattr(st.session_state, "qa_history"):
                        st.session_state.qa_history = []
                    st.session_state.qa_history.append(first_question)
                    response = f"Great! Now I'll ask you a series of technical questions based on your profile. Please answer each question thoroughly.\n\nLet's start:\n\n{first_question}"
                    st.session_state.stage = "QA"
                    st.session_state.messages.append({"role": "assistant", "content": response})
                else:
                    # If for some reason there are still no questions, end the interview
                    st.session_state.stage = "CONCLUDED"
                    st.session_state.messages.append({"role": "assistant", "content": "Sorry, no technical questions could be generated. The interview is now concluded."})
                    print(f"Got {len(fallback_questions)} fallback questions")
                    
                    if fallback_questions and len(fallback_questions) > 0:
                        first_question = fallback_questions[0]
                        st.session_state.qa_queue = fallback_questions[1:] if len(fallback_questions) > 1 else []
                        
                        st.session_state.current_question = first_question
                        st.session_state.qa_history = [first_question]
                        
                        response = f"I'll ask you a series of technical questions to assess your skills. Let's start:\n\n{first_question}"
                        st.session_state.stage = "QA"
                        st.session_state.messages.append({"role": "assistant", "content": response})
                        print(f"Added first fallback question: {first_question}")
                    else:
                        # Handle case where even fallback questions are missing
                        response = "I'm having trouble generating questions. Let's conclude the interview."
                        st.session_state.stage = "CONCLUDED"
                        st.session_state.messages.append({"role": "assistant", "content": response})
        elif isinstance(field_or_message, str) and len(field_or_message) > 0:
            # We received a guidance message (from context handling)
            response = field_or_message
            st.session_state.messages.append({"role": "assistant", "content": response})
            # Don't show immediately - will be shown on rerun
        else:
            # Normal field processing without special message
            for field in FIELDS:
                if field not in st.session_state.candidate_info:
                    current_field = field
                    break

            fields_order = ["full_name","email","phone","experience_years","desired_positions","location","tech_stack"]
            next_field_idx = fields_order.index(current_field) 

            if next_field_idx + 1 < len(fields_order):
                next_field = fields_order[next_field_idx + 1]
                response = f"Got it! Now please provide your {next_field.replace('_',' ')}."
                st.session_state.messages.append({"role": "assistant", "content": response})
                # Don't show immediately - will be shown on rerun

    # --- Stage: QA / Technical Questions ---
    elif st.session_state.stage == "QA":
        print("QA stage - handling answer")
        followup, next_question = handle_qa(st.session_state, user_input)
        print(f"QA handler returned: followup={followup[:30]}..., next_question={next_question[:30] if next_question else None}")
        
        # Add followup to messages
        st.session_state.messages.append({"role": "assistant", "content": followup})
        print("Added followup to messages")

        if next_question:
            # If we got a next question
            print(f"Got next question: {next_question[:30]}...")
            st.session_state.current_question = next_question
            
            # Only add to messages if it's actually a new question
            duplicate_question = next_question in [msg["content"] for msg in st.session_state.messages]
            if not duplicate_question:
                st.session_state.messages.append({"role": "assistant", "content": next_question})
                print("Added next question to messages")
            else:
                print("Question was duplicate, not adding to messages")
        else:
            # Interview has concluded
            st.session_state.stage = "CONCLUDED"
            save_candidate(st.session_state.candidate_info)

            # Only show the conclusion message if it wasn't already displayed
            # Check if the last message contains "completing" to avoid duplication
            last_messages = [msg["content"] for msg in st.session_state.messages[-3:]]
            conclusion_already_shown = any("completing" in msg.lower() for msg in last_messages)
            
            if not conclusion_already_shown:
                # Display conclusion message with next steps using HTML for better formatting
                conclusion_message = """
### Thank you for completing your technical screening interview! 🎉

Your responses have been recorded and will be evaluated by our team. Here's what happens next:

1. Our team will review your technical answers
2. If your profile matches our requirements, we'll contact you for the next round
3. You should hear back from us within 5 business days

If you have any questions about the process, please contact our HR team at careers@example.com.

Best of luck with your application!
                """
                
                # Add confetti animation for completion
                st.balloons()
                
                # Create an enhanced conclusion message with candidate info
                enhanced_conclusion = conclusion_message + "\n\n#### Your Submitted Information\n"
                
                # Add candidate info to the conclusion message
                for field, value in st.session_state.candidate_info.items():
                    formatted_field = field.replace('_', ' ').title()
                    if field == "tech_stack" and isinstance(value, list):
                        value_str = ", ".join(value)
                    else:
                        value_str = str(value)
                    enhanced_conclusion += f"**{formatted_field}:** {value_str}  \n"
                
                # Store in session state - will be shown on rerun
                st.session_state.messages.append({"role": "assistant", "content": enhanced_conclusion})
                
            # Send thank you email
            candidate_email = st.session_state.candidate_info.get("email")
            candidate_name = st.session_state.candidate_info.get("full_name")
            if candidate_email:
                try:
                    send_thank_you_email_mailjet(candidate_email, candidate_name)
                    st.success(f"✅ A confirmation email has been sent to {candidate_email}")
                except Exception as e:
                    st.warning(f"Could not send email: {str(e)}")

            # Scoring & report
            questions = st.session_state.qa_history if hasattr(st.session_state, "qa_history") else []
            
            # Use qa_pairs if available for better context
            if hasattr(st.session_state, "qa_pairs") and st.session_state.qa_pairs:
                questions = [pair["question"] for pair in st.session_state.qa_pairs]
                answers = [pair["answer"] for pair in st.session_state.qa_pairs]
            else:
                # Fallback to message history
                answers = [msg["content"] for msg in st.session_state.messages if msg["role"] == "user"]
                # Adjust to match number of questions
                answers = answers[-len(questions):] if questions else []

            if questions and answers and len(questions) == len(answers):
                progress_placeholder = st.empty()
                with progress_placeholder.container():
                    with st.spinner("Generating your interview report..."):
                        scoring_json = score_answers_with_gemini(questions, answers)
                    
                    try:
                        scoring = json.loads(scoring_json)
                    except Exception:
                        scoring = scoring_json

                    st.success("📊 Your interview report is ready!")
                    # Create a better formatted report display
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        st.download_button(
                            label="📥 Download Interview Report",
                            data=json.dumps(scoring, indent=2) if isinstance(scoring, list) else str(scoring),
                            file_name="interview_report.json",
                            mime="application/json",
                            use_container_width=True
                        )
                    
                    with col2:
                        if st.button("📊 View Summary Dashboard", use_container_width=True):
                            st.session_state.show_dashboard = True
                    
                    # Optional dashboard view
                    if hasattr(st.session_state, "show_dashboard") and st.session_state.show_dashboard:
                        st.markdown("### Interview Summary Dashboard")
                        try:
                            # Display summary metrics if scoring is in expected format
                            if isinstance(scoring, list):
                                # Calculate average score
                                scores = [q.get("score", 0) for q in scoring if isinstance(q, dict) and "score" in q]
                                if scores:
                                    avg_score = sum(scores) / len(scores)
                                    
                                    # Display metrics
                                    metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
                                    with metrics_col1:
                                        st.metric("Average Score", f"{avg_score:.1f}/10")
                                    with metrics_col2:
                                        st.metric("Questions Answered", len(scores))
                                    with metrics_col3:
                                        sentiment = "Excellent" if avg_score > 8 else "Good" if avg_score > 6 else "Average" if avg_score > 4 else "Needs Improvement"
                                        st.metric("Overall Assessment", sentiment)
                                    
                                    # Show individual question scores
                                    st.markdown("#### Question Breakdown")
                                    for i, q in enumerate(scoring):
                                        if isinstance(q, dict):
                                            with st.expander(f"Q{i+1}: {q.get('question', '')[:50]}..."):
                                                st.write(f"**Question:** {q.get('question', '')}")
                                                st.write(f"**Score:** {q.get('score', 'N/A')}/10")
                                                st.write(f"**Feedback:** {q.get('feedback', 'No feedback provided')}")
                        except Exception as e:
                            st.warning(f"Could not display dashboard: {e}")

            # End of QA process
    # Process completed
    print("Processing completed")
    
    # Add a timestamp to prevent duplicate processing
    st.session_state.last_processed = time.time()
    
    # Reset loading state
    st.session_state.is_loading = False
    print("Reset loading state")
    
    # Clear the user input to prevent reprocessing on refreshes
    if hasattr(st.session_state, "user_input"):
        delattr(st.session_state, "user_input")
        print("Cleared user_input")
        
    # Force a rerun to update the UI immediately
    st.rerun()

# Close the chat container div
st.markdown("</div>", unsafe_allow_html=True)

# # Footer
# st.markdown("---")
# st.markdown("""
# <div style='text-align: center; color: #888; padding: 1rem;'>
#     <p>© 2025 TalentScout AI 
# </div>
# """, unsafe_allow_html=True)
