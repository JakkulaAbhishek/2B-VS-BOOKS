import streamlit as st
import pandas as pd
import numpy as np
import io

TOLERANCE = 20
MAX_ROWS = 15000

st.set_page_config(page_title="GST Enterprise Formula Dashboard", layout="wide")
st.title("🚀 GST 2B vs Books – Formula Driven Reconciliation")

file_2b = st.file_uploader("Upload GSTR-2B Excel", type=["xlsx"])
file_pr = st.file_uploader("Upload Purchase Register Excel", type=["xlsx"])

if file_2b and file_pr:

    df_2b = pd.read_excel(file_2b)
    df_pr = pd.read_excel(file_pr)

    df_2b.columns = df_2b.columns.str.strip().str.upper()
    df_pr.columns = df_pr.columns.str.strip().str.upper()

    num_cols = ["TAXABLE VALUE","IGST","CGST","SGST"]

    for col in num_cols:
        df_2b[col] = pd.to_numeric(df_2b.get(col,0), errors="coerce").fillna(0)
        df_pr[col] = pd.to_numeric(df_pr.get(col,0), errors="coerce").fillna(0)

    df_2b["KEY"] = df_2b["SUPPLIER GSTIN"].astype(str)+"|"+df_2b["DOCUMENT NUMBER"].astype(str)
    df_pr["KEY"] = df_pr["SUPPLIER GSTIN"].astype(str)+"|"+df_pr["DOCUMENT NUMBER"].astype(str)

    merged = pd.merge(df_2b, df_pr, on="KEY", how="outer",
                      suffixes=(" (2B)", " (PR)"), indicator=True)

    rows = []

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

        rows.append({
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

    recon_df = pd.DataFrame(rows)

    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:

        workbook = writer.book

        header = workbook.add_format({
            "bold":True,
            "bg_color":"#1f4e79",
            "font_color":"white"
        })

        # ---------------- RECON SHEET ----------------
        recon_df.to_excel(writer, sheet_name="Reconciliation",
                          startrow=2, index=False)

        sheet = writer.sheets["Reconciliation"]

        # Row 1 – SUBTOTAL FORMULA (15000 rows coverage)
        for col in recon_df.select_dtypes(include=np.number).columns:
            idx = recon_df.columns.get_loc(col)
            col_letter = chr(65+idx)
            sheet.write_formula(
                0,
                idx,
                f"=SUBTOTAL(9,{col_letter}3:{col_letter}{MAX_ROWS})"
            )

        # Row 2 – Header
        for col_num, col_name in enumerate(recon_df.columns):
            sheet.write(1, col_num, col_name, header)

        # ---------------- RAW DATA SHEETS ----------------
        df_2b.to_excel(writer, sheet_name="2B Data", index=False)
        df_pr.to_excel(writer, sheet_name="Books Data", index=False)

        # ---------------- DASHBOARD (CHARTS ONLY) ----------------
        dash = workbook.add_worksheet("Dashboard")

        # Matching Status Summary (Formula Based)
        dash.write_row("A1",["Status","Count"],header)

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
        dash.insert_chart('D2',pie)

        # Top 10 2B Vendors – Using Pivot Table Formula Approach
        dash.write("A10","Top 10 2B Vendors (Dynamic)",header)

        dash.write_formula(
            "A11",
            '=SORTBY(UNIQUE(\'2B Data\'!A2:A15000),'
            'SUMIFS(\'2B Data\'!E:E,\'2B Data\'!A:A,UNIQUE(\'2B Data\'!A2:A15000)),-1)'
        )

    st.download_button(
        "⬇ Download Formula Based Enterprise Excel",
        output.getvalue(),
        "GST_Reconciliation_Enterprise.xlsx"
    )
