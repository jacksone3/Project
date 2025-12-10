import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------------------------------------------
# Page setup
# ----------------------------------------------------
st.set_page_config(
    page_title="FEMA Disaster Relief Dashboard",
    layout="wide"
)

st.title("FEMA Disaster Relief Dashboard")
st.write(
    """
    This dashboard explores FEMA Individual Assistance housing data, focusing on
    repair amounts and Transitional Sheltering Assistance (TSA) eligibility.
    """
)

# ----------------------------------------------------
# Load data
# ----------------------------------------------------
@st.cache_data
def load_data():
    # Make sure this filename matches the CSV in your repo
    return pd.read_csv("fema_small.csv")

df = load_data()

st.subheader("Data Preview")
st.dataframe(df[["repairAmount", "tsaEligible", "grossIncome",
                 "residenceType", "damagedStateAbbreviation"]].head(50))

# Optional: filter out extreme outliers so plots look nicer
df_plot = df[df["repairAmount"].notna()].copy()
upper_cap = df_plot["repairAmount"].quantile(0.99)
df_plot = df_plot[df_plot["repairAmount"] <= upper_cap]

# ----------------------------------------------------
# Histogram of repairAmount
# ----------------------------------------------------
st.subheader("Histogram of Repair Amount")

max_amount = st.slider(
    "Maximum repair amount to include in the plot",
    min_value=int(df_plot["repairAmount"].min()),
    max_value=int(upper_cap),
    value=int(upper_cap),
    step=500
)

df_hist = df_plot[df_plot["repairAmount"] <= max_amount]

fig_hist = px.histogram(
    df_hist,
    x="repairAmount",
    nbins=30,
    title="Distribution of Repair Amounts",
    labels={"repairAmount": "Repair Amount ($)"}
)
fig_hist.update_layout(xaxis_title="Repair Amount ($)", yaxis_title="Number of Households")
st.plotly_chart(fig_hist, use_container_width=True)

st.markdown(
    """
    **Insight:** The repair amounts are right-skewed – most households receive
    relatively small awards, while a smaller number of households receive very
    large repair payments.
    """
)

# ----------------------------------------------------
# Boxplot of repairAmount by tsaEligible
# ----------------------------------------------------
st.subheader("Boxplot: Repair Amount by TSA Eligibility")

fig_box = px.box(
    df_plot,
    x="tsaEligible",
    y="repairAmount",
    color="tsaEligible",
    title="Repair Amount by TSA Eligibility",
    labels={
        "tsaEligible": "TSA Eligible (1 = Yes, 0 = No)",
        "repairAmount": "Repair Amount ($)"
    }
)
fig_box.update_xaxes(
    tickmode="array",
    tickvals=[0, 1],
    ticktext=["0 = Not Eligible", "1 = Eligible"]
)
st.plotly_chart(fig_box, use_container_width=True)

st.markdown(
    """
    **Insight:** TSA-eligible households (1) tend to have higher and more variable
    repair amounts than non-eligible households (0), which is consistent with TSA
    targeting survivors with more severe housing damage.
    """
)
