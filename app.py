import streamlit as st
import pandas as pd
import numpy as np
import io

# ================= CONFIG =================
TOLERANCE = 20
MAX_ROWS = 15000

st.set_page_config(page_title="GST Reconciliation", layout="wide")

# ================= GOOGLE STYLE UI =================
st.markdown("""
<style>
body {background-color:#f5f5f5;}
h1 {color:#1a73e8; font-weight:600;}
div[data-testid="stFileUploader"] {background:white; padding:15px; border-radius:10px;}
.stButton>button {background:#1a73e8;color:white;border-radius:8px;height:40px;}
</style>
""", unsafe_allow_html=True)

st.title("GST 2B vs Books Reconciliation")

file_2b = st.file_uploader("Upload GSTR-2B Excel", type=["xlsx"])
file_pr = st.file_uploader("Upload Purchase Register Excel", type=["xlsx"])

# ================= PROCESS =================
if file_2b and file_pr:

    df_2b = pd.read_excel(file_2b)
    df_pr = pd.read_excel(file_pr)

    df_2b.columns = df_2b.columns.str.strip().str.upper()
    df_pr.columns = df_pr.columns.str.strip().str.upper()

    numeric_cols = ["TAXABLE VALUE","IGST","CGST","SGST"]

    for col in numeric_cols:
        df_2b[col] = pd.to_numeric(df_2b.get(col,0), errors="coerce").fillna(0)
        df_pr[col] = pd.to_numeric(df_pr.get(col,0), errors="coerce").fillna(0)

    df_2b["KEY"] = df_2b["SUPPLIER GSTIN"].astype(str)+"|"+df_2b["DOCUMENT NUMBER"].astype(str)
    df_pr["KEY"] = df_pr["SUPPLIER GSTIN"].astype(str)+"|"+df_pr["DOCUMENT NUMBER"].astype(str)

    merged = pd.merge(
        df_2b,
        df_pr,
        on="KEY",
        how="outer",
        suffixes=(" (2B)", " (PR)"),
        indicator=True
    )

    records = []

    for _, r in merged.iterrows():

        taxable_2b = r.get("TAXABLE VALUE (2B)",0)
        taxable_pr = r.get("TAXABLE VALUE (PR)",0)

        igst_2b = r.get("IGST (2B)",0)
        cgst_2b = r.get("CGST (2B)",0)
        sgst_2b = r.get("SGST (2B)",0)

        igst_pr = r.get("IGST (PR)",0)
        cgst_pr = r.get("CGST (PR)",0)
        sgst_pr = r.get("SGST (PR)",0)

        total_2b = igst_2b + cgst_2b + sgst_2b
        total_pr = igst_pr + cgst_pr + sgst_pr

        if r["_merge"]=="both":
            diff = abs(taxable_2b-taxable_pr)
            if diff==0:
                status="Exact"
                reason="GSTIN+Invoice+Taxable matched"
            elif diff<=TOLERANCE:
                status="Exact (Tolerance)"
                reason="Within tolerance"
            else:
                status="Value Mismatch"
                reason="Taxable mismatch"
        elif r["_merge"]=="left_only":
            status="Missing in PR"
            reason="Present only in 2B"
        else:
            status="Missing in 2B"
            reason="Present only in PR"

        supplier = r.get("SUPPLIER NAME (2B)")
        if pd.isna(supplier):
            supplier = r.get("SUPPLIER NAME (PR)","")

        records.append({
            "Match Status":status,
            "Match Reason":reason,
            "Supplier Name":supplier,
            "Supplier GSTIN (2B)":r.get("SUPPLIER GSTIN (2B)",""),
            "Supplier GSTIN (PR)":r.get("SUPPLIER GSTIN (PR)",""),
            "Document Number (2B)":r.get("DOCUMENT NUMBER (2B)",""),
            "Document Number (PR)":r.get("DOCUMENT NUMBER (PR)",""),
            "Taxable Value (2B)":taxable_2b,
            "Taxable Value (PR)":taxable_pr,
            "Total Tax (2B)":total_2b,
            "Total Tax (PR)":total_pr,
            "IGST (2B)":igst_2b,
            "IGST (PR)":igst_pr,
            "CGST (2B)":cgst_2b,
            "CGST (PR)":cgst_pr,
            "SGST (2B)":sgst_2b,
            "SGST (PR)":sgst_pr,
        })

    recon_df = pd.DataFrame(records)

    # ================= EXCEL GENERATION =================
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:

        workbook = writer.book

        header_format = workbook.add_format({
            "bold":True,
            "bg_color":"#1a73e8",
            "font_color":"white",
            "border":1
        })

        # ---------- RECON SHEET ----------
        recon_df.to_excel(
            writer,
            sheet_name="Reconciliation",
            startrow=2,
            index=False,
            header=False
        )

        sheet = writer.sheets["Reconciliation"]

        # Row 1 = Subtotal formulas
        for col in recon_df.select_dtypes(include=np.number).columns:
            idx = recon_df.columns.get_loc(col)
            col_letter = chr(65+idx)
            sheet.write_formula(
                0,
                idx,
                f"=SUBTOTAL(9,{col_letter}3:{col_letter}{MAX_ROWS})"
            )

        # Row 2 = Headers (only once)
        for col_num, col_name in enumerate(recon_df.columns):
            sheet.write(1, col_num, col_name, header_format)

        # Auto width
        for i, col in enumerate(recon_df.columns):
            width = max(recon_df[col].astype(str).map(len).max(), len(col)) + 2
            sheet.set_column(i, i, width)

        # ---------- RAW DATA ----------
        df_2b.to_excel(writer, sheet_name="2B Data", index=False)
        df_pr.to_excel(writer, sheet_name="Books Data", index=False)

        # ---------- DASHBOARD ----------
        dash = workbook.add_worksheet("Dashboard")

        dash.write_row("A1",["Status","Count"],header_format)

        statuses = ["Exact","Exact (Tolerance)",
                    "Value Mismatch","Missing in PR","Missing in 2B"]

        for i,status in enumerate(statuses):
            dash.write(1+i,0,status)
            dash.write_formula(
                1+i,1,
                f'=COUNTIF(Reconciliation!A3:A{MAX_ROWS},"{status}")'
            )

        pie = workbook.add_chart({'type':'pie'})
        pie.add_series({
            'categories': '=Dashboard!$A$2:$A$6',
            'values': '=Dashboard!$B$2:$B$6',
            'data_labels': {'percentage':True}
        })

        dash.insert_chart('D2', pie)

    st.success("Reconciliation generated successfully")

    st.download_button(
        "Download Enterprise Excel",
        output.getvalue(),
        "GST_Reconciliation_Final.xlsx"
    )
