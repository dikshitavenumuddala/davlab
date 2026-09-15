import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="Medicine Expiry & Waste Dashboard",
    page_icon="💊",
    layout="wide"
)

# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------
FILE_PATH = "data.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(FILE_PATH)

    # Clean column names
    df.columns = (
        df.columns
        .str.strip()
        .str.replace(" ", "_")
        .str.replace("/", "_")
    )

    return df


df = load_data()

# ---------------------------------------------------------
# TITLE
# ---------------------------------------------------------
st.title("💊 Medicine Expiry & Waste Management Dashboard")
st.markdown(
    "### Inventory • Expiry Risk • Waste • Financial Impact"
)

st.divider()

# ---------------------------------------------------------
# SIDEBAR FILTERS
# ---------------------------------------------------------
st.sidebar.header("🔎 Dashboard Filters")

filtered_df = df.copy()

# Medicine Category
if "Medicine_Category" in df.columns:
    categories = ["All"] + sorted(
        df["Medicine_Category"].dropna().astype(str).unique().tolist()
    )

    selected_category = st.sidebar.selectbox(
        "Medicine Category",
        categories
    )

    if selected_category != "All":
        filtered_df = filtered_df[
            filtered_df["Medicine_Category"].astype(str)
            == selected_category
        ]

# Dosage Form
if "Dosage_Form" in df.columns:
    forms = ["All"] + sorted(
        df["Dosage_Form"].dropna().astype(str).unique().tolist()
    )

    selected_form = st.sidebar.selectbox(
        "Dosage Form",
        forms
    )

    if selected_form != "All":
        filtered_df = filtered_df[
            filtered_df["Dosage_Form"].astype(str)
            == selected_form
        ]

# Manufacturer
if "Manufacturer" in df.columns:
    manufacturers = ["All"] + sorted(
        df["Manufacturer"].dropna().astype(str).unique().tolist()
    )

    selected_manufacturer = st.sidebar.selectbox(
        "Manufacturer",
        manufacturers
    )

    if selected_manufacturer != "All":
        filtered_df = filtered_df[
            filtered_df["Manufacturer"].astype(str)
            == selected_manufacturer
        ]

# Supplier
if "Supplier" in df.columns:
    suppliers = ["All"] + sorted(
        df["Supplier"].dropna().astype(str).unique().tolist()
    )

    selected_supplier = st.sidebar.selectbox(
        "Supplier",
        suppliers
    )

    if selected_supplier != "All":
        filtered_df = filtered_df[
            filtered_df["Supplier"].astype(str)
            == selected_supplier
        ]

# Expiry Status
if "Expiry_Status" in df.columns:
    expiry_statuses = ["All"] + sorted(
        df["Expiry_Status"].dropna().astype(str).unique().tolist()
    )

    selected_expiry = st.sidebar.selectbox(
        "Expiry Status",
        expiry_statuses
    )

    if selected_expiry != "All":
        filtered_df = filtered_df[
            filtered_df["Expiry_Status"].astype(str)
            == selected_expiry
        ]

# ---------------------------------------------------------
# HELPER FUNCTION
# ---------------------------------------------------------
def numeric_sum(column):
    if column in filtered_df.columns:
        return pd.to_numeric(
            filtered_df[column],
            errors="coerce"
        ).fillna(0).sum()
    return 0


# ---------------------------------------------------------
# KPI CALCULATIONS
# ---------------------------------------------------------
total_medicines = len(filtered_df)

current_stock = numeric_sum("Current_Stock")

wasted_quantity = numeric_sum("Quantity_Wasted")

potential_loss = numeric_sum("Potential_Loss")

stock_value = numeric_sum("Stock_Value")

# Medicines expiring within 30 days
if "Days_to_Expiry" in filtered_df.columns:

    days = pd.to_numeric(
        filtered_df["Days_to_Expiry"],
        errors="coerce"
    )

    expiring_30 = (days >= 0) & (days <= 30)
    expiring_30_count = expiring_30.sum()

    expiring_90 = (days >= 0) & (days <= 90)
    expiring_90_count = expiring_90.sum()

else:
    expiring_30_count = 0
    expiring_90_count = 0


# ---------------------------------------------------------
# KPI CARDS
# ---------------------------------------------------------
st.subheader("📊 Key Performance Indicators")

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric(
        "💊 Medicines",
        f"{total_medicines:,}"
    )

with col2:
    st.metric(
        "📦 Current Stock",
        f"{current_stock:,.0f}"
    )

with col3:
    st.metric(
        "🔴 Expiring <30 Days",
        f"{expiring_30_count:,}"
    )

with col4:
    st.metric(
        "🟠 Expiring <90 Days",
        f"{expiring_90_count:,}"
    )

with col5:
    st.metric(
        "🗑️ Quantity Wasted",
        f"{wasted_quantity:,.0f}"
    )

with col6:
    st.metric(
        "💰 Potential Loss",
        f"₹{potential_loss:,.2f}"
    )

st.divider()


# ---------------------------------------------------------
# EXPIRY STATUS CHART
# ---------------------------------------------------------
col1, col2 = st.columns(2)

with col1:

    st.subheader("⚠️ Expiry Status Distribution")

    if "Expiry_Status" in filtered_df.columns:

        expiry_data = (
            filtered_df["Expiry_Status"]
            .value_counts()
            .reset_index()
        )

        expiry_data.columns = [
            "Expiry_Status",
            "Count"
        ]

        fig = px.pie(
            expiry_data,
            names="Expiry_Status",
            values="Count",
            hole=0.45,
            title="Medicine Expiry Status"
        )

        fig.update_layout(
            legend_title="Expiry Status"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


# ---------------------------------------------------------
# STOCK BY CATEGORY
# ---------------------------------------------------------
with col2:

    st.subheader("📦 Stock by Medicine Category")

    if (
        "Medicine_Category" in filtered_df.columns
        and "Current_Stock" in filtered_df.columns
    ):

        category_stock = (
            filtered_df
            .groupby("Medicine_Category")["Current_Stock"]
            .sum()
            .reset_index()
            .sort_values(
                "Current_Stock",
                ascending=False
            )
        )

        fig = px.bar(
            category_stock,
            x="Medicine_Category",
            y="Current_Stock",
            title="Current Stock by Category",
            text_auto=True
        )

        fig.update_layout(
            xaxis_title="Medicine Category",
            yaxis_title="Current Stock"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


# ---------------------------------------------------------
# POTENTIAL LOSS BY CATEGORY
# ---------------------------------------------------------
col1, col2 = st.columns(2)

with col1:

    st.subheader("💰 Potential Loss by Category")

    if (
        "Medicine_Category" in filtered_df.columns
        and "Potential_Loss" in filtered_df.columns
    ):

        loss_category = (
            filtered_df
            .groupby("Medicine_Category")["Potential_Loss"]
            .sum()
            .reset_index()
            .sort_values(
                "Potential_Loss",
                ascending=False
            )
        )

        fig = px.bar(
            loss_category,
            x="Medicine_Category",
            y="Potential_Loss",
            title="Potential Financial Loss",
            text_auto=".2s"
        )

        fig.update_layout(
            xaxis_title="Medicine Category",
            yaxis_title="Potential Loss (₹)"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


# ---------------------------------------------------------
# WASTE BY DOSAGE FORM
# ---------------------------------------------------------
with col2:

    st.subheader("🗑️ Waste by Dosage Form")

    if (
        "Dosage_Form" in filtered_df.columns
        and "Quantity_Wasted" in filtered_df.columns
    ):

        waste_form = (
            filtered_df
            .groupby("Dosage_Form")["Quantity_Wasted"]
            .sum()
            .reset_index()
            .sort_values(
                "Quantity_Wasted",
                ascending=False
            )
        )

        fig = px.bar(
            waste_form,
            x="Dosage_Form",
            y="Quantity_Wasted",
            title="Quantity Wasted by Dosage Form",
            text_auto=True
        )

        fig.update_layout(
            xaxis_title="Dosage Form",
            yaxis_title="Quantity Wasted"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


# ---------------------------------------------------------
# EXPIRY TIMELINE
# ---------------------------------------------------------
st.subheader("📅 Medicines by Days Remaining Until Expiry")

if "Days_to_Expiry" in filtered_df.columns:

    expiry_days = pd.to_numeric(
        filtered_df["Days_to_Expiry"],
        errors="coerce"
    ).dropna()

    expiry_bins = pd.cut(
        expiry_days,
        bins=[
            -float("inf"),
            0,
            30,
            60,
            90,
            180,
            365,
            float("inf")
        ],
        labels=[
            "Expired",
            "0–30 Days",
            "31–60 Days",
            "61–90 Days",
            "91–180 Days",
            "181–365 Days",
            "1+ Year"
        ]
    )

    expiry_distribution = (
        expiry_bins
        .value_counts()
        .reindex([
            "Expired",
            "0–30 Days",
            "31–60 Days",
            "61–90 Days",
            "91–180 Days",
            "181–365 Days",
            "1+ Year"
        ])
        .fillna(0)
        .reset_index()
    )

    expiry_distribution.columns = [
        "Expiry_Range",
        "Number_of_Medicines"
    ]

    fig = px.bar(
        expiry_distribution,
        x="Expiry_Range",
        y="Number_of_Medicines",
        title="Expiry Risk Timeline",
        text_auto=True
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ---------------------------------------------------------
# TOP EXPIRY RISK MEDICINES
# ---------------------------------------------------------
st.subheader("🚨 Top Medicines at Expiry Risk")

if "Days_to_Expiry" in filtered_df.columns:

    risk_table = filtered_df.copy()

    risk_table["Days_to_Expiry"] = pd.to_numeric(
        risk_table["Days_to_Expiry"],
        errors="coerce"
    )

    risk_table = (
        risk_table
        .sort_values(
            "Days_to_Expiry",
            ascending=True
        )
        .head(10)
    )

    columns_to_show = [
        "Medicine_Name",
        "Medicine_Category",
        "Dosage_Form",
        "Days_to_Expiry",
        "Current_Stock",
        "Quantity_Wasted",
        "Potential_Loss",
        "Expiry_Status"
    ]

    available_columns = [
        col for col in columns_to_show
        if col in risk_table.columns
    ]

    st.dataframe(
        risk_table[available_columns],
        use_container_width=True,
        hide_index=True
    )


# ---------------------------------------------------------
# MANUFACTURER ANALYSIS
# ---------------------------------------------------------
st.subheader("🏭 Manufacturer Analysis")

if (
    "Manufacturer" in filtered_df.columns
    and "Potential_Loss" in filtered_df.columns
):

    manufacturer_data = (
        filtered_df
        .groupby("Manufacturer")["Potential_Loss"]
        .sum()
        .reset_index()
        .sort_values(
            "Potential_Loss",
            ascending=False
        )
        .head(10)
    )

    fig = px.bar(
        manufacturer_data,
        x="Potential_Loss",
        y="Manufacturer",
        orientation="h",
        title="Top Manufacturers by Potential Loss",
        text_auto=".2s"
    )

    fig.update_layout(
        yaxis={"categoryorder": "total ascending"},
        xaxis_title="Potential Loss (₹)",
        yaxis_title="Manufacturer"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ---------------------------------------------------------
# RAW DATA
# ---------------------------------------------------------
with st.expander("📋 View Filtered Dataset"):

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.divider()

st.caption(
    "Medicine Expiry & Waste Management Analytics Dashboard | "
    "Built using Python, Pandas, Streamlit & Plotly"
)