import streamlit as st
import os
import sys
import subprocess
from pathlib import Path


def show_rdp_events_page():
    st.header("RDP Events: Upload Parameters")
    logs_file = st.file_uploader("Upload RDP Logs File", type=["json"], key="rdp_logs", help="Upload JSON logs")
    prompt1_file = st.file_uploader("Upload RDP Prompt 1 File", type=["txt"], key="rdp_prompt1")
    prompt2_file = st.file_uploader("Upload RDP Prompt 2 File", type=["txt"], key="rdp_prompt2")
    rdp_param_1 = st.number_input(
        "RDP PARAM 1:",
        min_value=0,
        max_value=100,
        value=2,
        step=1,
        help="RDP-specific numeric parameter"
    )
    return logs_file, prompt1_file, prompt2_file, rdp_param_1
