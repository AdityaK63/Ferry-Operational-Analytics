import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------
# PAGE CONFIGURATION
# -----------------------------
st.set_page_config(
    page_title="Ferry Operational Analytics",
    page_icon="⛴️",
    layout="wide"
)

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("Ferry_Analytics_Cleaned_Data.csv")
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])

    df["Total Activity"] = (
        df["Sales Count"] + df["Redemption Count"]
    )

    df["Hour"] = df["Timestamp"].dt.hour
    df["Day"] = df["Timestamp"].dt.day_name()
    df["Month"] = df["Timestamp"].dt.month
    df["Month Name"] = df["Timestamp"].dt.month_name()
    df["Year"] = df["Timestamp"].dt.year
    df["Weekend"] = df["Timestamp"].dt.dayofweek >= 5

    return df

df = load_data()

# -----------------------------
# TITLE
# -----------------------------
st.title("⛴️ Ferry Operational Analytics")
st.subheader("Toronto Island Ferry Ticket Activity Analysis")

st.markdown("""
Explore ticket sales, redemption activity, temporal patterns and
operational activity indicators through this interactive dashboard.
""")

st.divider()

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------
st.sidebar.header("Dashboard Filters")

years = sorted(df["Year"].unique())

selected_years = st.sidebar.multiselect(
    "Select Year",
    years,
    default=years
)

df_filtered = df[df["Year"].isin(selected_years)]

months = sorted(df_filtered["Month"].unique())

selected_months = st.sidebar.multiselect(
    "Select Month",
    months,
    default=months
)

df_filtered = df_filtered[
    df_filtered["Month"].isin(selected_months)
]

days = sorted(df_filtered["Day"].unique())

selected_days = st.sidebar.multiselect(
    "Select Day",
    days,
    default=days
)

df_filtered = df_filtered[
    df_filtered["Day"].isin(selected_days)
]

if df_filtered.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

# -----------------------------
# KPI METRICS
# -----------------------------
total_sales = df_filtered["Sales Count"].sum()
total_redemptions = df_filtered["Redemption Count"].sum()
average_activity = df_filtered["Total Activity"].mean()
max_activity = df_filtered["Total Activity"].max()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Sales", f"{total_sales:,.0f}")
col2.metric("Total Redemptions", f"{total_redemptions:,.0f}")
col3.metric("Average Total Activity", f"{average_activity:,.2f}")
col4.metric("Maximum Recorded Activity", f"{max_activity:,.0f}")

st.divider()

# -----------------------------
# HOURLY ACTIVITY
# -----------------------------
st.header("Hourly Activity Analysis")

hourly = df_filtered.groupby("Hour")["Total Activity"].mean().reset_index()

fig_hourly = px.line(
    hourly,
    x="Hour",
    y="Total Activity",
    markers=True,
    title="Average Total Activity by Hour"
)

st.plotly_chart(fig_hourly, use_container_width=True)

# -----------------------------
# DAILY ACTIVITY
# -----------------------------
st.header("Daily Activity Analysis")

day_order = [
    "Monday", "Tuesday", "Wednesday",
    "Thursday", "Friday", "Saturday", "Sunday"
]

daily = df_filtered.groupby("Day")["Total Activity"].mean().reset_index()

daily["Day"] = pd.Categorical(
    daily["Day"],
    categories=day_order,
    ordered=True
)

daily = daily.sort_values("Day")

fig_daily = px.bar(
    daily,
    x="Day",
    y="Total Activity",
    title="Average Total Activity by Day"
)

st.plotly_chart(fig_daily, use_container_width=True)

# -----------------------------
# MONTHLY ACTIVITY
# -----------------------------
st.header("Monthly Activity Analysis")

monthly = df_filtered.groupby("Month").agg(
    Sales=("Sales Count", "mean"),
    Redemptions=("Redemption Count", "mean")
).reset_index()

fig_monthly = px.bar(
    monthly,
    x="Month",
    y=["Sales", "Redemptions"],
    barmode="group",
    title="Average Monthly Sales and Redemptions"
)

st.plotly_chart(fig_monthly, use_container_width=True)

# -----------------------------
# WEEKDAY VS WEEKEND
# -----------------------------
st.header("Weekday vs Weekend Analysis")

df_filtered["Day Type"] = df_filtered["Weekend"].map({
    True: "Weekend",
    False: "Weekday"
})

weekend = df_filtered.groupby("Day Type")[
    "Total Activity"
].mean().reset_index()

fig_weekend = px.bar(
    weekend,
    x="Day Type",
    y="Total Activity",
    title="Average Activity: Weekday vs Weekend"
)

st.plotly_chart(fig_weekend, use_container_width=True)

# -----------------------------
# ACTIVITY LEVEL CLASSIFICATION
# -----------------------------
st.header("Activity Level Distribution")

q25 = df_filtered["Total Activity"].quantile(0.25)
q75 = df_filtered["Total Activity"].quantile(0.75)

df_filtered["Activity Level"] = pd.cut(
    df_filtered["Total Activity"],
    bins=[-float("inf"), q25, q75, float("inf")],
    labels=["Low", "Moderate", "High"],
    include_lowest=True
)

activity_distribution = df_filtered["Activity Level"].value_counts().reset_index()
activity_distribution.columns = ["Activity Level", "Count"]

fig_activity = px.pie(
    activity_distribution,
    names="Activity Level",
    values="Count",
    hole=0.4,
    title="Distribution of Activity Levels"
)

st.plotly_chart(fig_activity, use_container_width=True)

# -----------------------------
# SALES VS REDEMPTIONS
# -----------------------------
st.header("Sales vs Redemptions")

sales_redemptions = pd.DataFrame({
    "Category": ["Sales", "Redemptions"],
    "Count": [
        df_filtered["Sales Count"].sum(),
        df_filtered["Redemption Count"].sum()
    ]
})

fig_sr = px.bar(
    sales_redemptions,
    x="Category",
    y="Count",
    title="Total Sales vs Total Redemptions"
)

st.plotly_chart(fig_sr, use_container_width=True)

# -----------------------------
# PEAK ACTIVITY RECORDS
# -----------------------------
st.header("Top 10 Activity Intervals")

peak = df_filtered.nlargest(10, "Total Activity")

st.dataframe(
    peak[[
        "Timestamp",
        "Sales Count",
        "Redemption Count",
        "Total Activity"
    ]],
    use_container_width=True
)

# -----------------------------
# DATA TABLE
# -----------------------------
with st.expander("View Dataset"):
    st.dataframe(df_filtered, use_container_width=True)

# -----------------------------
# DISCLAIMER
# -----------------------------
st.divider()

st.caption("""
This dashboard analyzes recorded ticket sales and redemption activity.
The dataset does not contain ferry vessel capacity or passenger counts
per departure. Therefore, the analysis does not directly measure actual
ferry capacity utilization.
"")

st.markdown("### Developed using Python, Pandas and Streamlit")
