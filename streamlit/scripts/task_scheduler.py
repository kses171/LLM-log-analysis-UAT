import streamlit as st


def show_task_scheduler_page():
    st.header("Task Scheduler: Upload Parameters")
    logs_file = st.file_uploader("Upload TS Logs File", type=["json"], key="ts_logs")
    prompt1_file = st.file_uploader("Upload TS Prompt 1 File", type=["txt"], key="ts_prompt1")
    prompt2_file = st.file_uploader("Upload TS Prompt 2 File", type=["txt"], key="ts_prompt2")
    ts_param_1 = st.number_input(
        "TS PARAM 1:",
        min_value=0,
        max_value=100,
        value=10,
        step=1,
        help="TS-specific numeric parameter"
    )
    return logs_file, prompt1_file, prompt2_file, ts_param_1
