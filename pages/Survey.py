import csv
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Survey", page_icon="📝")
st.title("Study Hours Survey 📝")
st.write("Enter a course and the hours you studied for it in one day.")

data_path = Path(__file__).resolve().parent.parent / "data.csv"

with st.form("survey_form"):
    course_input = st.text_input("Course (for example, CS 1301)")
    hours_input = st.text_input("Hours studied (for example, 1.5)")
    submitted = st.form_submit_button("Submit Data")

if submitted:
    course = course_input.strip().upper()
    try:
        hours = float(hours_input)
        if course == "":
            st.error("Please enter a course.")
        elif not 0 <= hours <= 24:
            st.error("Hours must be between 0 and 24.")
        else:
            # Append the new response without replacing the old responses.
            with open(data_path, "a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow([course, hours])
            st.success("Your data has been submitted!")
    except ValueError:
        st.error("Please enter a number for hours.")

st.divider()
st.header("Current Survey Responses")
current_data = pd.read_csv(data_path)
st.dataframe(current_data, hide_index=True)
