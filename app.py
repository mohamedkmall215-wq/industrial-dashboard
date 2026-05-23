# =========================================================
# IMPORTS
# =========================================================
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import requests
from streamlit_lottie import st_lottie

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Industrial Engineering Dashboard",
    layout="wide",
    page_icon="🏭"
)

# =========================================================
# CUSTOM CSS
# =========================================================
st.markdown("""
<style>

html, body, [class*="css"] {
    background-color: #020617;
    color: white;
    font-family: 'Segoe UI';
}

.main {
    background-color: #020617;
}

h1, h2, h3, h4 {
    color: #38bdf8;
}

section[data-testid="stSidebar"] {
    background-color: #0f172a;
}

[data-testid="stMetric"] {
    background-color: #111827;
    border: 1px solid #1e293b;
    padding: 20px;
    border-radius: 18px;
    text-align: center;
    box-shadow: 0px 0px 15px rgba(0,255,255,0.1);
}

div.stButton > button {
    background: linear-gradient(90deg,#0ea5e9,#2563eb);
    color: white;
    border-radius: 12px;
    height: 50px;
    width: 100%;
    border: none;
    font-size: 18px;
    font-weight: bold;
}

div.stButton > button:hover {
    background: linear-gradient(90deg,#0284c7,#1d4ed8);
}

.stDataFrame {
    border-radius: 20px;
    overflow: hidden;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# LOTTIE
# =========================================================
def load_lottie(url):

    r = requests.get(url)

    if r.status_code != 200:
        return None

    return r.json()

lottie_ai = load_lottie(
    "https://assets2.lottiefiles.com/packages/lf20_x62chJ.json"
)

# =========================================================
# HEADER
# =========================================================
col1, col2 = st.columns([3,1])

with col1:

    st.title("🏭 Industrial Engineering Smart Dashboard")

    st.markdown("""
    ### AI Powered Production Planning & LOB Analysis System
    """)

with col2:

    if lottie_ai:
        st_lottie(lottie_ai, height=180)

st.markdown("---")

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.title("⚙️ Project Inputs")

total_units = st.sidebar.number_input(
    "Total Units",
    min_value=1,
    value=30
)

target_delivery_rate = st.sidebar.number_input(
    "Target Rate (Unit/Week)",
    min_value=1.0,
    value=8.0,
    step=0.5
)

working_hours_per_week = st.sidebar.number_input(
    "Working Hours / Week",
    min_value=1,
    value=40
)

st.sidebar.success("AI System Active")

# =========================================================
# INPUT DATA
# =========================================================
st.subheader("🛠️ Activities Data")

data = {
    "Activity": [
        "Activity A",
        "Activity B",
        "Activity C",
        "Activity D"
    ],

    "Man-Hours per Unit": [
        10.0,
        15.0,
        8.0,
        12.0
    ],

    "Actual Crew Size": [
        2,
        3,
        2,
        2
    ]
}

df_input = pd.DataFrame(data)

edited_df = st.data_editor(
    df_input,
    num_rows="dynamic",
    use_container_width=True
)

# =========================================================
# CURRENT RESULTS
# =========================================================
current_results = []

for index, row in edited_df.iterrows():

    activity = row["Activity"]

    man_hours = row["Man-Hours per Unit"]

    actual_crew = row["Actual Crew Size"]

    actual_rate = (
        actual_crew * working_hours_per_week
    ) / man_hours

    productivity = (
        actual_rate / target_delivery_rate
    )

    delay_risk = max(
        0,
        (
            target_delivery_rate - actual_rate
        ) / target_delivery_rate * 100
    )

    efficiency = min(
        100,
        (
            actual_rate / target_delivery_rate
        ) * 100
    )

    if actual_rate < target_delivery_rate:

        status = "Bottleneck ⚠️"

    elif actual_rate > target_delivery_rate:

        status = "Surplus 🟢"

    else:

        status = "Balanced ✅"

    current_results.append({

        "Activity":
        activity,

        "Actual Crew":
        actual_crew,

        "Actual Rate":
        round(actual_rate,2),

        "Efficiency %":
        round(efficiency,2),

        "Delay Risk %":
        round(delay_risk,2),

        "Productivity Index":
        round(productivity,2),

        "Status":
        status
    })

# =========================================================
# DATAFRAME
# =========================================================
df_current = pd.DataFrame(current_results)

# =========================================================
# KPI CARDS
# =========================================================
st.subheader("📊 Industrial KPIs")

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Target Rate",
        f"{target_delivery_rate} U/W"
    )

with col2:

    bottlenecks = len(
        df_current[
            df_current["Status"]
            .str.contains("Bottleneck")
        ]
    )

    st.metric(
        "Bottlenecks",
        bottlenecks
    )

with col3:

    avg_eff = round(
        df_current["Efficiency %"]
        .mean(),
        2
    )

    st.metric(
        "Average Efficiency",
        f"{avg_eff}%"
    )

with col4:

    avg_rate = round(
        df_current["Actual Rate"]
        .mean(),
        2
    )

    st.metric(
        "Average Production",
        avg_rate
    )

st.markdown("---")

# =========================================================
# CURRENT TABLE
# =========================================================
st.subheader("📋 Current Engineering Calculations")

st.dataframe(
    df_current,
    use_container_width=True
)

# =========================================================
# BAR CHART
# =========================================================
st.subheader("📈 Production Rate Analysis")

fig_bar = px.bar(
    df_current,
    x="Activity",
    y="Actual Rate",
    color="Status",
    text="Actual Rate",
    template="plotly_dark"
)

fig_bar.update_layout(
    height=500
)

st.plotly_chart(
    fig_bar,
    use_container_width=True
)

# =========================================================
# DYNAMIC LOB CHART
# =========================================================
st.subheader("📉 Dynamic Line of Balance (LOB) Chart")

time_data = list(range(1, len(df_current) + 1))

actual_volume = df_current["Actual Rate"].tolist()

lob_line = [

    target_delivery_rate

    for _ in range(len(time_data))
]

fig_lob = go.Figure()

# =========================================================
# LINE OF BALANCE
# =========================================================
fig_lob.add_trace(

    go.Scatter(

        x=time_data,

        y=lob_line,

        mode='lines',

        line=dict(

            color='white',

            width=5,

            dash='dash'
        ),

        name='Line of Balance'
    )
)

# =========================================================
# ACTUAL PRODUCTION
# =========================================================
fig_lob.add_trace(

    go.Scatter(

        x=time_data,

        y=actual_volume,

        mode='lines+markers',

        line=dict(

            color='#00FFAA',

            width=6,

            shape='spline'
        ),

        marker=dict(

            size=14,

            color='#00FFAA'
        ),

        name='Actual Production'
    )
)


# =========================================================
# GANTT CHART
# =========================================================
st.subheader("📅 Gantt Chart with Line of Balance")

gantt_data = []

start_date = datetime.today()

for i, row in df_current.iterrows():

    duration = total_units / row["Actual Rate"]

    finish_date = start_date + timedelta(
        weeks=duration
    )

    if row["Actual Rate"] >= target_delivery_rate:

        progress_status = "Ahead"

    else:

        progress_status = "Behind"

    gantt_data.append(dict(

        Task=row["Activity"],

        Start=start_date,

        Finish=finish_date,

        Status=progress_status
    ))

gantt_df = pd.DataFrame(gantt_data)

fig_gantt = px.timeline(
    gantt_df,
    x_start="Start",
    x_end="Finish",
    y="Task",
    color="Status",

    color_discrete_map={

        "Ahead": "#00FFAA",

        "Behind": "#FF4B4B"
    },

    template="plotly_dark"
)

fig_gantt.update_yaxes(
    autorange="reversed"
)

lob_date = start_date + timedelta(
    weeks=(total_units / target_delivery_rate)
)

fig_gantt.add_vline(
    x=lob_date,
    line_width=4,
    line_dash="dash",
    line_color="white"
)

fig_gantt.update_layout(
    title="Gantt Chart with Line of Balance",
    height=700
)

st.plotly_chart(
    fig_gantt,
    use_container_width=True
)

# =========================================================
# AI REPORT
# =========================================================
st.markdown("---")

st.subheader("🤖 AI Engineering Consultant")

optimization_method = st.radio(

    "Choose Optimization Method",

    [

        "Increase Crew Size 👷",

        "Increase Working Hours ⏰"
    ],

    horizontal=True
)

if st.button("🚀 Generate Professional AI Report"):

    report_data = []

    for index, row in edited_df.iterrows():

        activity = row["Activity"]

        man_hours = row["Man-Hours per Unit"]

        actual_crew = row["Actual Crew Size"]

        # =====================================================
        # CURRENT RATE
        # =====================================================
        current_rate = (
            actual_crew *
            working_hours_per_week
        ) / man_hours

        current_efficiency = round(
            (
                current_rate /
                target_delivery_rate
            ) * 100,
            2
        )

        # =====================================================
        # DETECT CONDITIONS
        # =====================================================
        is_bottleneck = (
            current_rate < target_delivery_rate
        )

        is_surplus = (
            current_rate > target_delivery_rate
        )

        # =====================================================
        # DEFAULT VALUES
        # =====================================================
        recommended_crew = actual_crew

        crew_efficiency = current_efficiency

        hours_efficiency = current_efficiency

        recommendation = (
            "Maintain current workflow efficiency."
        )

        status = "🟢 Balanced"

        # =====================================================
        # ONLY FIX BOTTLENECK
        # =====================================================
        if is_bottleneck:

            status = "🔴 Bottleneck"

            # =================================================
            # CREW SIZE
            # =================================================
            if optimization_method == "Increase Crew Size 👷":

                recommended_crew = int(

                    (
                        target_delivery_rate *
                        man_hours
                    ) / working_hours_per_week

                ) + 1

                improved_rate_crew = round(

                    (
                        recommended_crew *
                        working_hours_per_week
                    ) / man_hours,

                    2
                )

                crew_efficiency = round(

                    (
                        improved_rate_crew /
                        target_delivery_rate
                    ) * 100,

                    2
                )

                recommendation = (

                    f"Increase crew size "
                    f"from {actual_crew} "
                    f"to {recommended_crew} "
                    f"to eliminate bottleneck."
                )

            # =================================================
            # WORKING HOURS
            # =================================================
            else:

                increased_hours = int(

                    (
                        target_delivery_rate *
                        man_hours
                    ) / actual_crew

                ) + 1

                improved_rate_hours = round(

                    (
                        actual_crew *
                        increased_hours
                    ) / man_hours,

                    2
                )

                hours_efficiency = round(

                    (
                        improved_rate_hours /
                        target_delivery_rate
                    ) * 100,

                    2
                )

                recommendation = (

                    f"Increase working hours "
                    f"from {working_hours_per_week} "
                    f"to {increased_hours} "
                    f"to eliminate bottleneck."
                )

        # =====================================================
        # SURPLUS CASE
        # =====================================================
        elif is_surplus:

            status = "🟢 Surplus"

            surplus_value = round(
                current_rate - target_delivery_rate,
                2
            )

            recommendation = (

                f"Production surplus detected "
                f"({surplus_value} U/W).\n"

                f"Recommended Actions:\n"

                f"• Transfer extra workers.\n"
                f"• Reduce overtime.\n"
                f"• Build inventory buffer.\n"
                f"• Use extra capacity for future demand."
            )

        # =====================================================
        # REPORT
        # =====================================================
        report_data.append({

            "Activity":
            activity,

            "Current Rate":
            f"{round(current_rate,2)} U/W",

            "Current Efficiency":
            f"{current_efficiency}%",

            "Status":
            status,

            "Recommended Crew":
            recommended_crew,

            "Crew Optimization":
            f"{crew_efficiency}%",

            "Hours Optimization":
            f"{hours_efficiency}%",

            "Recommendation":
            recommendation
        })

    report_df = pd.DataFrame(report_data)

    st.markdown(
        "## 🏭 Executive Industrial Engineering Report"
    )

    st.dataframe(
        report_df,
        use_container_width=True
    )

# =========================================================
# FOOTER
# =========================================================
st.markdown("---")

st.markdown("""

<center>

<h3>
🏭 Industrial Engineering Smart System
</h3>

AI-Powered Production Planning Platform

</center>

""", unsafe_allow_html=True)