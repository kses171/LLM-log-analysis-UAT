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
    rdp_temperature = st.slider("Temperature", 0.0, 1.0, 0.5)
    return logs_file, prompt1_file, prompt2_file, rdp_temperature
