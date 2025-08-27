import streamlit as st


def show_task_scheduler_page():
    st.header("Task Scheduler: Upload Parameters")
    logs_file = st.file_uploader("Upload TS Logs File", type=["json"], key="ts_logs")
    prompt1_file = st.file_uploader("Upload TS Prompt 1 File", type=["txt"], key="ts_prompt1")
    prompt2_file = st.file_uploader("Upload TS Prompt 2 File", type=["txt"], key="ts_prompt2")
    ts_temperature = st.slider("Temperature", 0.0, 1.0, 0.5)
    return logs_file, prompt1_file, prompt2_file, ts_temperature
