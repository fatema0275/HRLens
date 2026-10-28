import os
import glob
import pandas as pd

def find_dataset():
    """Locate the IBM HR Analytics dataset in the data folder."""
    candidates = [
        "data/WA_Fn-UseC_-HR-Employee-Attrition.csv",
        "data/ibm_hr_attrition.csv",
        "data/HR-Employee-Attrition.csv"
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
            
    csvs = glob.glob("data/*.csv")
    return csvs[0] if csvs else None

def main():
    filepath = find_dataset()
    if not filepath:
        print("Error: No CSV file found in data/ folder.")
        return

    print(f"--- Loading Dataset from: {filepath} ---")
    df = pd.read_csv(filepath)

    # 1. Total Number of Employees
    total_employees = len(df)
    print(f"\n[1] Total Number of Employees: {total_employees:,}")

    # 2. First 5 Rows
    print("\n[2] First 5 Rows:")
    print(df.head())

    # 3. Column Names
    print(f"\n[3] Column Names ({len(df.columns)} total):")
    for idx, col in enumerate(df.columns, 1):
        print(f"  {idx:2d}. {col} ({df[col].dtype})")

    # 4. Missing Values
    print("\n[4] Missing Values Check:")
    missing = df.isnull().sum()
    total_missing = missing.sum()
    print(f"  Total Missing Values across dataset: {total_missing}")
    if total_missing > 0:
        print(missing[missing > 0])
    else:
        print("  All columns have 0 missing values.")

    # 5. Basic Dataset Information
    print("\n[5] Basic Dataset Information (df.info()):")
    df.info()

if __name__ == "__main__":
    main()
