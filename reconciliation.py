import pandas as pd
import numpy as np

TOLERANCE = 20

def reconcile(file_2b, file_books):

    df_2b = pd.read_excel(file_2b)
    df_books = pd.read_excel(file_books)

    df_2b.columns = df_2b.columns.str.strip().str.upper()
    df_books.columns = df_books.columns.str.strip().str.upper()

    # Convert Taxable to numeric
    df_2b["TAXABLE VALUE"] = pd.to_numeric(df_2b["TAXABLE VALUE"], errors="coerce")
    df_books["TAXABLE VALUE"] = pd.to_numeric(df_books["TAXABLE VALUE"], errors="coerce")

    # Primary Key
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
            "EXACT MATCH (WITHIN ₹20 TOLERANCE)"
        ],
        default="INVOICE MATCH – VALUE MISMATCH"
    )

    matched_keys = primary_match["PRIMARY_KEY"]

    df_2b_unmatched = df_2b[~df_2b["PRIMARY_KEY"].isin(matched_keys)]
    df_books_unmatched = df_books[~df_books["PRIMARY_KEY"].isin(matched_keys)]

    # ---------------- SECONDARY MATCH ----------------
    secondary_matches = []

    for i, row_2b in df_2b_unmatched.iterrows():
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

            combined["MATCH STATUS"] = "MATCHED WITH TAXABLE VALUE (WITHIN ₹20 TOLERANCE)"
            secondary_matches.append(combined)

            df_books_unmatched = df_books_unmatched.drop(row_books.name)

    secondary_match_df = pd.DataFrame(secondary_matches)

    # ---------------- MISSING ----------------
    df_2b_unmatched = df_2b_unmatched.add_suffix("_2B")
    df_books_unmatched = df_books_unmatched.add_suffix("_BOOKS")

    df_2b_unmatched["MATCH STATUS"] = "MISSING IN BOOKS"
    df_books_unmatched["MATCH STATUS"] = "MISSING IN 2B"

    # ---------------- FINAL COMBINE ----------------
    final_df = pd.concat([
        primary_match,
        secondary_match_df,
        df_2b_unmatched,
        df_books_unmatched
    ], ignore_index=True)

    return final_df
