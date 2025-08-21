import streamlit as st
import requests
import json
import logging
import PyPDF2

logger = logging.getLogger(__name__)

def show_basic_chat_page():
    st.header("Basic Chat with Ollama")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "file_content" not in st.session_state:
        st.session_state.file_content = ""

    # Display chat history
    for role, text in st.session_state.messages:
        speaker = "👤 You" if role == "user" else "🤖 Ollama"
        st.markdown(f"**{speaker}:** {text}")

    # Model settings
    model_name = st.text_input("Model Name", value="mistral:7b")
    system_prompt = st.text_area("System Prompt", value="You are a helpful assistant.", height=100)
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7)
    max_tokens = st.number_input("Max Tokens", min_value=1, value=512)

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
            if role == "user":
                conversation_text += f"User: {text}\n"
            else:
                conversation_text += f"Ollama: {text}\n"

        payload = {
            "model": model_name,
            "prompt": conversation_text,
            "stream": True,  # enable streaming
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }

        reply = ""
        placeholder = st.empty()  # placeholder for live output

        try:
            with requests.post("http://localhost:11434/api/generate", json=payload, stream=True) as r:
                r.raise_for_status()
                for line in r.iter_lines():
                    if line:
                        try:
                            data = json.loads(line.decode("utf-8"))
                            if "response" in data:
                                reply += data["response"]
                                placeholder.markdown(f"**🤖 Ollama:** {reply}")
                        except json.JSONDecodeError:
                            continue  # ignore incomplete lines

            st.session_state.messages.append(("bot", reply.strip()))

        except Exception as e:
            error_msg = f"Error calling Ollama API: {e}"
            st.session_state.messages.append(("bot", error_msg))
            logger.exception(error_msg)
