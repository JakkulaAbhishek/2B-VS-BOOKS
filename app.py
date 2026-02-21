import streamlit as st
import pandas as pd
import numpy as np
import io
import matplotlib.pyplot as plt

TOLERANCE = 20

st.set_page_config(page_title="2B vs Books Reconciliation", layout="wide")

st.title("📊 GST 2B vs Purchase Reconciliation Tool")

file_2b = st.file_uploader("Upload GSTR-2B Excel", type=["xlsx"])
file_books = st.file_uploader("Upload Purchase Register Excel", type=["xlsx"])

if file_2b and file_books:

    df_2b = pd.read_excel(file_2b)
    df_books = pd.read_excel(file_books)

    df_2b.columns = df_2b.columns.str.strip().str.upper()
    df_books.columns = df_books.columns.str.strip().str.upper()

    df_2b["TAXABLE VALUE"] = pd.to_numeric(df_2b["TAXABLE VALUE"], errors="coerce")
    df_books["TAXABLE VALUE"] = pd.to_numeric(df_books["TAXABLE VALUE"], errors="coerce")

    df_2b["PRIMARY_KEY"] = df_2b["SUPPLIER GSTIN"].astype(str) + "|" + df_2b["INVOICE NO"].astype(str)
    df_books["PRIMARY_KEY"] = df_books["SUPPLIER GSTIN"].astype(str) + "|" + df_books["INVOICE NO"].astype(str)

    # ---------------- PRIMARY MATCH ----------------
    primary_match = pd.merge(
        df_2b,
        df_books,
        on="PRIMARY_KEY",
        how="inner",
        suffixes=("_2B", "_BOOKS")
    )

    primary_match["TAX_DIFF"] = abs(
        primary_match["TAXABLE VALUE_2B"] - primary_match["TAXABLE VALUE_BOOKS"]
    )

    primary_match["MATCH STATUS"] = np.select(
        [
            primary_match["TAX_DIFF"] == 0,
            primary_match["TAX_DIFF"] <= TOLERANCE
        ],
        [
            "EXACT MATCH",
            "EXACT MATCH (WITHIN ₹20)"
        ],
        default="INVOICE MATCH – VALUE MISMATCH"
    )

    matched_keys = primary_match["PRIMARY_KEY"]

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

    secondary_match = pd.DataFrame(secondary_rows)

    # ---------------- MISSING ----------------
    df_2b_unmatched = df_2b_unmatched.add_suffix("_2B")
    df_books_unmatched = df_books_unmatched.add_suffix("_BOOKS")

    df_2b_unmatched["MATCH STATUS"] = "MISSING IN BOOKS"
    df_books_unmatched["MATCH STATUS"] = "MISSING IN 2B"

    # ---------------- FINAL ----------------
    final_df = pd.concat(
        [primary_match, secondary_match, df_2b_unmatched, df_books_unmatched],
        ignore_index=True
    )

    st.success("Reconciliation Completed ✅")

    st.dataframe(final_df.head(50))

    # ---------------- DASHBOARD ----------------
    st.subheader("📈 Dashboard")

    status_counts = final_df["MATCH STATUS"].value_counts()
    total_2b = len(df_2b)
    exact = status_counts.get("EXACT MATCH", 0)
    tolerance = status_counts.get("EXACT MATCH (WITHIN ₹20)", 0)
    overall_match_percent = ((exact + tolerance) / total_2b) * 100

    col1, col2, col3 = st.columns(3)
    col1.metric("Total 2B Records", total_2b)
    col2.metric("Exact Matches", exact)
    col3.metric("Overall Match %", f"{overall_match_percent:.2f}%")

    fig, ax = plt.subplots()
    status_counts.plot(kind="pie", autopct="%1.1f%%", ax=ax)
    ax.set_ylabel("")
    st.pyplot(fig)

    # ---------------- EXCEL EXPORT ----------------
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        final_df.to_excel(writer, sheet_name="Reconciliation", index=False)

        dashboard_df = status_counts.reset_index()
        dashboard_df.columns = ["Match Status", "Count"]
        dashboard_df.to_excel(writer, sheet_name="Dashboard", index=False)

    st.download_button(
        label="📥 Download Reconciliation Report",
        data=output.getvalue(),
        file_name="GST_Reconciliation_Report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
