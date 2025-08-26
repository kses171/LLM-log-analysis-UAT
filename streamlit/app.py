import streamlit as st
import subprocess
import sys
import os
import requests
from pathlib import Path
from scripts.basic_chat import show_basic_chat_page
from scripts.rdp_events import show_rdp_events_page
from scripts.task_scheduler import show_task_scheduler_page
from scripts.download import run_analysis_and_download
from scripts.uploadedcsv import show_upload_csv_page


# resolve project root: two levels up from this script file
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

# Title
st.title("Windows Event Log Analyzer")

# Dropdown for event type
event_type = st.selectbox(
    "Choose Event Type to Analyze:",
    ("Task Scheduler", "Upload CSV", "Basic Chat", "RDP Events")
)

# BASIC CHAT SECTION
if event_type == "Basic Chat":
    show_basic_chat_page()
elif event_type == "Task Scheduler":
    logs_file, prompt1_file, prompt2_file, ts_param_1 = show_task_scheduler_page()
    run_analysis_and_download(event_type, logs_file, prompt1_file, prompt2_file, ts_param_1)
elif event_type == "RDP Events":
    logs_file, prompt1_file, prompt2_file, rdp_param_1 = show_rdp_events_page()
    run_analysis_and_download(event_type, logs_file, prompt1_file, prompt2_file, rdp_param_1)
elif event_type == "Upload CSV":
    show_upload_csv_page()

# Footer
st.markdown("---")
st.caption("Developed with Streamlit")
