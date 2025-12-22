import streamlit as st
import re, json
from decouple import config
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

# PAGE SET

st.set_page_config(page_title="TalentScout", page_icon="🤖", layout="centered")
st.title("🤖 TalentScout Hiring Assistant")

# LOADING UR PROMPTS.JSON
with open("prompts.json", "r") as f:
    PROMPTS = json.load(f)

# LLM I CALL BY LANGCHAIN CODE WE GOT FROM LANGCHAIN SITE FOR HUGGINGFACE
key = config("HUGGINGFACEHUB_API_TOKEN")
repo_id = "meta-llama/Llama-3.1-8B-Instruct"

llm = HuggingFaceEndpoint(
    repo_id=repo_id,
    temperature=0.7,
    max_new_tokens=300,
    huggingfacehub_api_token=key
)
model = ChatHuggingFace(llm=llm)

# SESSION STATE = SO WE GET ALL HISTORY I ASKED TO NEW USER, USER I/P I GET HERE
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

# VALIDATION HELPERS WE GET FROM INTERNET DIRECT COPY
def check_exit(text: str) -> bool:
    return text.lower().strip() in ["exit", "quit", "bye", "goodbye", "stop", "end", "cancel"]

def validate_name(name: str) -> bool:
    return len(name.strip()) >= 2 and name.replace(" ", "").isalpha()

def validate_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email.strip()) is not None

def validate_phone(phone: str) -> bool:
    digits = re.sub(r"\D", "", phone)
    return len(digits) == 10

def validate_exp(exp: str) -> bool:
    return exp.isdigit() and 0 <= int(exp) <= 50

def validate_general(text: str) -> bool:
    return len(text.strip()) >= 2

# LLM QUESTION GENERATOR
def generate_questions(tech: str, exp: str):
    try:
        prompt = PROMPTS["tech_prompt"].format(experience=exp, tech_stack=tech)
        response = model.invoke(prompt)
        questions = []
        for line in response.content.split("\n"):
            line = line.strip()
            if line.startswith(("1.", "2.", "3.")):
                q = line.split(".", 1)[1].strip()
                questions.append(q)
        return questions[:3] if questions else PROMPTS["fallback"]
    except Exception:
        return PROMPTS["fallback"]

# GREETING - MY ASSIGNMENT THEY WANT THIS SO .....
if not st.session_state.greet_shown:
    st.chat_message("assistant").write(PROMPTS["greeting"])
    st.session_state.greet_shown = True

# EXIT - my app wants to exit,if i say some exit relatedc words
if st.session_state.screening_ended:
    st.chat_message("assistant").write(PROMPTS["farewell"])
    if st.button("🔄 Start New Screening"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    st.stop()

# STEP 0–6: collect info i want from user
if st.session_state.step == 0:
    # Name
    st.chat_message("assistant").write(PROMPTS["questions"][0])
    user_input = st.chat_input("Full name...")
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
            st.chat_message("assistant").write("❌ Please enter a valid full name.")

elif st.session_state.step == 1:
    # Email
    st.chat_message("assistant").write(PROMPTS["questions"][1])
    user_input = st.chat_input("Email address...")
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
            st.chat_message("assistant").write("❌ Please enter a valid email (name@example.com).")

elif st.session_state.step == 2:
    # Phone
    st.chat_message("assistant").write(PROMPTS["questions"][2])
    user_input = st.chat_input("Phone number...")
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
            st.chat_message("assistant").write("❌ Please enter a 10-digit phone number.")

elif st.session_state.step == 3:
    # Experience
    st.chat_message("assistant").write(PROMPTS["questions"][3])
    user_input = st.chat_input("Years of experience...")
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
            st.chat_message("assistant").write("❌ Please enter a number between 0 and 50.")

elif st.session_state.step == 4:
    # Position
    st.chat_message("assistant").write(PROMPTS["questions"][4])
    user_input = st.chat_input("Desired position...")
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
            st.chat_message("assistant").write("❌ Please enter a valid position.")

elif st.session_state.step == 5:
    # Location
    st.chat_message("assistant").write(PROMPTS["questions"][5])
    user_input = st.chat_input("Current location...")
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
            st.chat_message("assistant").write("❌ Please enter a valid location.")

elif st.session_state.step == 6:
    # Tech Stack
    st.chat_message("assistant").write(PROMPTS["questions"][6])
    user_input = st.chat_input("Tech stack...")
    if user_input:
        if check_exit(user_input):
            st.session_state.screening_ended = True
            st.rerun()
        if validate_general(user_input):
            st.session_state.tech = user_input
            st.chat_message("user").write(user_input)
            # Generate questions now
            st.session_state.questions = generate_questions(user_input, st.session_state.exp)
            st.chat_message("assistant").write(f"✅ Generated {len(st.session_state.questions)} technical questions.")
            st.session_state.step = 7
            st.rerun()
        else:
            st.chat_message("assistant").write("❌ Please enter a valid tech stack.")

# STEP 7: ASK 1 by 1 question to user
elif st.session_state.step == 7:
    total = len(st.session_state.questions)
    current = st.session_state.current_q

    if current < total:
        st.progress((current + 1) / total)
        question = st.session_state.questions[current]
        st.chat_message("assistant").write(f"**Technical Question {current + 1}/{total}:** {question}")
        answer = st.text_area("Your answer:", height=120, key=f"tech_q_{current}")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Submit & Next", type="primary"):
                if answer.strip():
                    st.session_state.answers[current] = answer
                    st.session_state.current_q += 1
                    st.rerun()
                else:
                    st.warning("Please enter an answer or use Skip.")
        with col2:
            if st.button("⏭️ Skip"):
                st.session_state.current_q += 1
                st.rerun()
    else:
        st.session_state.step = 8
        st.rerun()

# STEP 8: SUMMARY 
elif st.session_state.step == 8:
    st.balloons()
    st.success("🎉 Screening Complete!")

    st.markdown("### 📋 Candidate Summary")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Name:** {st.session_state.name}")
        st.write(f"**Email:** {st.session_state.email}")
        st.write(f"**Phone:** {st.session_state.phone}")
    with col2:
        st.write(f"**Experience:** {st.session_state.exp} years")
        st.write(f"**Position:** {st.session_state.job}")
        st.write(f"**Location:** {st.session_state.city}")
        st.write(f"**Tech Stack:** {st.session_state.tech}")

    st.caption(f"Answered {len(st.session_state.answers)}/{len(st.session_state.questions)} technical questions.")

    if st.button("🔄 Start New Screening"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
