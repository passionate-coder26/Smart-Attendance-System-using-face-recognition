import pandas as pd
import os
from datetime import datetime, timedelta
from custom_logging import log_info, log_error

ATTENDANCE_FILE = "attendance.xlsx"

def mark_attendance(name):
    current_time = datetime.now()
    current_date = current_time.date()  # Get only the date part

    # Check if attendance file exists
    if os.path.exists(ATTENDANCE_FILE):
        df = pd.read_excel(ATTENDANCE_FILE)
    else:
        df = pd.DataFrame(columns=["Name", "Date", "Time"])

    # Ensure the correct data types for comparison
    if not df.empty:
        df["Date"] = pd.to_datetime(df["Date"], format="%Y-%m-%d").dt.date  # Convert to date format
        df["Time"] = pd.to_datetime(df["Time"], format="%H:%M:%S").dt.time  # Convert to time format

        # Filter records for the same person on the same date
        person_records = df[(df["Name"] == name) & (df["Date"] == current_date)]

        if not person_records.empty:
            last_time = max(person_records["Time"])
            last_time = datetime.combine(current_date, last_time)

            # Check if the last marked time is within the last 1 hour
            if (current_time - last_time) < timedelta(hours=1):
                log_info(f"Attendance already marked for {name} within the last hour.")
                print(f"Attendance already marked for {name} within the last hour.")
                return  # **Exit function early, preventing extra logging**

    # If attendance is not marked in the last hour, proceed to mark it
    new_entry = pd.DataFrame({"Name": [name], "Date": [current_date], "Time": [current_time.strftime("%H:%M:%S")]})
    df = pd.concat([df, new_entry], ignore_index=True)

    try:
        df.to_excel(ATTENDANCE_FILE, index=False)
        log_info(f"Attendance marked for {name} at {current_time.strftime('%H:%M:%S')} on {current_date}.")
        print(f"Attendance marked for {name} at {current_time.strftime('%H:%M:%S')} on {current_date}.")
    except Exception as e:
        log_error(f"Error updating attendance file: {str(e)}")
        print(f"Error updating attendance file: {e}")
