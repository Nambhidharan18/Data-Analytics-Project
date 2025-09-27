# Load required libraries
import pandas as pd
import numpy as np

# Step 1: Load dataset

# Note: Using 'latin1' encoding to avoid UnicodeDecodeError
sales_raw = pd.read_csv("sales_data_sample.csv", encoding="latin1")


# Step 2: Check for duplicates

# Create a composite key using ORDERNUMBER + ORDERLINENUMBER
sales_raw["dup_key"] = (
    sales_raw["ORDERNUMBER"].astype(str) + "_" + sales_raw["ORDERLINENUMBER"].astype(str)
)

# Count duplicates
dup_count = sales_raw.duplicated(subset=["dup_key"]).sum()
print("Number of duplicates found:", dup_count)

# Remove duplicates (keep the first occurrence)
sales_nodup = sales_raw.drop_duplicates(subset=["dup_key"], keep="first")


# Step 3: Check for negative or zero values

neg_sales = (sales_nodup["SALES"] <= 0).sum()
neg_price = (sales_nodup["PRICEEACH"] <= 0).sum()
neg_qty = (sales_nodup["QUANTITYORDERED"] <= 0).sum()

print("Negative or Zero values in Sales:", neg_sales)
print("Negative or Zero values in Price:", neg_price)
print("Negative or Zero values in Quantity Ordered:", neg_qty)


# Step 4: Check SALES integrity

# Compare SALES with QUANTITYORDERED * PRICEEACH
sales_nodup["calculated_sales"] = (
    sales_nodup["QUANTITYORDERED"] * sales_nodup["PRICEEACH"]
)

sales_nodup["sales_match"] = np.isclose(
    sales_nodup["SALES"], sales_nodup["calculated_sales"], atol=0.01
)


# Count mismatches
no_mismatch = (~sales_nodup["sales_match"]).sum()
print("Number of mismatched sales rows:", no_mismatch)

# Print mismatches side by side (for review)
if no_mismatch > 0:
    mismatches = sales_nodup.loc[
        ~sales_nodup["sales_match"],
        ["SALES", "calculated_sales", "QUANTITYORDERED", "PRICEEACH"],
    ]
    print("\nMismatched sales (side by side):")
    print(mismatches)


# Step 5: Validate YEAR_ID, MONTH_ID, QTR_ID

# Try parsing ORDERDATE in different formats
try:
    sales_nodup["ORDERDATE"] = pd.to_datetime(
        sales_nodup["ORDERDATE"], format="%m/%d/%Y", errors="coerce"
    )
except:
    sales_nodup["ORDERDATE"] = pd.to_datetime(
        sales_nodup["ORDERDATE"], format="%d/%m/%Y", errors="coerce"
    )

# Extract year, month, and quarter from parsed date
sales_nodup["year_check"] = sales_nodup["ORDERDATE"].dt.year
sales_nodup["month_check"] = sales_nodup["ORDERDATE"].dt.month
sales_nodup["quarter_check"] = sales_nodup["ORDERDATE"].dt.quarter

# Compare extracted values with dataset fields
print(
    "Year mismatches:",
    (sales_nodup["year_check"].astype("Int64") != sales_nodup["YEAR_ID"]).sum(skipna=True),
)
print(
    "Month mismatches:",
    (sales_nodup["month_check"].astype("Int64") != sales_nodup["MONTH_ID"]).sum(skipna=True),
)
print(
    "Quarter mismatches:",
    (sales_nodup["quarter_check"].astype("Int64") != sales_nodup["QTR_ID"]).sum(skipna=True),
)

# Step 6: Missing values summary

missing_summary = sales_nodup.isna().sum()
print("\nMissing Values Summary:\n", missing_summary)

# Step 7: Standardize STATUS values

# Convert to lowercase, then capitalize first letter
sales_nodup["STATUS"] = sales_nodup["STATUS"].str.lower().str.title()

# Step 8: Select required columns (final cleaned dataset)

# Overwrite SALES with calculated_sales to ensure consistency
sales_nodup["SALES"] = sales_nodup["calculated_sales"]

# Keep only the relevant columns (same order as R script)
sales_cleaned = sales_nodup[
    [
        "SALES",
        "STATUS",
        "QUANTITYORDERED",
        "QTR_ID",
        "MONTH_ID",
        "YEAR_ID",
        "PRODUCTLINE",
        "COUNTRY",
        "DEALSIZE",
    ]
]


# Step 9: Save cleaned dataset

sales_cleaned.to_csv("sales_data_cleaned.csv", index=False)
print("\n✅ Cleaned dataset saved as 'sales_data_cleaned.csv'")
