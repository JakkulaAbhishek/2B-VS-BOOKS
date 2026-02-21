import streamlit as st
import pandas as pd
import numpy as np
import io
import matplotlib.pyplot as plt

TOLERANCE = 20

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="GST 2B vs Books", layout="wide")

# ---------------- GOOGLE STYLE UI ----------------
st.markdown("""
<style>
.big-title {
    font-size: 38px;
    font-weight: 600;
    color: #1a73e8;
    text-align: center;
}
.subtitle {
    text-align: center;
    color: grey;
    font-size: 15px;
}
.footer {
    text-align:center;
    margin-top:50px;
    color:grey;
    font-size:14px;
}
.stButton>button {
    background-color:#1a73e8;
    color:white;
    border-radius:8px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="big-title">GST 2B vs Purchase Reconciliation</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Automated GST Matching with Dashboard</div>', unsafe_allow_html=True)
st.write("")

# ---------------- COMMON TEMPLATE ----------------
def create_template():
    return pd.DataFrame({
        "NAME": [],
        "SUPPLIER GSTIN": [],
        "INVOICE NO": [],
        "INVOICE DATE": [],
        "TAXABLE VALUE": [],
        "IGST": [],
        "CGST": [],
        "SGST": []
    })

template = create_template()
buffer = io.BytesIO()
template.to_excel(buffer, index=False)

st.download_button(
    label="📥 Download Common 2B & Books Template",
    data=buffer.getvalue(),
    file_name="2B_Books_Template.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.divider()

# ---------------- FILE UPLOAD ----------------
file_2b = st.file_uploader("Upload GSTR-2B Excel", type=["xlsx"])
file_books = st.file_uploader("Upload Purchase Register Excel", type=["xlsx"])

MANDATORY_COLUMNS = [
    "NAME",
    "SUPPLIER GSTIN",
    "INVOICE NO",
    "INVOICE DATE",
    "TAXABLE VALUE",
    "IGST",
    "CGST",
    "SGST"
]

def validate_columns(df):
    df.columns = df.columns.str.strip().str.upper()
    return [col for col in MANDATORY_COLUMNS if col not in df.columns]

if file_2b and file_books:

    df_2b = pd.read_excel(file_2b)
    df_books = pd.read_excel(file_books)

    missing_2b = validate_columns(df_2b)
    missing_books = validate_columns(df_books)

    if missing_2b:
        st.error(f"2B File Missing Columns: {missing_2b}")
        st.stop()

    if missing_books:
        st.error(f"Books File Missing Columns: {missing_books}")
        st.stop()

    df_2b.columns = df_2b.columns.str.strip().str.upper()
    df_books.columns = df_books.columns.str.strip().str.upper()

    # Convert types
    df_2b["INVOICE DATE"] = pd.to_datetime(df_2b["INVOICE DATE"], errors="coerce")
    df_books["INVOICE DATE"] = pd.to_datetime(df_books["INVOICE DATE"], errors="coerce")

    numeric_cols = ["TAXABLE VALUE", "IGST", "CGST", "SGST"]
    for col in numeric_cols:
        df_2b[col] = pd.to_numeric(df_2b[col], errors="coerce")
        df_books[col] = pd.to_numeric(df_books[col], errors="coerce")

    # Create Primary Key
    df_2b["PRIMARY_KEY"] = df_2b["SUPPLIER GSTIN"].astype(str) + "|" + df_2b["INVOICE NO"].astype(str)
    df_books["PRIMARY_KEY"] = df_books["SUPPLIER GSTIN"].astype(str) + "|" + df_books["INVOICE NO"].astype(str)

    # ---------------- PRIMARY MATCH ----------------
    primary = pd.merge(df_2b, df_books, on="PRIMARY_KEY", how="inner", suffixes=("_2B", "_BOOKS"))

    primary["TAX_DIFF"] = abs(primary["TAXABLE VALUE_2B"] - primary["TAXABLE VALUE_BOOKS"])
    primary["GST_DIFF"] = abs(
        (primary["IGST_2B"] + primary["CGST_2B"] + primary["SGST_2B"]) -
        (primary["IGST_BOOKS"] + primary["CGST_BOOKS"] + primary["SGST_BOOKS"])
    )

    primary["MATCH STATUS"] = np.select(
        [
            primary["TAX_DIFF"] == 0,
            primary["TAX_DIFF"] <= TOLERANCE
        ],
        [
            "EXACT MATCH",
            "EXACT MATCH (WITHIN ₹20)"
        ],
        default="INVOICE MATCH – VALUE MISMATCH"
    )

    matched_keys = primary["PRIMARY_KEY"]

    df_2b_unmatched = df_2b[~df_2b["PRIMARY_KEY"].isin(matched_keys)]
    df_books_unmatched = df_books[~df_books["PRIMARY_KEY"].isin(matched_keys)]

    # ---------------- SECONDARY MATCH ----------------
    secondary_rows = []

    for _, row_2b in df_2b_unmatched.iterrows():
        possible = df_books_unmatched[
            (df_books_unmatched["SUPPLIER GSTIN"] == row_2b["SUPPLIER GSTIN"]) &
            (abs(df_books_unmatched["TAXABLE VALUE"] - row_2b["TAXABLE VALUE"]) <= TOLERANCE)
        ]

        if not possible.empty:
            row_books = possible.iloc[0]
            combined = pd.concat([
                row_2b.add_suffix("_2B"),
                row_books.add_suffix("_BOOKS")
            ])
            combined["MATCH STATUS"] = "MATCHED WITH TAXABLE VALUE (WITHIN ₹20)"
            secondary_rows.append(combined)
            df_books_unmatched = df_books_unmatched.drop(row_books.name)

    secondary = pd.DataFrame(secondary_rows)

    # ---------------- MISSING ----------------
    df_2b_unmatched = df_2b_unmatched.add_suffix("_2B")
    df_books_unmatched = df_books_unmatched.add_suffix("_BOOKS")

    df_2b_unmatched["MATCH STATUS"] = "MISSING IN BOOKS"
    df_books_unmatched["MATCH STATUS"] = "MISSING IN 2B"

    # ---------------- FINAL DATA ----------------
    final_df = pd.concat([primary, secondary, df_2b_unmatched, df_books_unmatched], ignore_index=True)

    st.success("Reconciliation Completed Successfully ✅")
    st.dataframe(final_df)

    # ---------------- DASHBOARD ----------------
    st.subheader("📊 Dashboard")

    status_counts = final_df["MATCH STATUS"].value_counts()
    total_2b = len(df_2b)
    exact = status_counts.get("EXACT MATCH", 0)
    tolerance_match = status_counts.get("EXACT MATCH (WITHIN ₹20)", 0)
    overall_percent = ((exact + tolerance_match) / total_2b) * 100 if total_2b > 0 else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Total 2B Records", total_2b)
    col2.metric("Exact Matches", exact)
    col3.metric("Overall Match %", f"{overall_percent:.2f}%")

    fig, ax = plt.subplots()
    status_counts.plot(kind="pie", autopct="%1.1f%%", ax=ax)
    ax.set_ylabel("")
    st.pyplot(fig)

    # ---------------- EXPORT ----------------
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        final_df.to_excel(writer, sheet_name="Reconciliation", index=False)
        status_counts.reset_index().to_excel(writer, sheet_name="Dashboard", index=False)

    st.download_button(
        label="📥 Download Final GST Reconciliation Report",
        data=output.getvalue(),
        file_name="GST_Reconciliation_Report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ---------------- FOOTER ----------------
st.markdown("""
<div class="footer">
Tool developed by <b>ABHISHEK JAKKULA</b><br>
GMAIL: jakkulaabhishek5@gmail.com
</div>
""", unsafe_allow_html=True)
