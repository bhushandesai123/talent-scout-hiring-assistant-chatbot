import os
os.environ["LANGCHAIN_VERBOSE"] = "false"

import streamlit as st
from decouple import config
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

st.set_page_config(page_title="TalentScout AI", layout="wide")
st.title("🤖 TalentScout AI - PG-AGI")

# Load ChatHuggingFace
token = config("HUGGINGFACEHUB_API_TOKEN")
endpoint = HuggingFaceEndpoint(
    repo_id="mistralai/Mistral-7B-Instruct-v0.2",
    huggingfacehub_api_token=token,
    temperature=0.1,
    max_new_tokens=250,
    task="conversational"
)
llm = ChatHuggingFace(llm=endpoint)

# === FIXED SEQUENTIAL QUESTIONING SYSTEM ===
QUESTIONS_SEQUENCE = [
    "Hello! Welcome to PG-AGI AI/ML Intern screening. What is your FULL NAME?",
    "Thank you. What is your EMAIL ADDRESS?",
    "Perfect. What is your PHONE NUMBER?",
    "Great. What is your CURRENT LOCATION?",
    "Excellent. How many YEARS OF EXPERIENCE do you have?",
    "Understood. What POSITION are you applying for?",
    "Perfect. List your TECH STACK (Python/Django/AWS/K8s/React/Docker etc):"
]

TECH_QUESTION_PROMPT = """You are a technical interviewer. Based on the candidate's tech stack: {tech_stack}
Generate ONE technical question about {tech_area}. Make it relevant to an AI/ML Intern position.
Format: Just the question, no extra text."""

SYSTEM_PROMPT = """You are PG-AGI TalentScout AI for AI/ML Intern position.
Your role is to ask questions sequentially and generate relevant technical questions based on tech stack.

RULES:
1. Follow the EXACT question sequence provided
2. After tech stack is provided, ask technical questions one by one
3. Keep responses concise and professional
4. Always maintain conversation flow
5. End with closing message after 3 technical questions"""

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": QUESTIONS_SEQUENCE[0]}
    ]
    st.session_state.step = 0
    st.session_state.tech_stack = ""
    st.session_state.tech_questions_asked = 0
    st.session_state.tech_areas = ["Python programming", "ML/AI concepts", "Data structures/algorithms"]

# Store candidate info
if "candidate_info" not in st.session_state:
    st.session_state.candidate_info = {
        "name": "", "email": "", "phone": "", "location": "",
        "experience": "", "position": "", "tech_stack": ""
    }

# Sidebar - Progress tracker
with st.sidebar:
    total_steps = len(QUESTIONS_SEQUENCE) + 3  # 7 info + 3 tech questions
    current_step = st.session_state.step + st.session_state.tech_questions_asked
    st.progress(min(current_step / total_steps, 1.0))
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Info Step", st.session_state.step + 1, 7)
    with col2:
        st.metric("Tech Q", st.session_state.tech_questions_asked, 3)
    
    st.info("💡 Answer each question sequentially")
    
    if st.session_state.tech_stack:
        st.success(f"Tech Stack: {st.session_state.tech_stack}")

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Function to get next question
def get_next_question():
    """Determine the next question based on current state"""
    
    # If we're still in info gathering phase
    if st.session_state.step < len(QUESTIONS_SEQUENCE):
        # Update candidate info based on last response
        if st.session_state.step > 0 and st.session_state.messages:
            user_messages = [m for m in st.session_state.messages if m["role"] == "user"]
            if len(user_messages) >= st.session_state.step:
                last_answer = user_messages[-1]["content"]
                
                # Map step to info field
                if st.session_state.step == 1:  # Name
                    st.session_state.candidate_info["name"] = last_answer
                elif st.session_state.step == 2:  # Email
                    st.session_state.candidate_info["email"] = last_answer
                elif st.session_state.step == 3:  # Phone
                    st.session_state.candidate_info["phone"] = last_answer
                elif st.session_state.step == 4:  # Location
                    st.session_state.candidate_info["location"] = last_answer
                elif st.session_state.step == 5:  # Experience
                    st.session_state.candidate_info["experience"] = last_answer
                elif st.session_state.step == 6:  # Position
                    st.session_state.candidate_info["position"] = last_answer
                elif st.session_state.step == 7:  # Tech Stack
                    st.session_state.candidate_info["tech_stack"] = last_answer
                    st.session_state.tech_stack = last_answer
        
        return QUESTIONS_SEQUENCE[st.session_state.step]
    
    # If we're in technical questioning phase
    elif st.session_state.tech_questions_asked < 3:
        if st.session_state.tech_stack:
            # Use LLM to generate technical question
            tech_area = st.session_state.tech_areas[st.session_state.tech_questions_asked]
            prompt = TECH_QUESTION_PROMPT.format(
                tech_stack=st.session_state.tech_stack,
                tech_area=tech_area
            )
            
            messages = [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=prompt)
            ]
            
            response = llm.invoke(messages)
            question = f"**TECH QUESTION {st.session_state.tech_questions_asked + 1}**: {response.content.strip()}"
            return question
        else:
            return "Please list your tech stack first so I can ask relevant technical questions."
    
    # All questions completed
    else:
        return "**SCREENING COMPLETE**: Thank you for your time! The PG-AGI team will review your responses and contact you within 48 hours."

# Handle user input
if user_input := st.chat_input("Type your answer here..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Check for exit commands
    exit_commands = ["bye", "exit", "stop", "quit", "end"]
    if any(cmd in user_input.lower() for cmd in exit_commands):
        st.session_state.messages.append({
            "role": "assistant", 
            "content": "Thank you for your time! The screening session has ended. Have a great day!"
        })
        st.rerun()
    
    # Determine next step
    if st.session_state.step < len(QUESTIONS_SEQUENCE):
        # Move to next info question
        if st.session_state.step == 6 and user_input:  # After tech stack
            st.session_state.tech_stack = user_input
        
        st.session_state.step += 1
    elif st.session_state.tech_questions_asked < 3:
        # Move to next tech question
        st.session_state.tech_questions_asked += 1
    
    # Get and add next question
    next_question = get_next_question()
    st.session_state.messages.append({"role": "assistant", "content": next_question})
    
    st.rerun()

# Display candidate info summary (for debugging/verification)
with st.expander("Candidate Information (Preview)"):
    st.json(st.session_state.candidate_info)

st.markdown("---")
st.caption("PG-AGI AI/ML Intern Screening System | TalentScout AI Assistant")
ubuntu@ip-10-0-2-43:~/talent-scout$ 
