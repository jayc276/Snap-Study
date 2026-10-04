from google import genai
import streamlit as st

from google.genai import types

import smtplib
from email.message import EmailMessage

from prompts import SYSTEM_PROMPT, WELCOME_MESSAGE_TEMPLATE, SUMMARY_REQUEST_PROMPT

st.set_page_config(
    page_title="Snap & Study",
    page_icon="📚",
    layout="wide",
)

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

GMAIL_ADDRESS = st.secrets["GMAIL_ADDRESS"]
GMAIL_APP_PASSWORD = st.secrets["GMAIL_APP_PASSWORD"]

MODEL_NAME = "gemini-3.8-flash"

@st.cache_resource
def get_gemini_client():
    retry_options = types.HttpRetryOptions(
        attempts=7,
        initial_delay=1,
        max_delay=15,
        exp_base=2,
        jitter=1,
        http_status_codes=[500, 502, 503, 504],
    )

    return genai.Client(
        api_key=GEMINI_API_KEY,
        http_options=types.HttpOptions(
            retry_options=retry_options
        ),
    )


gemini_client = get_gemini_client()

if "messages" not in st.session_state:
    st.session_state.messages = []

def render_message(message):
    with st.chat_message(message["role"]):
        if message["kind"] == "text":
            st.write(message["content"])
        elif message["kind"] == "image":
            st.image(message["content"])


def add_message(role, kind, content):
    st.session_state.messages.append(
        {
            "role": role,
            "kind": kind,
            "content": content,
        }
    )
    render_message(st.session_state.messages[-1])

def ask_gemini(parts):
    try:
        response = st.session_state.chat.send_message(parts)
        return response.text

    except Exception as error:
        error_message = str(error)

        if "429" in error_message or "RESOURCE_EXHAUSTED" in error_message:
            return (
                "⚠️ The study AI has reached its current usage limit. "
                "Please try again later."
            )

        if "503" in error_message or "UNAVAILABLE" in error_message:
            return (
                "⚠️ The study AI is temporarily busy. "
                "Please try again in a little while."
            )

        if "401" in error_message or "403" in error_message:
            return (
                "⚠️ There is a problem with the Gemini API configuration. "
                "Please check the API settings."
            )

        return (
            "⚠️ Something went wrong while processing your request. "
            "Please try again."
        )

def send_email(to_email, user_name, summary):
    try:
        message = EmailMessage()

        message["Subject"] = "📚 Your Snap & Study Summary"
        message["From"] = GMAIL_ADDRESS
        message["To"] = to_email

        message.set_content(
            f"""Hi {user_name},

Here is your Snap & Study summary:

{summary}

Keep learning! 📚
"""
        )

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            server.send_message(message)

        return True, "Email sent successfully."

    except Exception as error:
        return False, str(error)


# Onboarding
if "onboarded" not in st.session_state:
    st.title("📚 Snap & Study")
    st.caption("Snap a problem. Understand the concept. Study smarter.")

    with st.form("onboarding_form"):
        name = st.text_input("Your name")

        email = st.text_input(
            "Your email address",
            placeholder="example@gmail.com",
        )

        submitted = st.form_submit_button("Let's study 🚀")

    if submitted:
        if not name.strip() or not email.strip():
            st.warning("Please enter your name and email address.")
        elif "@" not in email or "." not in email.split("@")[-1]:
            st.warning("Please enter a valid email address.")
        else:
            st.session_state.name = name.strip()
            st.session_state.email = email.strip()

            st.session_state.chat = gemini_client.chats.create(
                model=MODEL_NAME,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT
                ),
            )

            st.session_state.messages = []
            st.session_state.onboarded = True

            st.rerun()

    st.stop()

# Send to Email Button / Application Header
header_col, email_col, clear_col = st.columns(
    [5, 1.5, 1.5],
    vertical_alignment="center",
)

with header_col:
    st.title("📚 Snap & Study")
    st.caption("Your AI study companion for questions, diagrams, problems, and notes.")

with email_col:
    send_disabled = len(st.session_state.messages) <= 1
    
    if st.button(
        "📧 Save to Email",
        disabled=send_disabled,
        use_container_width=True,
    ):
        with st.spinner("Preparing your study summary..."):
            summary = ask_gemini([SUMMARY_REQUEST_PROMPT])

        success, info = send_email(
            st.session_state.email,
            st.session_state.name,
            summary,
        )

        if success:
            st.success("Study summary saved! Check your email 📧")
        else:
            st.error(f"Couldn't send the study summary: {info}")
            
with clear_col:
    if st.button(
        "🗑️ Clear Chat",
        use_container_width=True,
    ):
        st.session_state.messages = []

        st.session_state.chat = gemini_client.chats.create(
            model=MODEL_NAME,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT
            ),
        )

        st.rerun()

# Chat interface
if not st.session_state.messages:
    add_message(
        "assistant",
        "text",
        WELCOME_MESSAGE_TEMPLATE.format(
            name=st.session_state.name
        ),
    )
else:
    for message in st.session_state.messages:
        render_message(message)

if not st.session_state.messages or len(st.session_state.messages) == 1:
    st.caption(
        "📸 Upload a question, diagram, or notes — "
        "you can also add an instruction with your image."
    )
    
user_input = st.chat_input(
    "Ask a question or attach a photo of your study material...",
    accept_file=True,
    file_type=["jpg", "jpeg", "png"],
)


if user_input:
    photo = user_input.files[0] if user_input.files else None
    text = user_input.text
    parts = []

    if photo is not None:
        photo_bytes = photo.getvalue()

        add_message("user", "image", photo_bytes)

        parts.append(
            types.Part.from_bytes(
                data=photo_bytes,
                mime_type=photo.type,
            )
        )

    if text:
        add_message("user", "text", text)
        parts.append(text)

    elif photo is not None:
        parts.append(
            "Explain this study material in simple language. "
            "Identify the topic, explain the main concept, "
            "and give the important points to remember."
        )

    with st.spinner("Understanding your study material..."):
        answer = ask_gemini(parts)

    add_message("assistant", "text", answer)