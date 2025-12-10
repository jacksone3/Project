# fema_app.py

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# =========================================================
# CONFIGURATION
# =========================================================

# Change this if your CSV has a different name
DATA_FILE = "fema_small.csv"

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

# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    """Read the FEMA CSV file."""
    df = pd.read_csv(path)

    # Make sure repairAmount is numeric
    if "repairAmount" in df.columns:
        df["repairAmount"] = pd.to_numeric(df["repairAmount"], errors="coerce")

    return df


# Check that the file exists in the repo
if not Path(DATA_FILE).exists():
    st.error(
        f"❌ Could not find `{DATA_FILE}`.\n\n"
        "Make sure the CSV file is in the **same GitHub folder** as `fema_app.py` "
        "and that the name here matches exactly (including .csv)."
    )
    st.stop()

# Load the data
df = load_data(DATA_FILE)

# Basic column checks
required_cols = {"repairAmount", "tsaEligible"}
missing = required_cols - set(df.columns)
if missing:
    st.error(
        f"❌ Your dataset is missing required columns: {', '.join(missing)}.\n\n"
        "The app needs at least `repairAmount` and `tsaEligible`."
    )
    st.stop()

# Drop rows with missing repairAmount or tsaEligible
df = df[df["repairAmount"].notna() & df["tsaEligible"].notna()].copy()

# Optional: cap extreme outliers at 99th percentile so plots look nicer
upper_cap = df["repairAmount"].quantile(0.99)
df_plot = df[df["repairAmount"] <= upper_cap].copy()

# =========================================================
# DATA PREVIEW
# =========================================================

st.subheader("Data Preview")

preview_cols = ["repairAmount", "tsaEligible"]
extra_cols = [c for c in ["grossIncome", "residenceType", "damagedStateAbbreviation"] if c in df.columns]
preview_cols += extra_cols

st.dataframe(df[preview_cols].head(50))

st.markdown(
    """
    The preview shows the key variables used in the analysis:
    - **repairAmount** – FEMA housing repair award (in dollars)  
    - **tsaEligible** – Transitional Sheltering Assistance eligibility (1 = Yes, 0 = No)  
    """
)

# =========================================================
# HISTOGRAM OF REPAIR AMOUNT
# =========================================================

st.subheader("Histogram of Repair Amount")

# Slider to control max amount shown
max_amount = st.slider(
    "Maximum repair amount to include in the histogram",
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
fig_hist.update_layout(
    xaxis_title="Repair Amount ($)",
    yaxis_title="Number of Households"
)

st.plotly_chart(fig_hist, use_container_width=True)

st.markdown(
    """
    **Insight:** The distribution of repair amounts is heavily right-skewed.  
    Most households receive relatively small awards, while a smaller number
    receive much larger repair payments.
    """
)

# =========================================================
# BOXPLOT: REPAIR AMOUNT BY TSA ELIGIBILITY
# =========================================================

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
    repair amounts than non-eligible households (0).  
    This pattern is consistent with TSA being targeted toward survivors with more
    severe housing damage and higher repair needs.
    """
)

st.success("Dashboard loaded successfully. Use this view (plus a screenshot) in your report for Part IV.")
