import streamlit as st
import pandas as pd
from pathlib import Path

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="DPS Pipeline & Liquidity App",
    layout="wide"
)

# ---------------------------------------------------
# FILE LOCATION
# ---------------------------------------------------

DATA_FILE = Path(
    "pipeline_for_streamlit_corrected_mapping_ready.xlsx"
)

# ---------------------------------------------------
# LOAD WORKBOOK
# ---------------------------------------------------

@st.cache_data
def load_workbook(file_path):
    return pd.read_excel(file_path, sheet_name=None)

sheets = load_workbook(DATA_FILE)

# ---------------------------------------------------
# LOAD SHEETS
# ---------------------------------------------------

pipeline = sheets.get("Pipeline_Control", pd.DataFrame())
so_mapping = sheets.get("SO_Mapping", pd.DataFrame())
so_source = sheets.get("SO_Source", pd.DataFrame())
eligibility = sheets.get("Cash_Eligibility", pd.DataFrame())
cash_bridge = sheets.get("Cash_Bridge", pd.DataFrame())

# ---------------------------------------------------
# APP TITLE
# ---------------------------------------------------

st.title("DPS Pipeline & Liquidity Tracking App")

# ---------------------------------------------------
# SIDEBAR NAVIGATION
# ---------------------------------------------------

page = st.sidebar.radio(
    "Select View",
    [
        "Executive Dashboard",
        "Pipeline Control",
        "SO Mapping",
        "Cash Eligibility",
        "Cash Bridge",
        "Data Quality"
    ]
)

# ---------------------------------------------------
# EXECUTIVE DASHBOARD
# ---------------------------------------------------

if page == "Executive Dashboard":

    st.subheader("Executive Pipeline Dashboard")

    total_pipeline = (
        pipeline.get(
            "Pipeline Amount",
            pd.Series(dtype=float)
        ).sum()
    )

    remaining_pipeline = (
        pipeline.get(
            "Remaining Pipeline",
            pd.Series(dtype=float)
        ).sum()
    )

    deal_count = len(pipeline)

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Pipeline",
        f"${total_pipeline:,.0f}"
    )

    col2.metric(
        "Remaining Pipeline",
        f"${remaining_pipeline:,.0f}"
    )

    col3.metric(
        "Deal Count",
        deal_count
    )

    st.dataframe(
        pipeline,
        use_container_width=True
    )

# ---------------------------------------------------
# PIPELINE CONTROL
# ---------------------------------------------------

elif page == "Pipeline Control":

    st.subheader("Pipeline Control")

    st.warning(
        "Pipeline visibility only. "
        "Deals missing timing or mapping "
        "should NOT feed liquidity."
    )

    edited_pipeline = st.data_editor(
        pipeline,
        use_container_width=True,
        num_rows="dynamic"
    )

# ---------------------------------------------------
# SO MAPPING
# ---------------------------------------------------

elif page == "SO Mapping":

    st.subheader("Pipeline to Sales Order Mapping")

    st.warning(
        "Many-to-many mapping allowed. "
        "Do not force one Deal ID to one SO."
    )

    st.data_editor(
        so_mapping,
        use_container_width=True,
        num_rows="dynamic"
    )

# ---------------------------------------------------
# CASH ELIGIBILITY
# ---------------------------------------------------

elif page == "Cash Eligibility":

    st.subheader("Cash Forecast Eligibility")

    st.warning(
        "Only eligible, mapped, timed items "
        "should feed liquidity."
    )

    st.dataframe(
        eligibility,
        use_container_width=True
    )

# ---------------------------------------------------
# CASH BRIDGE
# ---------------------------------------------------

elif page == "Cash Bridge":

    st.subheader("Weekly Cash Bridge Preview")

    st.warning(
        "Preview only. "
        "Must reconcile to workbook before use."
    )

    st.dataframe(
        cash_bridge,
        use_container_width=True
    )

# ---------------------------------------------------
# DATA QUALITY
# ---------------------------------------------------

elif page == "Data Quality":

    st.subheader("Data Quality Checks")

    checks = []

    # Duplicate Deal IDs

    if "Deal ID" in pipeline.columns:

        duplicate_deals = pipeline[
            pipeline["Deal ID"].duplicated(keep=False)
        ]

        checks.append(
            (
                "Duplicate Deal IDs",
                len(duplicate_deals)
            )
        )

    else:

        checks.append(
            (
                "Missing Deal ID Column",
                "FAIL"
            )
        )

    # Missing Close Dates

    if "Expected Close Date" in pipeline.columns:

        missing_close = pipeline[
            pipeline["Expected Close Date"].isna()
        ]

        checks.append(
            (
                "Missing Expected Close Dates",
                len(missing_close)
            )
        )

    # Cash Eligible Deals

    if "Cash Forecast Eligibility" in pipeline.columns:

        eligible = pipeline[
            pipeline[
                "Cash Forecast Eligibility"
            ].astype(str).str.contains(
                "Eligible",
                na=False
            )
        ]

        checks.append(
            (
                "Cash Eligible Deals",
                len(eligible)
            )
        )

    quality_df = pd.DataFrame(
        checks,
        columns=["Check", "Result"]
    )

    st.dataframe(
        quality_df,
        use_container_width=True
    )