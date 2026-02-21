import streamlit as st
import pandas as pd
import numpy as np
import io
import xlsxwriter

TOLERANCE = 20

st.set_page_config(page_title="GST 2B vs Books", layout="wide")
st.title("GST 2B vs Purchase Reconciliation Tool")

# ---------------- TEMPLATE ----------------
def create_template():
    return pd.DataFrame({
        "SUPPLIER NAME": [],
        "SUPPLIER GSTIN": [],
        "MY GSTIN": [],
        "DOCUMENT NUMBER": [],
        "DOCUMENT DATE": [],
        "TAXABLE VALUE": [],
        "IGST": [],
        "CGST": [],
        "SGST": []
    })

template = create_template()
buffer = io.BytesIO()
template.to_excel(buffer, index=False)

st.download_button(
    "Download Common Template",
    buffer.getvalue(),
    "2B_Books_Template.xlsx"
)

st.divider()

file_2b = st.file_uploader("Upload GSTR-2B", type=["xlsx"])
file_pr = st.file_uploader("Upload Purchase Register", type=["xlsx"])

if file_2b and file_pr:

    df_2b = pd.read_excel(file_2b)
    df_pr = pd.read_excel(file_pr)

    df_2b.columns = df_2b.columns.str.strip().str.upper()
    df_pr.columns = df_pr.columns.str.strip().str.upper()

    numeric_cols = ["TAXABLE VALUE","IGST","CGST","SGST"]
    for col in numeric_cols:
        df_2b[col] = pd.to_numeric(df_2b[col], errors="coerce").fillna(0)
        df_pr[col] = pd.to_numeric(df_pr[col], errors="coerce").fillna(0)

    df_2b["PRIMARY_KEY"] = df_2b["SUPPLIER GSTIN"].astype(str) + "|" + df_2b["DOCUMENT NUMBER"].astype(str)
    df_pr["PRIMARY_KEY"] = df_pr["SUPPLIER GSTIN"].astype(str) + "|" + df_pr["DOCUMENT NUMBER"].astype(str)

    merged = pd.merge(
        df_2b, df_pr,
        on="PRIMARY_KEY",
        how="outer",
        suffixes=(" (2B)", " (PR)"),
        indicator=True
    )

    output_rows = []

    for _, row in merged.iterrows():

        taxable_2b = row.get("TAXABLE VALUE (2B)", 0)
        taxable_pr = row.get("TAXABLE VALUE (PR)", 0)

        tax_2b = row.get("IGST (2B)",0) + row.get("CGST (2B)",0) + row.get("SGST (2B)",0)
        tax_pr = row.get("IGST (PR)",0) + row.get("CGST (PR)",0) + row.get("SGST (PR)",0)

        if row["_merge"] == "both":
            diff = abs(taxable_2b - taxable_pr)
            if diff == 0:
                status = "Exact"
            elif diff <= TOLERANCE:
                status = "Exact (Within 20)"
            else:
                status = "Value Mismatch"
        elif row["_merge"] == "left_only":
            status = "Missing in PR"
        else:
            status = "Missing in 2B"

        output_rows.append({
            "Match Status": status,
            "Supplier Name": row.get("SUPPLIER NAME (2B)", row.get("SUPPLIER NAME (PR)", "")),
            "Taxable Value (2B)": taxable_2b,
            "Taxable Value (PR)": taxable_pr
        })

    final_df = pd.DataFrame(output_rows)

    st.success("Reconciliation Completed")
    st.dataframe(final_df)

    # ---------------- EXCEL EXPORT ----------------
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)

    recon_sheet = workbook.add_worksheet("Reconciliation")
    dash_sheet = workbook.add_worksheet("Dashboard")
    sheet_2b = workbook.add_worksheet("2B Data")
    sheet_pr = workbook.add_worksheet("PR Data")

    header_format = workbook.add_format({'bold': True, 'bg_color': '#D9E1F2', 'border':1})

    # Write Reconciliation
    for col_num, col_name in enumerate(final_df.columns):
        recon_sheet.write(0, col_num, col_name, header_format)

    for row_num, row_data in enumerate(final_df.values):
        for col_num, cell in enumerate(row_data):
            recon_sheet.write(row_num+1, col_num, cell)

    # Write original data
    df_2b.to_excel(pd.ExcelWriter(output, engine='xlsxwriter'), sheet_name="2B Data")

    # Instead manual writing to avoid conflict
    for col_num, col_name in enumerate(df_2b.columns):
        sheet_2b.write(0, col_num, col_name, header_format)
    for row_num, row_data in enumerate(df_2b.values):
        for col_num, cell in enumerate(row_data):
            sheet_2b.write(row_num+1, col_num, cell)

    for col_num, col_name in enumerate(df_pr.columns):
        sheet_pr.write(0, col_num, col_name, header_format)
    for row_num, row_data in enumerate(df_pr.values):
        for col_num, cell in enumerate(row_data):
            sheet_pr.write(row_num+1, col_num, cell)

    last_row = len(final_df) + 1

    # ---------------- DASHBOARD FORMULAS ----------------
    dash_sheet.write("A1","Exact")
    dash_sheet.write("B1", f"=COUNTIF(Reconciliation!A2:A{last_row},\"Exact*\")")

    dash_sheet.write("A2","Missing in PR")
    dash_sheet.write("B2", f"=COUNTIF(Reconciliation!A2:A{last_row},\"Missing in PR\")")

    dash_sheet.write("A3","Missing in 2B")
    dash_sheet.write("B3", f"=COUNTIF(Reconciliation!A2:A{last_row},\"Missing in 2B\")")

    dash_sheet.write("A4","Value Mismatch")
    dash_sheet.write("B4", f"=COUNTIF(Reconciliation!A2:A{last_row},\"Value Mismatch\")")

    # Pie Chart
    chart = workbook.add_chart({'type':'pie'})
    chart.add_series({
        'categories': '=Dashboard!$A$1:$A$4',
        'values': '=Dashboard!$B$1:$B$4',
        'data_labels': {'percentage':True}
    })
    dash_sheet.insert_chart('D2', chart)

    # ---------------- TOP 10 2B ----------------
    top2b = df_2b.groupby("SUPPLIER NAME")["TAXABLE VALUE"].sum().sort_values(ascending=False).head(10)
    dash_sheet.write("A7","Top 10 2B Parties")
    for i,(name,val) in enumerate(top2b.items()):
        dash_sheet.write(i+8,0,name)
        dash_sheet.write(i+8,1,val)

    chart2 = workbook.add_chart({'type':'column'})
    chart2.add_series({
        'categories': f'=Dashboard!$A$9:$A${8+len(top2b)}',
        'values': f'=Dashboard!$B$9:$B${8+len(top2b)}'
    })
    dash_sheet.insert_chart('D15', chart2)

    # ---------------- TOP 10 PR ----------------
    toppr = df_pr.groupby("SUPPLIER NAME")["TAXABLE VALUE"].sum().sort_values(ascending=False).head(10)
    dash_sheet.write("F7","Top 10 PR Parties")
    for i,(name,val) in enumerate(toppr.items()):
        dash_sheet.write(i+8,5,name)
        dash_sheet.write(i+8,6,val)

    chart3 = workbook.add_chart({'type':'column'})
    chart3.add_series({
        'categories': f'=Dashboard!$F$9:$F${8+len(toppr)}',
        'values': f'=Dashboard!$G$9:$G${8+len(toppr)}'
    })
    dash_sheet.insert_chart('J15', chart3)

    workbook.close()

    st.download_button(
        "Download Full Reconciliation Report",
        output.getvalue(),
        "GST_Reconciliation_Report.xlsx"
    )

st.markdown("""
<hr>
<center>
Tool developed by <b>ABHISHEK JAKKULA</b><br>
GMAIL: jakkulaabhishek5@gmail.com
</center>
""", unsafe_allow_html=True)
