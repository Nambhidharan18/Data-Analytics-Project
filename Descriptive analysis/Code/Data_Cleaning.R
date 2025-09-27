# Load required libraries
library(tidyverse)
library(dplyr)
library(lubridate)

# Step 1: Load dataset
sales_raw <- read.csv("sales_data_sample.csv", stringsAsFactors = FALSE)

# Step 2: Check for duplicates
# Use ORDERNUMBER + ORDERLINENUMBER as composite key
sales_raw <- sales_raw %>%
  mutate(dup_key = paste0(ORDERNUMBER, "_", ORDERLINENUMBER))

dup_count <- sum(duplicated(sales_raw$dup_key))
cat("Number of duplicates found:", dup_count, "\n")

# Remove duplicates if any
sales_nodup <- sales_raw %>% distinct(dup_key, .keep_all = TRUE)

# Step 3: Check SALES integrity (SALES vs QUANTITYORDERED * PRICEEACH)
sales_nodup <- sales_nodup %>%
  mutate(calculated_sales = QUANTITYORDERED * PRICEEACH,
         sales_match = ifelse(round(SALES, 2) == round(calculated_sales, 2), TRUE, FALSE))

cat("Number of mismatched sales rows:", sum(!sales_nodup$sales_match), "\n")

# Step 4: Check YEAR_ID, MONTH_ID, QTR_ID integrity against ORDERDATE
# Convert ORDERDATE to a proper Date format
# Try a different format if the first one fails
sales_nodup$ORDERDATE <- lubridate::mdy(sales_nodup$ORDERDATE)

# Check for a different date format if the first one resulted in NAs
if (sum(is.na(sales_nodup$ORDERDATE)) > 0) {
  sales_nodup$ORDERDATE <- lubridate::dmy(sales_nodup$ORDERDATE)
}

# Extract year, month, quarter from ORDERDATE
sales_nodup <- sales_nodup %>%
  mutate(year_check = year(ORDERDATE),
         month_check = month(ORDERDATE),
         qtr_check = quarter(ORDERDATE))

# Compare with dataset fields, handling NAs
cat("YEAR mismatches:", sum(sales_nodup$year_check != sales_nodup$YEAR_ID, na.rm = TRUE), "\n")
cat("MONTH mismatches:", sum(sales_nodup$month_check != sales_nodup$MONTH_ID, na.rm = TRUE), "\n")
cat("QTR mismatches:", sum(sales_nodup$qtr_check != sales_nodup$QTR_ID, na.rm = TRUE), "\n")

# Step 5: Check for missing values
missing_summary <- colSums(is.na(sales_nodup))
print(missing_summary)

# Step 6: Check for negative or zero values in numeric fields
neg_sales <- sum(sales_nodup$SALES < 0)
neg_qty <- sum(sales_nodup$QUANTITYORDERED <= 0)
neg_price <- sum(sales_nodup$PRICEEACH <= 0)

cat("Negative sales:", neg_sales, "\n")
cat("Zero/negative quantities:", neg_qty, "\n")
cat("Zero/negative prices:", neg_price, "\n")

# Step 7: Standardize STATUS values (capitalize first letter only)
sales_nodup$STATUS <- tolower(sales_nodup$STATUS)
sales_nodup$STATUS <- tools::toTitleCase(sales_nodup$STATUS)

# Step 8: Select only required columns (final cleaned dataset)

# Overwrite SALES with calculated_sales to ensure consistency
sales_nodup$SALES <- sales_nodup$calculated_sales

sales_cleaned <- sales_nodup %>%
  select(SALES, STATUS, QUANTITYORDERED, QTR_ID, MONTH_ID, 
         YEAR_ID, PRODUCTLINE, COUNTRY, DEALSIZE)


# Step 9: Save cleaned dataset
write.csv(sales_cleaned, "sales_data_cleaned.csv", row.names = FALSE)

cat("Cleaned dataset saved as sales_data_cleaned.csv\n")



