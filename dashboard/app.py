
import streamlit as st
import pandas as pd
from sqlalchemy import text
from src.database import engine

# Page configuration
st.set_page_config(
    page_title="E-Commerce Customer Intelligence",
    page_icon="📊",
    layout="wide"
)

# Dashboard heading
st.title("E-Commerce Customer Intelligence Dashboard")
st.caption("Real-Time Data Engineering and Customer Analytics Platform")

st.divider()

# Database connection test
try:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    st.success("PostgreSQL database connected successfully!")

    # Load RFM customer data
    rfm_query = """
        SELECT
            customer_id,
            recency_days,
            frequency,
            monetary,
            rfm_score,
            customer_segment
        FROM customer_rfm
    """

    rfm_df = pd.read_sql(text(rfm_query), engine)

    # KPI metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Customers", f"{len(rfm_df):,}")

    with col2:
        st.metric(
            "Total Customer Spending",
            f"₹{rfm_df['monetary'].sum():,.2f}"
        )

    with col3:
        st.metric(
            "Customer Segments",
            f"{rfm_df['customer_segment'].nunique():,}"
        )

    st.divider()

    # Customer segment summary
    st.subheader("Customer Segmentation")

    segment_summary = (
        rfm_df.groupby("customer_segment")
        .size()
        .reset_index(name="customers")
        .sort_values("customers", ascending=False)
    )

    st.bar_chart(
        segment_summary,
        x="customer_segment",
        y="customers"
    )

    # Customer data table
    st.subheader("Customer RFM Details")

    st.dataframe(
        rfm_df.sort_values("monetary", ascending=False),
        use_container_width=True
    )

except Exception as error:
    st.error("Unable to connect to the database or load dashboard data.")
    st.exception(error)
