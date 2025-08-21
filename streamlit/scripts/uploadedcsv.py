import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta

# =====================
# Helper Functions
# =====================

# Helper functions
def parse_time(ts):
    if isinstance(ts, str):
        return datetime.fromisoformat(ts)
    return ts

def filter_RDP_events(data):
    """Filter Remote Desktop Protocol (RDP) related events."""
    rdp_event_ids = {
        "21", "22", "23", "24", "25", "39", "40",
        "1024", "1025", "1026", "1027", "1028", "1029", "1102", "1103"
    }
    
    rdp_events = []
    events_4648 = []
    
    # Loop through all events and categorize them
    for event in data:
        # Check if it's an RDP event
        if ((event.get("Provider") == "Microsoft-Windows-Sysmon" 
             and str(event.get("EventId")) == "3" 
             and event.get("PayloadData2") == "RuleName: RDP")
            or (event.get("Provider") in (
                "Microsoft-Windows-TerminalServices-LocalSessionManager",
                "Microsoft-Windows-TerminalServices-ClientActiveXCore"
            ) and str(event.get("EventId")) in rdp_event_ids)):
            rdp_events.append(event)
        
        # Check if it's a 4648 event
        elif str(event.get("EventId")) == "4648":
            events_4648.append(event)
    
    # Parse and cache times for RDP events
    for event in rdp_events:
        event["ParsedTime"] = parse_time(event.get("TimeCreated"))
    
    # Parse and cache times for 4648 events
    for event in events_4648:
        event["ParsedTime"] = parse_time(event.get("TimeCreated"))
    
    # Get RDP events with EventId 1029
    rdp_events_1029 = [e for e in rdp_events if str(e.get("EventId")) == "1029"]
    
    # Find 4648 events within 10 seconds of 1029 events
    time_window = timedelta(seconds=10)
    relevant_4648_events = []
    
    for event_4648 in events_4648:
        for rdp_event in rdp_events_1029:
            if abs(event_4648["ParsedTime"] - rdp_event["ParsedTime"]) <= time_window:
                relevant_4648_events.append(event_4648)
                break
    
    # Merge all relevant events
    all_events = rdp_events + relevant_4648_events
    
    # Sort by time
    sorted_events = sorted(all_events, key=lambda e: e["ParsedTime"])
    
    # Remove ParsedTime before returning
    for e in sorted_events:
        e.pop("ParsedTime", None)
    
    return sorted_events

def filter_Pwsh_events(data):
    """Filter PowerShell (Pwsh) related events."""
    filtered = [
        e for e in data
        if str(e.get("EventId")) in ("4103", "4104")
    ]
    return sorted(filtered, key=lambda e: e.get("TimeCreated"))

def filter_task_scheduler_events(data):
    """Filter Task Scheduler-related events."""
    filtered = [
        e for e in data
        if e.get("Provider") == "Microsoft-Windows-TaskScheduler"
    ]
    return sorted(filtered, key=lambda e: e.get("TimeCreated"))

# =====================
# Streamlit Page
# =====================

@st.cache_data
def load_csv(file):
    df = pd.read_csv(file)
    return df, df.to_dict(orient="records")

def show_upload_csv_page():
    st.header("Upload CSV")
    st.write("Upload a CSV file and extract specific event types into JSON files.")

    # Initialize session state keys
    if 'extracted_files' not in st.session_state:
        st.session_state.extracted_files = {}
    if 'current_file' not in st.session_state:
        st.session_state.current_file = None

    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

    if uploaded_file is not None:
        # Reset extracted files if new file uploaded
        if uploaded_file != st.session_state.current_file:
            st.session_state.extracted_files = {}
            st.session_state.current_file = uploaded_file

        # Read CSV with caching
        df, records = load_csv(uploaded_file)

        st.write("Preview of uploaded CSV:")
        st.dataframe(df.head())

        # Event type checkboxes
        st.subheader("Select event types to extract:")
        extract_rdp = st.checkbox("RDP Events")
        extract_pwsh = st.checkbox("PowerShell Events")
        extract_tasks = st.checkbox("Task Scheduler Events")

        # Extract button
        if st.button("Extract Events"):
            extracted_files = {}

            if extract_rdp:
                rdp_events = filter_RDP_events(records)
                rdp_json = json.dumps(rdp_events, indent=2)
                extracted_files["RDP_events.json"] = rdp_json
                st.success(f"Extracted {len(rdp_events)} RDP events.")

            if extract_pwsh:
                pwsh_events = filter_Pwsh_events(records)
                pwsh_json = json.dumps(pwsh_events, indent=2)
                extracted_files["PowerShell_events.json"] = pwsh_json
                st.success(f"Extracted {len(pwsh_events)} PowerShell events.")

            if extract_tasks:
                task_events = filter_task_scheduler_events(records)
                task_json = json.dumps(task_events, indent=2)
                extracted_files["TaskScheduler_events.json"] = task_json
                st.success(f"Extracted {len(task_events)} Task Scheduler events.")

            if not extracted_files:
                st.warning("Please select at least one event type.")
            else:
                # Store in session state
                st.session_state.extracted_files = extracted_files

        # Download buttons (persisted using session state)
        if st.session_state.extracted_files:
            st.subheader("Download JSON files")
            for filename, content in st.session_state.extracted_files.items():
                st.download_button(
                    label=f"Download {filename}",
                    data=content,
                    file_name=filename,
                    mime="application/json"
                )

