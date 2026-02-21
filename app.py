import streamlit as st
import pandas as pd
import numpy as np
import io
import plotly.express as px

TOLERANCE = 20

# ---------------- SaaS UI ----------------
st.set_page_config(page_title="GST Reconciliation SaaS", layout="wide")

st.markdown("""
<style>
body {background-color: #f4f6f9;}
.main {background-color: #f4f6f9;}
.stMetric {background-color: white; padding:15px; border-radius:10px;}
</style>
""", unsafe_allow_html=True)

st.title("🚀 GST 2B vs Books – Reconciliation SaaS Platform")
st.caption("Professional Automated GST Matching Engine")

# ---------------- Upload ----------------
col1, col2 = st.columns(2)
file_2b = col1.file_uploader("Upload GSTR-2B Excel", type=["xlsx"])
file_pr = col2.file_uploader("Upload Purchase Register Excel", type=["xlsx"])

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
            "Taxable (2B)": taxable_2b,
            "Taxable (PR)": taxable_pr,
            "Difference": taxable_2b - taxable_pr,
            "IGST (2B)": row.get("IGST (2B)",0),
            "IGST (PR)": row.get("IGST (PR)",0),
            "CGST (2B)": row.get("CGST (2B)",0),
            "CGST (PR)": row.get("CGST (PR)",0),
            "SGST (2B)": row.get("SGST (2B)",0),
            "SGST (PR)": row.get("SGST (PR)",0),
        })

    recon_df = pd.DataFrame(records)

    # ---------------- KPI Tiles ----------------
    total = len(recon_df)
    exact = len(recon_df[recon_df["Match Status"].str.contains("Exact")])
    mismatch = len(recon_df[recon_df["Match Status"]=="Value Mismatch"])
    missing = len(recon_df[recon_df["Match Status"].str.contains("Missing")])

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Total Records", total)
    c2.metric("Exact %", f"{round((exact/total)*100,2) if total else 0}%")
    c3.metric("Mismatch %", f"{round((mismatch/total)*100,2) if total else 0}%")
    c4.metric("Missing %", f"{round((missing/total)*100,2) if total else 0}%")

    st.divider()

    # ---------------- Charts ----------------
    chart1 = px.pie(recon_df, names="Match Status", title="Matching Status Distribution")
    st.plotly_chart(chart1, use_container_width=True)

    top_2b = df_2b.groupby("SUPPLIER NAME")["TAXABLE VALUE"].sum().sort_values(ascending=False).head(10)
    fig2 = px.bar(top_2b, title="Top 10 Vendors - 2B")
    st.plotly_chart(fig2, use_container_width=True)

    top_pr = df_pr.groupby("SUPPLIER NAME")["TAXABLE VALUE"].sum().sort_values(ascending=False).head(10)
    fig3 = px.bar(top_pr, title="Top 10 Vendors - Purchase Register")
    st.plotly_chart(fig3, use_container_width=True)

    st.divider()
    st.subheader("Reconciliation Table")
    st.dataframe(recon_df, use_container_width=True)

    # ---------------- Excel Export ----------------
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        recon_df.to_excel(writer, sheet_name="Reconciliation", index=False)
        df_2b.to_excel(writer, sheet_name="2B Data", index=False)
        df_pr.to_excel(writer, sheet_name="Purchase Data", index=False)

    st.download_button("⬇ Download Final SaaS Report",
                       output.getvalue(),
                       "GST_Reconciliation_SaaS.xlsx")

st.markdown("""
<hr>
<center>
<b>Developed by ABHISHEK JAKKULA</b><br>
jakkulaabhishek5@gmail.com
</center>
""", unsafe_allow_html=True)
