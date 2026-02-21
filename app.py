import streamlit as st
import pandas as pd
import numpy as np
import io
import plotly.express as px

TOLERANCE = 20

st.set_page_config(page_title="GST Reconciliation Pro", layout="wide")
st.title("🚀 GST 2B vs Books – Enterprise Reconciliation Suite")

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

    merged = pd.merge(df_2b, df_pr, on="KEY", how="outer",
                      suffixes=(" (2B)", " (PR)"), indicator=True)

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
                reason = "Taxable within tolerance"
            else:
                status = "Value Mismatch"
                reason = "Taxable mismatch"

        elif row["_merge"] == "left_only":
            status = "Missing in PR"
            reason = "Present in 2B only"
        else:
            status = "Missing in 2B"
            reason = "Present in PR only"

        supplier = row.get("SUPPLIER NAME (2B)")
        if pd.isna(supplier):
            supplier = row.get("SUPPLIER NAME (PR)","")

        records.append({
            "Match Status": status,
            "Match Reason": reason,
            "Supplier Name": supplier,
            "Taxable (2B)": taxable_2b,
            "Taxable (PR)": taxable_pr,
            "Difference": taxable_2b - taxable_pr,
            "Total Tax (2B)": total_2b,
            "Total Tax (PR)": total_pr,
            "IGST (2B)": igst_2b,
            "CGST (2B)": cgst_2b,
            "SGST (2B)": sgst_2b,
            "IGST (PR)": igst_pr,
            "CGST (PR)": cgst_pr,
            "SGST (PR)": sgst_pr,
        })

    recon_df = pd.DataFrame(records)

    # ---------------- WEB DASHBOARD ----------------
    st.subheader("📊 Web Dashboard")

    col1, col2 = st.columns(2)

    fig1 = px.pie(recon_df, names="Match Status", title="Matching Status")
    col1.plotly_chart(fig1, use_container_width=True)

    # Top 10 2B + Others
    top2b = df_2b.groupby("SUPPLIER NAME")[["TAXABLE VALUE","IGST","CGST","SGST"]].sum()
    top2b = top2b.sort_values("TAXABLE VALUE", ascending=False)

    top10_2b = top2b.head(10)
    others_2b = top2b.iloc[10:].sum()

    if len(top2b) > 10:
        top10_2b.loc["Others"] = others_2b

    fig2 = px.pie(top10_2b, values="TAXABLE VALUE",
                  names=top10_2b.index,
                  title="Top 10 Vendors – 2B (Taxable)")
    col2.plotly_chart(fig2, use_container_width=True)

    st.divider()

    col3, col4 = st.columns(2)

    toppr = df_pr.groupby("SUPPLIER NAME")[["TAXABLE VALUE","IGST","CGST","SGST"]].sum()
    toppr = toppr.sort_values("TAXABLE VALUE", ascending=False)

    top10_pr = toppr.head(10)
    others_pr = toppr.iloc[10:].sum()

    if len(toppr) > 10:
        top10_pr.loc["Others"] = others_pr

    fig3 = px.pie(top10_pr, values="TAXABLE VALUE",
                  names=top10_pr.index,
                  title="Top 10 Vendors – PR (Taxable)")
    col3.plotly_chart(fig3, use_container_width=True)

    st.dataframe(recon_df, use_container_width=True)

    # ---------------- Excel Export ----------------
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:

        workbook = writer.book

        # DASHBOARD FIRST
        dash = workbook.add_worksheet("Dashboard")

        header = workbook.add_format({
            "bold":True,
            "bg_color":"#1f4e79",
            "font_color":"white"
        })

        dash.write("A1","GST RECONCILIATION DASHBOARD",header)

        dash.write_row("A3",["Status","Count"],header)

        statuses = recon_df["Match Status"].value_counts()

        row = 3
        for status, count in statuses.items():
            dash.write(row,0,status)
            dash.write(row,1,count)
            row += 1

        chart = workbook.add_chart({'type':'pie'})
        chart.add_series({
            'categories': f'=Dashboard!$A$4:$A${row}',
            'values': f'=Dashboard!$B$4:$B${row}',
            'data_labels': {'percentage':True}
        })

        dash.insert_chart('D3', chart)

        # RECON SHEET
        recon_df.to_excel(writer, sheet_name="Reconciliation", index=False)
        sheet = writer.sheets["Reconciliation"]

        for col_num, value in enumerate(recon_df.columns.values):
            sheet.write(0, col_num, value, header)

        # Subtotal row
        last_row = len(recon_df) + 1
        sheet.write(f"A{last_row+1}", "TOTAL", header)

        numeric_columns = ["Taxable (2B)","Taxable (PR)","Difference",
                           "Total Tax (2B)","Total Tax (PR)",
                           "IGST (2B)","CGST (2B)","SGST (2B)",
                           "IGST (PR)","CGST (PR)","SGST (PR)"]

        for col in numeric_columns:
            col_idx = recon_df.columns.get_loc(col)
            col_letter = chr(65 + col_idx)
            sheet.write_formula(
                last_row,
                col_idx,
                f"=SUBTOTAL(9,{col_letter}2:{col_letter}{last_row})"
            )

        df_2b.to_excel(writer, sheet_name="2B Data", index=False)
        df_pr.to_excel(writer, sheet_name="Purchase Data", index=False)

    st.download_button("⬇ Download Final Enterprise Dashboard Report",
                       output.getvalue(),
                       "GST_Reconciliation_Enterprise.xlsx")
