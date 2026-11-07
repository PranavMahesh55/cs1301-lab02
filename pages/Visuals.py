import csv
import json
from pathlib import Path
import statistics

import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="Visuals", page_icon="📈")
st.title("Data Visualizations 📈")

# Find data.json even if Streamlit is started from a different folder.
data_path = Path(__file__).resolve().parent.parent / "data.json"
with open(data_path, "r") as file:
    study_data = json.load(file)

st.caption(study_data["description"])
days = study_data["days"]
courses = study_data["courses"]

# PART 1: Static bar chart
st.header("1. Weekly Study Hours by Course")

course_names = []
weekly_hours = []
for course in courses:
    course_names.append(course)
    weekly_hours.append(sum(courses[course]))

fig, ax = plt.subplots(figsize=(8, 4))
ax.bar(course_names, weekly_hours)
ax.set_title(study_data["chart_title"])
ax.set_xlabel("Course")
ax.set_ylabel("Study Hours per Week")
fig.tight_layout()
st.pyplot(fig)
plt.close(fig)

st.divider()

# PART 1: Dynamic line chart
st.header("2. Daily Study Hours")
st.write("Select courses to graph their combined study hours for each day.")

if "selected_courses" not in st.session_state:
    st.session_state["selected_courses"] = course_names.copy()
if "previous_stats" not in st.session_state:
    st.session_state["previous_stats"] = None

st.multiselect("Courses to include", course_names, key="selected_courses")
selected_courses = st.session_state["selected_courses"]

if len(selected_courses) > 0:
    daily_hours = []
    for day_index in range(len(days)):
        total = 0
        for course in selected_courses:
            total += courses[course][day_index]
        daily_hours.append(total)

    line_fig, line_ax = plt.subplots(figsize=(8, 4))
    line_ax.plot(days, daily_hours, marker="o")
    line_ax.set_title("Combined Daily Study Hours for Selected Courses")
    line_ax.set_xlabel("Day")
    line_ax.set_ylabel("Study Hours")
    line_ax.set_ylim(bottom=0)
    line_ax.tick_params(axis="x", labelrotation=30)
    line_fig.tight_layout()
    st.pyplot(line_fig)
    plt.close(line_fig)

    # Extra credit: compare these statistics with the previous chart's statistics.
    mean_hours = statistics.mean(daily_hours)
    median_hours = statistics.median(daily_hours)
    previous_stats = st.session_state["previous_stats"]
    mean_delta = None
    median_delta = None
    if previous_stats is not None:
        mean_delta = f"{mean_hours - previous_stats[0]:+.2f} hours"
        median_delta = f"{median_hours - previous_stats[1]:+.2f} hours"

    mean_column, median_column = st.columns(2)
    with mean_column:
        st.metric("Mean Daily Hours", f"{mean_hours:.2f} hours",
                  delta=mean_delta, delta_color="off")
    with median_column:
        st.metric("Median Daily Hours", f"{median_hours:.2f} hours",
                  delta=median_delta, delta_color="off")

    st.caption("Changes are compared with the previous course selection.")
    st.session_state["previous_stats"] = [mean_hours, median_hours]
else:
    st.info("Select at least one course to display the chart and statistics.")


# PART 2: Read the responses from data.csv.
st.divider()
st.header("Part 2: Study Survey Results")
csv_path = Path(__file__).resolve().parent.parent / "data.csv"
with open(csv_path, "r", newline="") as file:
    survey_rows = list(csv.DictReader(file))

if len(survey_rows) == 0:
    st.info("Enter data on the Survey page to see the CSV graphs.")
    st.stop()

# Static bar chart: add up all the hours for each course.
st.header("3. Total Study Hours by Course")
totals = {}
for row in survey_rows:
    course = row["Category"]
    hours = float(row["Value"])
    if course not in totals:
        totals[course] = 0
    totals[course] += hours

csv_courses = list(totals.keys())
bar_fig, bar_ax = plt.subplots(figsize=(8, 4))
bar_ax.bar(csv_courses, list(totals.values()))
bar_ax.set_title("Total Study Hours from Survey Responses")
bar_ax.set_xlabel("Course")
bar_ax.set_ylabel("Total Study Hours")
bar_ax.tick_params(axis="x", labelrotation=30)
bar_fig.tight_layout()
st.pyplot(bar_fig)
plt.close(bar_fig)

st.divider()
# Dynamic histogram: show all courses or one selected course.
st.header("4. Daily Study Hours from the Survey")
if "csv_course" not in st.session_state:
    st.session_state["csv_course"] = "All courses"
if "csv_previous_stats" not in st.session_state:
    st.session_state["csv_previous_stats"] = None

st.selectbox("Survey course to include", ["All courses"] + csv_courses,
             key="csv_course")
selected_course = st.session_state["csv_course"]
hours = []
for row in survey_rows:
    if selected_course == "All courses" or row["Category"] == selected_course:
        hours.append(float(row["Value"]))

hist_fig, hist_ax = plt.subplots(figsize=(8, 4))
hist_ax.hist(hours, bins=6, edgecolor="white")
hist_ax.set_title("Daily Study Hours: " + selected_course)
hist_ax.set_xlabel("Hours Studied per Response")
hist_ax.set_ylabel("Number of Responses")
hist_fig.tight_layout()
st.pyplot(hist_fig)
plt.close(hist_fig)

# Extra credit: compare mean and median with the previous selection.
mean_hours = statistics.mean(hours)
median_hours = statistics.median(hours)
previous_stats = st.session_state["csv_previous_stats"]
mean_delta = None
median_delta = None
if previous_stats is not None:
    mean_delta = f"{mean_hours - previous_stats[0]:+.2f} hours"
    median_delta = f"{median_hours - previous_stats[1]:+.2f} hours"

st.metric("Mean Hours per Response", f"{mean_hours:.2f} hours",
          delta=mean_delta, delta_color="off")
st.metric("Median Hours per Response", f"{median_hours:.2f} hours",
          delta=median_delta, delta_color="off")
st.caption("Changes are compared with the previous course selection.")
st.session_state["csv_previous_stats"] = [mean_hours, median_hours]
