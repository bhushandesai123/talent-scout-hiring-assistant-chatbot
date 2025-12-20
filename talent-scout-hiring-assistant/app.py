import streamlit as st
import re
import os
from huggingface_hub import InferenceClient

st.set_page_config(page_title="TalentScout AI Hiring Assistant", page_icon="🤖", layout="centered")

st.title("🤖 TalentScout AI Hiring Assistant")
st.markdown("*AI-powered initial screening for technology placements*")

# ======================
# INITIALIZE SESSION STATE
# ======================
if "step" not in st.session_state:
    st.session_state.step = 0
    st.session_state.name = ""
    st.session_state.email = ""
    st.session_state.phone = ""
    st.session_state.exp = ""
    st.session_state.job = ""
    st.session_state.city = ""
    st.session_state.tech = ""
    st.session_state.questions = []
    st.session_state.current_q = 0
    st.session_state.answers = {}
    st.session_state.screening_ended = False
    st.session_state.greet_shown = False

# ======================
# HELPER FUNCTIONS
# ======================
def check_exit(text):
    """Check if user wants to exit"""
    exit_words = ["exit", "quit", "bye", "goodbye", "stop", "end", "cancel"]
    return text.lower().strip() in exit_words

def validate_name(name):
    """Validate full name"""
    return len(name.strip()) >= 2 and name.replace(" ", "").isalpha()

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email.strip()) is not None

def validate_phone(phone):
    """Validate phone number (10 digits)"""
    digits = re.sub(r'\D', '', phone)
    return len(digits) == 10

def validate_exp(exp):
    """Validate experience (0-50 years)"""
    return exp.isdigit() and 0 <= int(exp) <= 50

def validate_general(text):
    """General text validation"""
    return len(text.strip()) >= 2

def generate_hf_questions(tech_stack, experience):
    """Generate 3-5 questions using Hugging Face LLM"""
    try:
        # Get Hugging Face token
        hf_token = os.getenv("HF_TOKEN") or st.secrets.get("HF_TOKEN", "")
        
        if not hf_token:
            return get_fallback_questions(tech_stack)
        
        # Initialize client
        client = InferenceClient(
            token=hf_token,
            model="mistralai/Mistral-7B-Instruct-v0.1"
        )
        
        # Create prompt
        prompt = f"""Generate 3-5 technical interview questions.

Candidate has {experience} years experience.
Tech Stack: {tech_stack}

Instructions:
1. Generate exactly 3-5 questions
2. Questions should test practical knowledge
3. Cover different technologies mentioned
4. Difficulty should match experience level
5. Format as numbered list (1., 2., 3., etc.)

Technical Questions:"""
        
        # Call Hugging Face API
        with st.spinner("🤖 Generating questions with AI..."):
            response = client.text_generation(
                prompt,
                max_new_tokens=250,
                temperature=0.7,
                do_sample=True
            )
        
        # Parse response
        questions = []
        lines = response.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-') or line.startswith('*')):
                # Clean the question
                q = re.sub(r'^[0-9]+[\.\)]\s*', '', line)
                q = re.sub(r'^[-\*]\s*', '', q)
                if q and len(q) > 10:
                    questions.append(q)
        
        return questions[:5] if questions else get_fallback_questions(tech_stack)
        
    except Exception:
        return get_fallback_questions(tech_stack)

def get_fallback_questions(tech_stack):
    """Fallback questions if LLM fails"""
    techs = [t.strip().lower() for t in tech_stack.split(",") if t.strip()]
    questions = []
    
    # Tech to question mapping
    tech_map = {
        "python": ["Explain Python decorators with example.", "Difference between list and tuple?"],
        "java": ["What is polymorphism in Java?", "Explain Java collections."],
        "javascript": ["What is closure in JavaScript?", "Explain event loop."],
        "react": ["What are React hooks?", "Explain virtual DOM."],
        "aws": ["Difference between EC2 and Lambda?", "What is S3 used for?"],
        "sql": ["Explain different SQL joins.", "What are database indexes?"],
        "docker": ["Docker vs virtual machines?", "What is Dockerfile?"],
        "node": ["What is event-driven programming?", "Explain callback hell."]
    }
    
    # Get questions for each tech
    for tech in techs[:3]:
        for key in tech_map:
            if key in tech:
                questions.extend(tech_map[key][:1])  # 1 question per tech
                break
    
    # Ensure 3-5 questions
    if len(questions) < 3:
        questions.extend([
            "Describe your experience with these technologies.",
            "Explain a challenging project you worked on.",
            "How do you stay updated with technology trends?"
        ])
    
    return questions[:5]

# ======================
# GREETING
# ======================
if not st.session_state.greet_shown:
    st.chat_message("assistant").write("👋 Hello! I'm TalentScout AI Hiring Assistant. I'll help with your initial screening. Type 'exit' anytime to end.")
    st.session_state.greet_shown = True

# ======================
# EXIT HANDLING
# ======================
if st.session_state.screening_ended:
    st.chat_message("assistant").write("👋 Screening ended. Thank you for your time!")
    if st.button("Start New Screening"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    st.stop()

# ======================
# STEP 1: INFORMATION COLLECTION (7 QUESTIONS)
# ======================
if st.session_state.step == 0:  # Name
    st.chat_message("assistant").write("What is your full name?")
    user_input = st.chat_input("Type your name...")
    
    if user_input:
        if check_exit(user_input):
            st.session_state.screening_ended = True
            st.rerun()
        
        if validate_name(user_input):
            st.session_state.name = user_input
            st.chat_message("user").write(user_input)
            st.session_state.step = 1
            st.rerun()
        else:
            st.chat_message("assistant").write("❌ Please enter a valid name (letters only, at least 2 characters)")
            st.rerun()

elif st.session_state.step == 1:  # Email
    st.chat_message("assistant").write("What is your email address?")
    user_input = st.chat_input("Type email...")
    
    if user_input:
        if check_exit(user_input):
            st.session_state.screening_ended = True
            st.rerun()
        
        if validate_email(user_input):
            st.session_state.email = user_input
            st.chat_message("user").write(user_input)
            st.session_state.step = 2
            st.rerun()
        else:
            st.chat_message("assistant").write("❌ Please enter valid email (name@example.com)")
            st.rerun()

elif st.session_state.step == 2:  # Phone
    st.chat_message("assistant").write("What is your phone number? (10 digits)")
    user_input = st.chat_input("Type phone...")
    
    if user_input:
        if check_exit(user_input):
            st.session_state.screening_ended = True
            st.rerun()
        
        if validate_phone(user_input):
            st.session_state.phone = user_input
            st.chat_message("user").write(user_input)
            st.session_state.step = 3
            st.rerun()
        else:
            st.chat_message("assistant").write("❌ Please enter 10-digit phone number")
            st.rerun()

elif st.session_state.step == 3:  # Experience
    st.chat_message("assistant").write("How many years of experience? (0-50)")
    user_input = st.chat_input("Type years...")
    
    if user_input:
        if check_exit(user_input):
            st.session_state.screening_ended = True
            st.rerun()
        
        if validate_exp(user_input):
            st.session_state.exp = user_input
            st.chat_message("user").write(user_input)
            st.session_state.step = 4
            st.rerun()
        else:
            st.chat_message("assistant").write("❌ Please enter number between 0-50")
            st.rerun()

elif st.session_state.step == 4:  # Position
    st.chat_message("assistant").write("What position are you applying for?")
    user_input = st.chat_input("Type position...")
    
    if user_input:
        if check_exit(user_input):
            st.session_state.screening_ended = True
            st.rerun()
        
        if validate_general(user_input):
            st.session_state.job = user_input
            st.chat_message("user").write(user_input)
            st.session_state.step = 5
            st.rerun()
        else:
            st.chat_message("assistant").write("❌ Please enter valid position")
            st.rerun()

elif st.session_state.step == 5:  # Location
    st.chat_message("assistant").write("Where are you currently located?")
    user_input = st.chat_input("Type location...")
    
    if user_input:
        if check_exit(user_input):
            st.session_state.screening_ended = True
            st.rerun()
        
        if validate_general(user_input):
            st.session_state.city = user_input
            st.chat_message("user").write(user_input)
            st.session_state.step = 6
            st.rerun()
        else:
            st.chat_message("assistant").write("❌ Please enter valid location")
            st.rerun()

elif st.session_state.step == 6:  # Tech Stack
    st.chat_message("assistant").write("What is your tech stack? (comma separated, e.g., Python, React, AWS)")
    user_input = st.chat_input("Type tech stack...")
    
    if user_input:
        if check_exit(user_input):
            st.session_state.screening_ended = True
            st.rerun()
        
        if validate_general(user_input):
            st.session_state.tech = user_input
            st.chat_message("user").write(user_input)
            
            # Generate technical questions using Hugging Face
            questions = generate_hf_questions(user_input, st.session_state.exp)
            st.session_state.questions = questions
            
            st.chat_message("assistant").write(f"✅ Generated {len(questions)} technical questions!")
            st.session_state.step = 7
            st.rerun()
        else:
            st.chat_message("assistant").write("❌ Please enter valid tech skills")
            st.rerun()

# ======================
# STEP 2: TECHNICAL QUESTIONS (SHOW ONE BY ONE)
# ======================
elif st.session_state.step == 7:
    questions = st.session_state.questions
    current_q = st.session_state.current_q
    
    # Check if questions exist
    if not questions:
        st.chat_message("assistant").write("⚠️ No questions generated. Moving to completion.")
        st.session_state.step = 8
        st.rerun()
    
    # Check if all questions answered
    if current_q >= len(questions):
        st.session_state.step = 8
        st.rerun()
    
    # Display current question
    question_text = questions[current_q]
    total_q = len(questions)
    
    # Show progress
    st.progress((current_q + 1) / total_q)
    st.caption(f"Question {current_q + 1} of {total_q}")
    
    # Show question in chat (only once)
    if "last_q_shown" not in st.session_state or st.session_state.last_q_shown != current_q:
        st.chat_message("assistant").write(f"**Question {current_q + 1}:** {question_text}")
        st.session_state.last_q_shown = current_q
        st.rerun()
    
    # Answer input
    answer = st.text_area(
        "**Your answer:**",
        key=f"ans_{current_q}",
        height=150,
        placeholder="Type your detailed answer here..."
    )
    
    # Buttons
    col1, col2 = st.columns(2)
    
    with col1:
        submit_clicked = st.button("✅ Submit Answer", key=f"sub_{current_q}", type="primary")
    
    with col2:
        skip_clicked = st.button("⏭️ Skip Question", key=f"skip_{current_q}")
    
    # Handle button clicks
    if submit_clicked:
        if answer.strip():
            if check_exit(answer):
                st.session_state.screening_ended = True
                st.rerun()
            
            # Store answer
            st.session_state.answers[current_q] = answer
            st.chat_message("user").write(f"**Answer:** {answer[:100]}...")
            
            # Move to next question
            st.session_state.current_q += 1
            if "last_q_shown" in st.session_state:
                del st.session_state.last_q_shown
            
            st.rerun()
        else:
            st.warning("Please enter an answer.")
    
    if skip_clicked:
        st.session_state.current_q += 1
        if "last_q_shown" in st.session_state:
            del st.session_state.last_q_shown
        st.rerun()
    
    # Instructions
    st.markdown("---")
    st.caption("💡 Provide specific examples. Type 'exit' to end screening.")

# ======================
# STEP 3: COMPLETION
# ======================
elif st.session_state.step == 8:
    # Celebration
    st.balloons()
    
    # Completion message
    st.chat_message("assistant").write("""
    🎉 **Screening Successfully Completed!**
    
    Thank you for completing the technical assessment.
    
    **Next Steps:**
    1. Our team will review your responses
    2. You'll hear back within 3-5 business days
    3. Next round: Technical interview
    
    We appreciate your time and interest in TalentScout!
    """)
    
    # Show summary
    with st.expander("📋 View Your Screening Summary", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Personal Information:**")
            st.write(f"- Name: {st.session_state.name}")
            st.write(f"- Email: {st.session_state.email}")
            st.write(f"- Phone: {st.session_state.phone}")
            st.write(f"- Location: {st.session_state.city}")
        
        with col2:
            st.write("**Professional Information:**")
            st.write(f"- Experience: {st.session_state.exp} years")
            st.write(f"- Position: {st.session_state.job}")
            st.write(f"- Tech Stack: {st.session_state.tech}")
            st.write(f"- Questions Answered: {len(st.session_state.answers)}/{len(st.session_state.questions)}")
    
    # Start new screening button
    if st.button("🔄 Start New Screening", type="primary"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# ======================
# SIDEBAR
# ======================
with st.sidebar:
    st.markdown("### 📋 Candidate Info")
    st.markdown("---")
    
    if st.session_state.name:
        st.write(f"**Name:** {st.session_state.name}")
    if st.session_state.email:
        st.write(f"**Email:** {st.session_state.email}")
    if st.session_state.phone:
        st.write(f"**Phone:** {st.session_state.phone}")
    if st.session_state.exp:
        st.write(f"**Experience:** {st.session_state.exp} years")
    if st.session_state.job:
        st.write(f"**Position:** {st.session_state.job}")
    if st.session_state.city:
        st.write(f"**Location:** {st.session_state.city}")
    if st.session_state.tech:
        st.write(f"**Tech Stack:** {st.session_state.tech}")
    
    st.markdown("---")
    
    # Progress indicator
    if st.session_state.step <= 6:
        progress = st.session_state.step / 6
        st.progress(progress)
        st.caption(f"Step {st.session_state.step + 1}/7")
    elif st.session_state.step == 7 and st.session_state.questions:
        total_q = len(st.session_state.questions)
        current_q = min(st.session_state.current_q, total_q)
        if total_q > 0:
            progress = current_q / total_q
            st.progress(progress)
            st.caption(f"Question {current_q + 1}/{total_q}")
    
    st.markdown("---")
    
    # Restart button
    if st.button("🔄 Restart Screening", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 🤖 Powered By")
    st.caption("""
    **Hugging Face LLM**
    - Mistral-7B model
    - AI-generated questions
    - Real-time processing
    """)
    
    st.markdown("---")
    st.caption("🔐 Data processed locally | For demonstration purposes")

# ======================
# FOOTER
# ======================
st.markdown("---")
st.caption("TalentScout AI Hiring Assistant | AI/ML Intern Assignment | Powered by Hugging Face")