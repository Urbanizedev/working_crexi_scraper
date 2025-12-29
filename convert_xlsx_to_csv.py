import numpy as np
import pandas as pd
import os
# pip install openpyxl

# source folder with your .xlsx files, change as needed
xlsx_dir = r"C:\Users\sandr\Downloads\CrexiScrapeResults11172026"

# destination folder for converted CSVs, change as needed
csv_dir = os.path.join(xlsx_dir, "convertedCSV")
os.makedirs(csv_dir, exist_ok=True)

# loop through all .xlsx files in the source folder
for file in os.listdir(xlsx_dir):
    if file.endswith(".xlsx"):
        xlsx_path = os.path.join(xlsx_dir, file)
        csv_path = os.path.join(csv_dir, file.replace(".xlsx", ".csv"))

        # read and convert
        df = pd.read_excel(xlsx_path)
        df.to_csv(csv_path, index=False)
        print(f"Converted: {file} → {csv_path}")

# merge the CSVs
# destination of merged CSV, change as needed
merged_csv_path = os.path.join(xlsx_dir, "merged_results.csv")

all_dfs = []

for file in os.listdir(csv_dir):
    if file.endswith(".csv"):
        csv_path = os.path.join(csv_dir, file)
        # first 2 rows have nonsense, skip them to get to the header
        df = pd.read_csv(csv_path, skiprows=2)
        all_dfs.append(df)

# # merge and export
# merge_keys = [
#     "Property Link", "Property Name", "Property Status", "Type", "Address",
#     "City", "State", "Zip", "Tenant(s)", "Lease Term", "Remaining Term",
#     "SqFt", "Lot Size", "Units", "NOI", "Cap Rate", "Asking Price",
#     "Price/SqFt", "Price/Acre", "Days on Market", "Opportunity Zone",
#     "Longitude", "Latitude"
# ]
#
# if all_dfs:
#
#     # go through each df and add merge_keys columns if missing any. typically missing Lease Term and Remaining Term
#     for i, df in enumerate(all_dfs):
#         df.columns = df.columns.str.strip()
#         missing = [key for key in merge_keys if key not in df.columns]
#         if missing:
#             print(f"File {i} was missing columns: {missing}")
#         for key in merge_keys:
#             if key not in df.columns:
#                 df[key] = np.nan
#         all_dfs[i] = df
#
#     merged_df = all_dfs[0]
#     for df in all_dfs[1:]:
#         merged_df = pd.merge(
#             merged_df, df,
#             on=merge_keys,
#             how="outer"
#         )
#     merged_df.to_csv(merged_csv_path, index=False)
#     print(f"Merged {len(all_dfs)} CSVs into {merged_csv_path}")
# else:
#     print("No CSV files found to merge.")

# concatenate and export
merge_keys = [
    "Property Link", "Property Name", "Property Status", "Type", "Address",
    "City", "State", "Zip", "Tenant(s)", "Lease Term", "Remaining Term",
    "SqFt", "Lot Size", "Units", "NOI", "Cap Rate", "Asking Price",
    "Price/SqFt", "Price/Acre", "Days on Market", "Opportunity Zone",
    "Longitude", "Latitude"
]

if all_dfs:
    normalized_dfs = []

    # go through each df and add merge_keys columns if missing any. typically missing Lease Term and Remaining Term
    for i, df in enumerate(all_dfs):
        df.columns = df.columns.str.strip()
        missing = [key for key in merge_keys if key not in df.columns]

        if missing:
            print(f"File {i + 1} was missing columns: {missing}")
            for key in missing:
                df[key] = np.nan  # add missing columns

        df = df[[col for col in merge_keys if col in df.columns]]

        for key in merge_keys:
            if key not in df.columns:
                df[key] = np.nan

        df = df[merge_keys]
        normalized_dfs.append(df)


    merged_df = pd.concat(normalized_dfs, ignore_index=True)
    merged_df.to_csv(merged_csv_path, index=False)
    print(f"Concatenated {len(all_dfs)} CSVs into {merged_csv_path}")
else:
    print("No CSV files found to merge.")