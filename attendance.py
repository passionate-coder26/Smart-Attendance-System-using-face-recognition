import pandas as pd
from datetime import datetime
import os

# Load or create the attendance DataFrame
attendance_file = "Attendance.csv"
if os.path.exists(attendance_file):
    attendance_df = pd.read_csv(attendance_file)
else:
    attendance_df = pd.DataFrame(columns=["Name", "Time"])

def mark_attendance(name):
    global attendance_df
    if name not in attendance_df['Name'].values:
        now = datetime.now()
        dtString = now.strftime('%Y-%m-%d %H:%M:%S')
        new_entry = pd.DataFrame({"Name": [name], "Time": [dtString]})
        attendance_df = pd.concat([attendance_df, new_entry], ignore_index=True)
    else:
        print(f"{name} is already marked as present today.")

def update_attendance():
    attendance_df.to_csv(attendance_file, index=False)