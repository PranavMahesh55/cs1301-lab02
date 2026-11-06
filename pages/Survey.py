# Collect one course's study hours for one day and append the response to CSV.
import csv
import math
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Study Survey", page_icon="📝")
st.title("Study Hours Survey 📝")
st.write("Enter a course and the hours you studied for it in one day. "
         "Submit a separate response for each course or study day.")

# An absolute path keeps the data inside Lab02 regardless of the launch folder.
data_path = Path(__file__).resolve().parent.parent / "data.csv"

with st.form("survey_form", clear_on_submit=True):
    category_input = st.text_input("Course (for example, CS 1301)")
    value_input = st.text_input("Hours studied in one day (for example, 1.5)")
    submitted = st.form_submit_button("Submit Data")

if submitted:
    course = " ".join(category_input.strip().upper().split())
    try:
        hours = float(value_input.strip())
    except ValueError:
        hours = None

    if not course:
        st.error("Please enter a course name.")
    elif hours is None or not math.isfinite(hours) or not 0 <= hours <= 24:
        st.error("Enter a number of hours from 0 to 24, such as 1.5.")
    else:
        try:
            needs_header = not data_path.exists() or data_path.stat().st_size == 0
            # csv.writer safely handles course names containing commas or quotes.
            with data_path.open("a", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                if needs_header:
                    writer.writerow(["Category", "Value"])
                writer.writerow([course, hours])
        except OSError:
            st.error("The response could not be saved. Please check file permissions.")
        else:
            st.success(f"Saved {hours:g} study hours for {course}.")

st.divider()
st.header("Current Survey Responses")
if data_path.exists() and data_path.stat().st_size > 0:
    current_data = pd.read_csv(data_path)
    if current_data.empty:
        st.info("No responses yet. Submit the form to start collecting data.")
    else:
        st.dataframe(current_data, hide_index=True)
        st.caption(f"{len(current_data)} responses saved. Open Visuals to see the graphs.")
else:
    st.info("No responses yet. Submit the form to start collecting data.")
