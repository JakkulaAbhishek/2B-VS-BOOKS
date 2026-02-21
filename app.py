import streamlit as st
import pandas as pd
import numpy as np
import io
import plotly.express as px

TOLERANCE = 20

st.set_page_config(page_title="GST Reconciliation Enterprise", layout="wide")

st.markdown("""
<style>
.main {background-color:#f4f6f9;}
h1 {color:#1f4e79;}
.stButton>button {background-color:#1f4e79;color:white;border-radius:8px;}
</style>
""", unsafe_allow_html=True)

st.title("🚀 GST 2B vs Books – Enterprise Reconciliation")

file_2b = st.file_uploader("Upload GSTR-2B Excel", type=["xlsx"])
file_pr = st.file_uploader("Upload Purchase Register Excel", type=["xlsx"])

if file_2b and file_pr:

    df_2b = pd.read_excel(file_2b)
    df_pr = pd.read_excel(file_pr)

    df_2b.columns = df_2b.columns.str.strip().str.upper()
    df_pr.columns = df_pr.columns.str.strip().str.upper()

    numeric = ["TAXABLE VALUE","IGST","CGST","SGST"]

    for col in numeric:
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
            "Tax Difference (2B-PR)":taxable_2b-taxable_pr,
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

    # ----------- WEB DASHBOARD ------------
    st.subheader("📊 Live Dashboard")

    fig = px.pie(recon_df, names="Match Status")
    st.plotly_chart(fig, use_container_width=True)

    # ----------- EXCEL CREATION ------------
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:

        workbook = writer.book
        header = workbook.add_format({
            "bold":True,
            "bg_color":"#1f4e79",
            "font_color":"white",
            "border":1
        })

        number_fmt = workbook.add_format({'num_format':'#,##0.00'})

        # ================= DASHBOARD =================
        dash = workbook.add_worksheet("Dashboard")

        dash.write("A1","GST RECONCILIATION DASHBOARD",header)

        dash.write_row("A3",["Status","Count"],header)

        status_counts = recon_df["Match Status"].value_counts()

        r=3
        for k,v in status_counts.items():
            dash.write(r,0,k)
            dash.write(r,1,v)
            r+=1

        pie = workbook.add_chart({'type':'pie'})
        pie.add_series({
            'categories':f'=Dashboard!$A$4:$A${r}',
            'values':f'=Dashboard!$B$4:$B${r}',
            'data_labels':{'percentage':True}
        })
        dash.insert_chart('D3',pie)

        # ================= RECON SHEET =================
        recon_df.to_excel(writer,sheet_name="Reconciliation",startrow=1,index=False)
        sheet = writer.sheets["Reconciliation"]

        # SUBTOTAL FIRST ROW (NO GAP)
        sheet.write_row(0,0,recon_df.columns,header)

        for col in recon_df.select_dtypes(include=np.number).columns:
            idx = recon_df.columns.get_loc(col)
            col_letter = chr(65+idx)
            sheet.write_formula(
                0,
                idx,
                f"=SUBTOTAL(9,{col_letter}2:{col_letter}{len(recon_df)+1})",
                number_fmt
            )

        # Auto column width
        for i,col in enumerate(recon_df.columns):
            width = max(recon_df[col].astype(str).map(len).max(),len(col))+2
            sheet.set_column(i,i,width)

        # 2B & PR raw sheets
        df_2b.to_excel(writer,sheet_name="2B Data",index=False)
        df_pr.to_excel(writer,sheet_name="Purchase Data",index=False)

    st.download_button("⬇ Download Enterprise Excel",
                       output.getvalue(),
                       "GST_Reconciliation_Enterprise.xlsx")
