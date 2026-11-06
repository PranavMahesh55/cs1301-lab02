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


# PART 2: Graphs read the actual responses saved by Survey.py.
import pandas as pd

st.divider()
st.header("Part 2: Collected Study Hours")
st.caption("Source: data.csv. Each response describes one course on one study day.")
csv_path = Path(__file__).resolve().parent.parent / "data.csv"

if not csv_path.exists() or csv_path.stat().st_size == 0:
    st.info("Submit study hours on the Survey page to display the CSV graphs.")
    st.stop()

survey_data = pd.read_csv(csv_path)
if survey_data.empty:
    st.info("No survey responses yet. Add responses on Survey, then return here.")
    st.stop()

# Ignore invalid rows if the CSV was edited by hand outside the survey.
survey_data["Value"] = pd.to_numeric(survey_data["Value"], errors="coerce")
valid_rows = (survey_data["Category"].notna()
              & survey_data["Category"].astype(str).str.strip().ne("")
              & survey_data["Value"].between(0, 24))
if not valid_rows.all():
    st.warning("Some CSV rows have missing courses or invalid hours and were skipped.")
survey_data = survey_data.loc[valid_rows].copy()
if survey_data.empty:
    st.info("Add valid survey responses with a course and 0–24 study hours.")
    st.stop()

# Static CSV bar chart: uses all valid responses, independent of the filters below.
st.subheader("3. Total Reported Study Hours by Course")
total_hours = survey_data.groupby("Category")["Value"].sum().sort_index()
bar_fig, bar_ax = plt.subplots(figsize=(8, 4))
bar_ax.bar(total_hours.index, total_hours.values)
bar_ax.set_title("Total Study Hours from All Survey Responses")
bar_ax.set_xlabel("Course")
bar_ax.set_ylabel("Total Reported Study Hours")
bar_ax.tick_params(axis="x", labelrotation=30)
bar_fig.tight_layout()
st.pyplot(bar_fig)
plt.close(bar_fig)
st.caption("Totals include every response; courses with more responses may have higher totals.")

st.divider()
# Dynamic CSV histogram: course selection changes the underlying displayed subset.
st.subheader("4. Distribution of Reported Daily Study Hours")
csv_courses = sorted(survey_data["Category"].unique().tolist())
if "csv_selected_courses" not in st.session_state:
    st.session_state["csv_selected_courses"] = csv_courses.copy()
else:
    st.session_state["csv_selected_courses"] = [
        course for course in st.session_state["csv_selected_courses"]
        if course in csv_courses
    ]
if "csv_previous_stats" not in st.session_state:
    st.session_state["csv_previous_stats"] = None

st.multiselect("Survey courses to include", csv_courses, key="csv_selected_courses")
st.slider("Number of histogram bins", min_value=3, max_value=12, value=6,
          key="csv_histogram_bins")
filtered_data = survey_data[
    survey_data["Category"].isin(st.session_state["csv_selected_courses"])
]

if filtered_data.empty:
    st.info("Select at least one course to display the histogram and statistics.")
else:
    hours = filtered_data["Value"].tolist()
    histogram_fig, histogram_ax = plt.subplots(figsize=(8, 4))
    histogram_ax.hist(hours, bins=st.session_state["csv_histogram_bins"],
                      edgecolor="white")
    histogram_ax.set_title("Daily Study Hours for Selected Survey Courses")
    histogram_ax.set_xlabel("Study Hours per Response")
    histogram_ax.set_ylabel("Number of Responses")
    histogram_ax.yaxis.get_major_locator().set_params(integer=True)
    histogram_fig.tight_layout()
    st.pyplot(histogram_fig)
    plt.close(histogram_fig)

    # Extra credit: mean/median update for the same rows shown in the histogram.
    csv_mean = statistics.mean(hours)
    csv_median = statistics.median(hours)
    previous = st.session_state["csv_previous_stats"]
    mean_change = None
    median_change = None
    if previous is not None:
        mean_change = f"{csv_mean - previous[0]:+.2f} hours"
        median_change = f"{csv_median - previous[1]:+.2f} hours"

    mean_col, median_col = st.columns(2)
    with mean_col:
        st.metric("Mean Hours per Response", f"{csv_mean:.2f} hours",
                  delta=mean_change, delta_color="off")
    with median_col:
        st.metric("Median Hours per Response", f"{csv_median:.2f} hours",
                  delta=median_change, delta_color="off")
    st.caption(f"{len(hours)} responses shown. Changes compare with the previous "
               "displayed histogram. Changing bins alone does not change the mean or median.")
    st.session_state["csv_previous_stats"] = [csv_mean, csv_median]
