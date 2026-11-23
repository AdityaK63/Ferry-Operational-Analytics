import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Ferry Operational Analytics",
    page_icon="⛴️",
    layout="wide"
)

# Load dataset
@st.cache_data
def load_data():
    df = pd.read_csv("Ferry_Analytics_Cleaned_Data.csv")
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])

    df["Total Activity"] = df["Sales Count"] + df["Redemption Count"]
    df["Hour"] = df["Timestamp"].dt.hour
    df["Day"] = df["Timestamp"].dt.day_name()
    df["Month"] = df["Timestamp"].dt.month
    df["Month Name"] = df["Timestamp"].dt.month_name()
    df["Year"] = df["Timestamp"].dt.year
    df["Weekend"] = df["Timestamp"].dt.dayofweek >= 5

    return df

df = load_data()

# Title
st.title("⛴️ Ferry Capacity Utilization & Operational Efficiency Analytics")
st.markdown(
    "### Toronto Island Ferry | Ticket Activity & Operational Insights"
)

st.info(
    "This dashboard analyzes ticket sales and redemptions as operational activity indicators. "
    "Actual vessel capacity utilization cannot be calculated because vessel capacity and "
    "passenger occupancy data are not available in the dataset."
)

# Sidebar filters
st.sidebar.header("Dashboard Filters")

years = sorted(df["Year"].unique())
selected_years = st.sidebar.multiselect(
    "Select Year",
    years,
    default=years
)

months = sorted(df["Month"].unique())
selected_months = st.sidebar.multiselect(
    "Select Month",
    months,
    default=months
)

filtered_df = df[
    (df["Year"].isin(selected_years)) &
    (df["Month"].isin(selected_months))
]

if filtered_df.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

# KPIs
total_sales = filtered_df["Sales Count"].sum()
total_redemptions = filtered_df["Redemption Count"].sum()
avg_activity = filtered_df["Total Activity"].mean()
total_records = len(filtered_df)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Sales", f"{total_sales:,.0f}")
col2.metric("Total Redemptions", f"{total_redemptions:,.0f}")
col3.metric("Avg Total Activity", f"{avg_activity:,.2f}")
col4.metric("Total Records", f"{total_records:,}")

st.divider()

# Hourly Analysis
st.subheader("🕒 Hourly Operational Activity")

hourly = (
    filtered_df.groupby("Hour")["Total Activity"]
    .mean()
    .reset_index()
)

fig_hour = px.line(
    hourly,
    x="Hour",
    y="Total Activity",
    markers=True,
    title="Average Total Activity by Hour"
)

fig_hour.update_layout(
    xaxis_title="Hour of Day",
    yaxis_title="Average Total Activity"
)

st.plotly_chart(fig_hour, use_container_width=True)

# Daily Analysis
st.subheader("📅 Daily Activity")

day_order = [
    "Monday", "Tuesday", "Wednesday",
    "Thursday", "Friday", "Saturday", "Sunday"
]

daily = (
    filtered_df.groupby("Day")["Total Activity"]
    .mean()
    .reindex(day_order)
    .reset_index()
)

fig_day = px.bar(
    daily,
    x="Day",
    y="Total Activity",
    title="Average Total Activity by Day"
)

st.plotly_chart(fig_day, use_container_width=True)

# Monthly Analysis
st.subheader("📈 Monthly Sales and Redemption Trends")

monthly = (
    filtered_df.groupby("Month")
    .agg({
        "Sales Count": "sum",
        "Redemption Count": "sum"
    })
    .reset_index()
)

fig_month = px.bar(
    monthly,
    x="Month",
    y=["Sales Count", "Redemption Count"],
    barmode="group",
    title="Monthly Sales vs Redemptions"
)

st.plotly_chart(fig_month, use_container_width=True)

# Weekend vs Weekday
st.subheader("🌆 Weekend vs Weekday")

filtered_df["Day Type"] = filtered_df["Weekend"].map({
    True: "Weekend",
    False: "Weekday"
})

week_comparison = (
    filtered_df.groupby("Day Type")["Total Activity"]
    .mean()
    .reset_index()
)

fig_week = px.bar(
    week_comparison,
    x="Day Type",
    y="Total Activity",
    color="Day Type",
    title="Average Activity: Weekend vs Weekday"
)

st.plotly_chart(fig_week, use_container_width=True)

# Sales vs Redemption
st.subheader("🎟️ Sales vs Redemptions")

fig_sr = px.scatter(
    filtered_df,
    x="Sales Count",
    y="Redemption Count",
    title="Relationship Between Sales and Redemptions"
)

st.plotly_chart(fig_sr, use_container_width=True)

# Activity classification
st.subheader("📊 Activity Level Distribution")

q1 = filtered_df["Total Activity"].quantile(0.25)
q3 = filtered_df["Total Activity"].quantile(0.75)

filtered_df["Activity Level"] = pd.cut(
    filtered_df["Total Activity"],
    bins=[-float("inf"), q1, q3, float("inf")],
    labels=["Low", "Moderate", "High"]
)

activity_counts = (
    filtered_df["Activity Level"]
    .value_counts()
    .reindex(["Low", "Moderate", "High"])
    .reset_index()
)

activity_counts.columns = ["Activity Level", "Count"]

fig_activity = px.pie(
    activity_counts,
    names="Activity Level",
    values="Count",
    title="Activity Level Distribution",
    hole=0.45
)

st.plotly_chart(fig_activity, use_container_width=True)

# Peak activity records
st.subheader("🔥 Peak Activity Intervals")

peak_intervals = filtered_df.sort_values(
    "Total Activity",
    ascending=False
).head(10)

st.dataframe(
    peak_intervals[
        ["Timestamp", "Sales Count", "Redemption Count", "Total Activity"]
    ],
    use_container_width=True
)

# Raw data
with st.expander("View Dataset"):
    st.dataframe(filtered_df, use_container_width=True)

# Footer
st.divider()

st.caption(
    "Ferry Operational Analytics | Python, Pandas, Streamlit & Plotly"
)

st.caption(
    "Note: Ticket activity is used as a proxy for operational demand. "
    "Actual passenger occupancy and vessel capacity utilization are not measured."
)
