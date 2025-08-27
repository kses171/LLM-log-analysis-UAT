import streamlit as st
import logging
import PyPDF2
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

# ──────────────────────────────
# Project imports
# ──────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
from LLM_APIs.llm_local import call_local_llm
from LLM_APIs.llm_bedrock import call_bedrock


def show_basic_chat_page():
    st.header("Basic Chat with LLM")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "file_content" not in st.session_state:
        st.session_state.file_content = ""

    # Display chat history
    for role, text in st.session_state.messages:
        speaker = "You" if role == "user" else "Bot"
        st.markdown(f"**{speaker}:** {text}")

    # Model + provider selection
    provider = st.radio("LLM Provider", ["AWS Bedrock", "Ollama (NUS Server)"])
    model_name = st.text_input("Model Name", value="apac.anthropic.claude-sonnet-4-20250514-v1:0")
    system_prompt = st.text_area("System Prompt", value="You are a helpful assistant.", height=100)
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7)
    max_tokens = st.number_input("Max Tokens", min_value=1, value=8192)

    # File upload
    uploaded_file = st.file_uploader("Attach a file", type=["txt", "md", "csv", "json", "pdf"])
    if uploaded_file is not None:
        try:
            if uploaded_file.type == "application/pdf":
                # If you want PDF support, need PyPDF2 or pdfplumber
                reader = PyPDF2.PdfReader(uploaded_file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() or ""
                st.session_state.file_content = text
            else:
                st.session_state.file_content = uploaded_file.read().decode("utf-8", errors="ignore")
            
            st.success(f"File '{uploaded_file.name}' uploaded and content added to context.")
        except Exception as e:
            st.error(f"Error reading file: {e}")

    # User input
    user_input = st.text_area("Your message:", key="chat_input", height=100)

    if st.button("Send") and user_input.strip():
        st.session_state.messages.append(("user", user_input))

        # Combine messages into one prompt
        conversation_text = system_prompt + "\n"

        # Include uploaded file context (if any)
        if st.session_state.file_content:
            conversation_text += f"\n[Attached File Content]\n{st.session_state.file_content}\n\n"

        for role, text in st.session_state.messages:
            conversation_text += f"{'User' if role == 'user' else 'Bot'}: {text}\n"

        reply = ""
        placeholder = st.empty()  # placeholder for live output

        if provider == "Local Ollama":
            generator = call_local_llm(model_name, conversation_text, temperature, max_tokens)
        else:
            generator = call_bedrock(model_name, conversation_text, temperature, max_tokens)

        for partial in generator:
            reply = partial or ""
            placeholder.markdown(f"**Bot:** {reply}")

        st.session_state.messages.append(("bot", reply.strip()))
