#!/usr/bin/env python3
"""
Simple test script for Task Scheduler log analysis.
Usage: python analyze_task_scheduler.py <logs_path> <prompt1_path> <prompt2_path> <ts_param_1>
"""

import sys
import os
from datetime import datetime

def main():
    if len(sys.argv) != 5:
        print("Error: Expected 4 arguments")
        print("Usage: python analyze_task_scheduler.py <logs_path> <prompt1_path> <prompt2_path> <ts_param_1>")
        sys.exit(1)
    
    logs_path = sys.argv[1]
    prompt1_path = sys.argv[2]
    prompt2_path = sys.argv[3]
    ts_param_1 = sys.argv[4]
    
    print("Task Scheduler Analysis Started")
    print(f"Logs file: {logs_path}")
    print(f"Prompt 1 file: {prompt1_path}")
    print(f"Prompt 2 file: {prompt2_path}")
    print(f"TS Parameter 1: {ts_param_1}")
    
    # Simulate reading files
    try:
        # Check if files exist
        for file_path in [logs_path, prompt1_path, prompt2_path]:
            if not os.path.exists(file_path):
                print(f"Error: File not found: {file_path}")
                sys.exit(1)
        
        # Read file sizes (simulate processing)
        logs_size = os.path.getsize(logs_path)
        prompt1_size = os.path.getsize(prompt1_path)
        prompt2_size = os.path.getsize(prompt2_path)
        
        print(f"Processing logs file ({logs_size} bytes)...")
        print(f"Processing prompt 1 file ({prompt1_size} bytes)...")
        print(f"Processing prompt 2 file ({prompt2_size} bytes)...")
        
        # Simulate analysis
        print("Analyzing Task Scheduler events...")
        print("Extracting scheduled tasks...")
        print("Identifying suspicious activities...")
        
        # Create output directory
        output_dir = os.path.join("streamlit", "output")
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate report
        report_path = os.path.join(output_dir, "task_scheduler_report.md")
        
        with open(report_path, "w") as f:
            f.write(f"# Task Scheduler Analysis Report\n\n")
            f.write(f"**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"## Input Parameters\n")
            f.write(f"- Logs file: {os.path.basename(logs_path)} ({logs_size} bytes)\n")
            f.write(f"- Prompt 1 file: {os.path.basename(prompt1_path)} ({prompt1_size} bytes)\n")
            f.write(f"- Prompt 2 file: {os.path.basename(prompt2_path)} ({prompt2_size} bytes)\n")
            f.write(f"- TS Parameter 1: {ts_param_1}\n\n")
            f.write(f"## Analysis Results\n")
            f.write(f"- Total events processed: 150\n")
            f.write(f"- Scheduled tasks found: 12\n")
            f.write(f"- Suspicious activities detected: 3\n")
            f.write(f"- High-priority alerts: 1\n\n")
            f.write(f"## Summary\n")
            f.write(f"Task Scheduler analysis completed successfully. ")
            f.write(f"Found {ts_param_1} related events. ")
            f.write(f"Please review the identified suspicious activities for potential security concerns.\n")
        
        print(f"Report generated: {report_path}")
        print("Task Scheduler analysis completed successfully!")
        
    except Exception as e:
        print(f"Error during analysis: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()