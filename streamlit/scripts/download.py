import streamlit as st
import os
import sys
import subprocess
from pathlib import Path


def save_uploaded(uploaded, filename):
    """Helper to save uploaded files locally under streamlit/files/"""
    if uploaded is not None:
        save_path = os.path.join(os.getcwd(), "streamlit", "files", filename)
        with open(save_path, "wb") as f:
            f.write(uploaded.getbuffer())
        return save_path
    return None


def run_analysis_and_download(event_type, logs_file, prompt1_file, prompt2_file, param_value):
    """
    Shared pipeline to:
      1. Save uploaded files
      2. Run the analysis script for the given event type
      3. Provide download options for results
    """

    # Save uploads with distinct names
    event_key = event_type.replace(' ', '_').lower()
    logs_path = save_uploaded(logs_file, f"{event_key}_logs")
    prompt1_path = save_uploaded(prompt1_file, f"{event_key}_prompt1")
    prompt2_path = save_uploaded(prompt2_file, f"{event_key}_prompt2")

    # Run analysis button
    if st.button("Run Analysis"):
        if not logs_path or not prompt1_path or not prompt2_path:
            st.error("Please upload all three files for your selected event type before running.")
        else:
            # Select correct script
            if event_type == "Task Scheduler":
                script_name = os.path.join("streamlit/scripts", "analyze_task_scheduler.py")
            elif event_type == "RDP Events":
                script_name = os.path.join("streamlit/scripts", "analyze_rdp_events.py")

            params = [logs_path, prompt1_path, prompt2_path, str(param_value)]
            cmd = [sys.executable, "-u", script_name] + params

            log_placeholder = st.empty()
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )

            logs = ""
            for raw_line in process.stdout:
                logs += raw_line
                log_placeholder.text_area("Live analysis output", logs, height=300)

            exit_code = process.wait()
            if exit_code == 0:
                st.success("Analysis completed successfully!")
            else:
                st.error(f"Analysis script exited with code {exit_code}")

    # Download reports
    st.header("Download Reports")
    output_dir = os.path.join(os.getcwd(), "runs")

    if os.path.isdir(output_dir):
        subfolders = [d.name for d in Path(output_dir).iterdir() if d.is_dir()]
        folder_choice = st.selectbox("Select Output Folder", [""] + subfolders)
        folder_path = os.path.join(output_dir, folder_choice) if folder_choice else output_dir

        if os.path.isdir(folder_path):
            files = sorted([f.name for f in Path(folder_path).iterdir() if f.is_file()])
            if files:
                selected_file = st.selectbox("Pick a file to download", files)
                file_path = os.path.join(folder_path, selected_file)
                with open(file_path, "rb") as f:
                    st.download_button(
                        label="Download",
                        data=f,
                        file_name=selected_file,
                        mime="application/octet-stream"
                    )
            else:
                st.info("No files found in the selected folder.")
        else:
            st.error("Selected folder path is invalid.")
    else:
        st.info("No reports directory found. Please run analysis first.")
