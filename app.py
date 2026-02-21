import streamlit as st
import pandas as pd
import numpy as np
import io
import matplotlib.pyplot as plt

TOLERANCE = 20

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="GST 2B vs Books", layout="wide")

# ---------------- GOOGLE STYLE CSS ----------------
st.markdown("""
<style>
.big-title {
    font-size: 40px;
    font-weight: 600;
    color: #1a73e8;
    text-align: center;
}
.subtitle {
    text-align: center;
    color: grey;
    font-size: 16px;
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
st.markdown('<div class="subtitle">Automated GST Matching & Dashboard Tool</div>', unsafe_allow_html=True)
st.write("")

# ---------------- TEMPLATE DOWNLOAD ----------------

def create_template():
    template = pd.DataFrame({
        "NAME": [],
        "SUPPLIER GSTIN": [],
        "INVOICE NO": [],
        "TAXABLE VALUE": [],
        "IGST": [],
        "CGST": [],
        "SGST": []
    })
    return template

col1, col2 = st.columns(2)

with col1:
    template_2b = create_template()
    buffer_2b = io.BytesIO()
    template_2b.to_excel(buffer_2b, index=False)
    st.download_button(
        label="📥 Download 2B Template",
        data=buffer_2b.getvalue(),
        file_name="2B_Template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

with col2:
    template_books = create_template()
    buffer_books = io.BytesIO()
    template_books.to_excel(buffer_books, index=False)
    st.download_button(
        label="📥 Download Books Template",
        data=buffer_books.getvalue(),
        file_name="Books_Template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

st.divider()

# ---------------- FILE UPLOAD ----------------

file_2b = st.file_uploader("Upload GSTR-2B Excel", type=["xlsx"])
file_books = st.file_uploader("Upload Purchase Register Excel", type=["xlsx"])

# ---------------- VALIDATION FUNCTION ----------------

MANDATORY_COLUMNS = [
    "NAME",
    "SUPPLIER GSTIN",
    "INVOICE NO",
    "TAXABLE VALUE",
    "IGST",
    "CGST",
    "SGST"
]

def validate_columns(df):
    df.columns = df.columns.str.strip().str.upper()
    missing = [col for col in MANDATORY_COLUMNS if col not in df.columns]
    return missing

# ---------------- PROCESS ----------------

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

    df_2b["TAXABLE VALUE"] = pd.to_numeric(df_2b["TAXABLE VALUE"], errors="coerce")
    df_books["TAXABLE VALUE"] = pd.to_numeric(df_books["TAXABLE VALUE"], errors="coerce")

    df_2b["PRIMARY_KEY"] = df_2b["SUPPLIER GSTIN"].astype(str) + "|" + df_2b["INVOICE NO"].astype(str)
    df_books["PRIMARY_KEY"] = df_books["SUPPLIER GSTIN"].astype(str) + "|" + df_books["INVOICE NO"].astype(str)

    # PRIMARY MATCH
    primary = pd.merge(df_2b, df_books, on="PRIMARY_KEY", how="inner", suffixes=("_2B", "_BOOKS"))

    primary["TAX_DIFF"] = abs(primary["TAXABLE VALUE_2B"] - primary["TAXABLE VALUE_BOOKS"])

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

    # MISSING
    df_2b_unmatched = df_2b_unmatched.add_suffix("_2B")
    df_books_unmatched = df_books_unmatched.add_suffix("_BOOKS")

    df_2b_unmatched["MATCH STATUS"] = "MISSING IN BOOKS"
    df_books_unmatched["MATCH STATUS"] = "MISSING IN 2B"

    final_df = pd.concat([primary, df_2b_unmatched, df_books_unmatched], ignore_index=True)

    st.success("Reconciliation Completed Successfully ✅")
    st.dataframe(final_df)

    # DASHBOARD
    st.subheader("📊 Dashboard")

    status_counts = final_df["MATCH STATUS"].value_counts()
    fig, ax = plt.subplots()
    status_counts.plot(kind="pie", autopct="%1.1f%%", ax=ax)
    ax.set_ylabel("")
    st.pyplot(fig)

    # EXPORT
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        final_df.to_excel(writer, sheet_name="Reconciliation", index=False)

    st.download_button(
        label="📥 Download Final Report",
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
