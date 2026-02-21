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

    df_2b["DOCUMENT DATE"] = pd.to_datetime(df_2b["DOCUMENT DATE"], errors="coerce")
    df_pr["DOCUMENT DATE"] = pd.to_datetime(df_pr["DOCUMENT DATE"], errors="coerce")

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
            "Supplier GSTIN (2B)": row.get("SUPPLIER GSTIN (2B)", ""),
            "Supplier GSTIN (PR)": row.get("SUPPLIER GSTIN (PR)", ""),
            "My GSTIN (2B)": row.get("MY GSTIN (2B)", ""),
            "My GSTIN (PR)": row.get("MY GSTIN (PR)", ""),
            "Document Number (2B)": row.get("DOCUMENT NUMBER (2B)", ""),
            "Document Number (PR)": row.get("DOCUMENT NUMBER (PR)", ""),
            "Document Date (2B)": str(row.get("DOCUMENT DATE (2B)", "")),
            "Document Date (PR)": str(row.get("DOCUMENT DATE (PR)", "")),
            "Taxable Value (2B)": taxable_2b,
            "Taxable Value (PR)": taxable_pr,
            "Tax Difference (2B-PR)": taxable_2b - taxable_pr,
            "Total Tax (2B)": tax_2b,
            "Total Tax (PR)": tax_pr,
            "IGST (2B)": row.get("IGST (2B)",0),
            "IGST (PR)": row.get("IGST (PR)",0),
            "CGST (2B)": row.get("CGST (2B)",0),
            "CGST (PR)": row.get("CGST (PR)",0),
            "SGST (2B)": row.get("SGST (2B)",0),
            "SGST (PR)": row.get("SGST (PR)",0),
        })

    final_df = pd.DataFrame(output_rows).fillna("")

    st.success("Reconciliation Completed")
    st.dataframe(final_df)

    # ---------------- EXCEL GENERATION ----------------
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet("Reconciliation")
    dashboard = workbook.add_worksheet("Dashboard")

    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#D9E1F2',
        'border':1
    })

    # Write data
    for col_num, value in enumerate(final_df.columns.values):
        worksheet.write(0, col_num, value, header_format)
        worksheet.set_column(col_num, col_num, 18)

    for row_num, row_data in enumerate(final_df.values):
        for col_num, cell_data in enumerate(row_data):
            worksheet.write(row_num+1, col_num, str(cell_data))

    # ---------------- DASHBOARD ----------------
    status_counts = final_df["Match Status"].value_counts().reset_index()
    status_counts.columns = ["Status", "Count"]

    dashboard.write_row("A1", ["Status","Count"], header_format)
    for i, row in status_counts.iterrows():
        dashboard.write_row(i+1, 0, row.values)

    chart = workbook.add_chart({'type': 'pie'})
    chart.add_series({
        'categories': f"=Dashboard!$A$2:$A${len(status_counts)+1}",
        'values':     f"=Dashboard!$B$2:$B${len(status_counts)+1}",
        'data_labels': {'percentage': True}
    })
    chart.set_title({'name': 'Match Status Distribution'})
    dashboard.insert_chart('D2', chart)

    workbook.close()

    st.download_button(
        "Download Final Reconciliation Report",
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
