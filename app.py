import streamlit as st
import pandas as pd
import numpy as np
import io

TOLERANCE = 20

st.set_page_config(page_title="GST Reconciliation Pro", layout="wide")
st.title("🚀 GST 2B vs Books Reconciliation – Enterprise")

file_2b = st.file_uploader("Upload GSTR-2B Excel", type=["xlsx"])
file_pr = st.file_uploader("Upload Purchase Register Excel", type=["xlsx"])

if file_2b and file_pr:

    df_2b = pd.read_excel(file_2b)
    df_pr = pd.read_excel(file_pr)

    df_2b.columns = df_2b.columns.str.strip().str.upper()
    df_pr.columns = df_pr.columns.str.strip().str.upper()

    numeric_cols = ["TAXABLE VALUE","IGST","CGST","SGST"]

    for col in numeric_cols:
        df_2b[col] = pd.to_numeric(df_2b.get(col,0), errors="coerce").fillna(0)
        df_pr[col] = pd.to_numeric(df_pr.get(col,0), errors="coerce").fillna(0)

    df_2b["KEY"] = df_2b["SUPPLIER GSTIN"].astype(str) + "|" + df_2b["DOCUMENT NUMBER"].astype(str)
    df_pr["KEY"] = df_pr["SUPPLIER GSTIN"].astype(str) + "|" + df_pr["DOCUMENT NUMBER"].astype(str)

    merged = pd.merge(
        df_2b, df_pr,
        on="KEY",
        how="outer",
        suffixes=(" (2B)", " (PR)"),
        indicator=True
    )

    records = []

    for _, row in merged.iterrows():

        taxable_2b = row.get("TAXABLE VALUE (2B)",0)
        taxable_pr = row.get("TAXABLE VALUE (PR)",0)

        igst_2b = row.get("IGST (2B)",0)
        igst_pr = row.get("IGST (PR)",0)
        cgst_2b = row.get("CGST (2B)",0)
        cgst_pr = row.get("CGST (PR)",0)
        sgst_2b = row.get("SGST (2B)",0)
        sgst_pr = row.get("SGST (PR)",0)

        total_2b = igst_2b + cgst_2b + sgst_2b
        total_pr = igst_pr + cgst_pr + sgst_pr

        if row["_merge"] == "both":
            diff = abs(taxable_2b - taxable_pr)

            if diff == 0:
                status = "Exact"
                reason = "GSTIN + Invoice + Taxable matched"

            elif diff <= TOLERANCE:
                status = "Exact (Tolerance)"
                reason = "GSTIN + Invoice matched, Taxable within tolerance"

            else:
                status = "Value Mismatch"
                reason = "GSTIN + Invoice matched, Taxable mismatch"

        elif row["_merge"] == "left_only":
            status = "Missing in PR"
            reason = "Present in 2B but not in Purchase Register"

        else:
            status = "Missing in 2B"
            reason = "Present in Purchase Register but not in 2B"

        supplier = row.get("SUPPLIER NAME (2B)")
        if pd.isna(supplier):
            supplier = row.get("SUPPLIER NAME (PR)","")

        records.append({
            "Match Status": status,
            "Match Reason": reason,
            "Supplier Name": supplier,
            "Supplier GSTIN (2B)": row.get("SUPPLIER GSTIN (2B)",""),
            "Supplier GSTIN (PR)": row.get("SUPPLIER GSTIN (PR)",""),
            "My GSTIN (2B)": row.get("MY GSTIN (2B)",""),
            "My GSTIN (PR)": row.get("MY GSTIN (PR)",""),
            "Document Number (2B)": row.get("DOCUMENT NUMBER (2B)",""),
            "Document Number (PR)": row.get("DOCUMENT NUMBER (PR)",""),
            "Document Date (2B)": row.get("DOCUMENT DATE (2B)",""),
            "Document Date (PR)": row.get("DOCUMENT DATE (PR)",""),
            "Taxable Value (2B)": taxable_2b,
            "Taxable Value (PR)": taxable_pr,
            "Tax Difference (2B-PR)": taxable_2b - taxable_pr,
            "Total Tax (2B)": total_2b,
            "Total Tax (PR)": total_pr,
            "IGST (2B)": igst_2b,
            "IGST (PR)": igst_pr,
            "CGST (2B)": cgst_2b,
            "CGST (PR)": cgst_pr,
            "SGST (2B)": sgst_2b,
            "SGST (PR)": sgst_pr,
        })

    recon_df = pd.DataFrame(records)

    st.dataframe(recon_df, use_container_width=True)

    # ---------------- Excel Export ----------------
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:

        recon_df.to_excel(writer, sheet_name="Reconciliation", index=False)
        df_2b.to_excel(writer, sheet_name="2B Data", index=False)
        df_pr.to_excel(writer, sheet_name="Purchase Data", index=False)

        workbook = writer.book
        dash = workbook.add_worksheet("Dashboard")

        header = workbook.add_format({
            "bold":True,
            "bg_color":"#1f4e79",
            "font_color":"white"
        })

        dash.write("A1","GST RECONCILIATION DASHBOARD",header)

        dash.write("A3","Total Records")
        dash.write_formula("B3","=COUNTA(Reconciliation!A:A)-1")

        dash.write("A4","Exact %")
        dash.write_formula("B4",'=COUNTIF(Reconciliation!A:A,"Exact")/B3')

        dash.write("A5","Mismatch %")
        dash.write_formula("B5",'=COUNTIF(Reconciliation!A:A,"Value Mismatch")/B3')

        dash.write("A6","Missing %")
        dash.write_formula("B6",'=COUNTIF(Reconciliation!A:A,"Missing*")/B3')

        # Status Table
        dash.write_row("A8",["Status","Count"],header)

        dash.write("A9","Exact")
        dash.write_formula("B9",'=COUNTIF(Reconciliation!A:A,"Exact")')

        dash.write("A10","Value Mismatch")
        dash.write_formula("B10",'=COUNTIF(Reconciliation!A:A,"Value Mismatch")')

        dash.write("A11","Missing in PR")
        dash.write_formula("B11",'=COUNTIF(Reconciliation!A:A,"Missing in PR")')

        dash.write("A12","Missing in 2B")
        dash.write_formula("B12",'=COUNTIF(Reconciliation!A:A,"Missing in 2B")')

        chart = workbook.add_chart({'type':'pie'})
        chart.add_series({
            'categories': '=Dashboard!$A$9:$A$12',
            'values': '=Dashboard!$B$9:$B$12',
            'data_labels': {'percentage':True}
        })
        dash.insert_chart('D3', chart)

        # Top 10 2B
        top_2b = df_2b.groupby("SUPPLIER NAME")["TAXABLE VALUE"].sum().sort_values(ascending=False).head(10)
        top_2b.to_excel(writer, sheet_name="Top10_2B")

        # Top 10 PR
        top_pr = df_pr.groupby("SUPPLIER NAME")["TAXABLE VALUE"].sum().sort_values(ascending=False).head(10)
        top_pr.to_excel(writer, sheet_name="Top10_PR")

    st.download_button("⬇ Download Final Enterprise Report",
                       output.getvalue(),
                       "GST_Reconciliation_Enterprise.xlsx")
