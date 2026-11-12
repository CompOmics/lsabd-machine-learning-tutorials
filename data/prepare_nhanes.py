"""
Build the NHANES 2017-2018 table used in notebook 4.

The National Health and Nutrition Examination Survey (NHANES) is a program of the National Center
for Health Statistics (NCHS), part of the US Centers for Disease Control and Prevention (CDC). It
combines interviews, physical examinations and laboratory tests of a representative sample of the
US population. The data are in the public domain.

Source: Centers for Disease Control and Prevention (CDC), National Center for Health Statistics
(NCHS). National Health and Nutrition Examination Survey Data, 2017-2018. Hyattsville, MD: U.S.
Department of Health and Human Services. https://wwwn.cdc.gov/nchs/nhanes/

This script downloads a selection of 2017-2018 data files, merges them on the respondent sequence
number (``SEQN``) and keeps a subset of columns with their original NHANES names and codes. Values
are not cleaned, so that special codes (e.g., 7777 for "refused") and missing values remain as in
the original data. The only change is that values smaller than 1e-10, which are an artifact of the
SAS transport format for zero, are set to exactly zero.

Usage: ``uv run python data/prepare_nhanes.py``
"""

from functools import reduce
from pathlib import Path

import pandas as pd

BASE_URL = "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/{}.xpt"

COLUMNS = {
    "DEMO_J": ["SEQN", "RIDAGEYR", "RIAGENDR", "RIDRETH3", "DMDEDUC2", "INDFMPIR"],
    "BMX_J": ["SEQN", "BMXWT", "BMXHT", "BMXBMI", "BMXWAIST"],
    "BPX_J": [
        "SEQN", "BPXPLS", "BPXSY1", "BPXSY2", "BPXSY3", "BPXDI1", "BPXDI2", "BPXDI3",
    ],
    "BPQ_J": ["SEQN", "BPQ020", "BPQ050A"],
    "TCHOL_J": ["SEQN", "LBXTC"],
    "GHB_J": ["SEQN", "LBXGH"],
    "PAQ_J": ["SEQN", "PAD680"],
    "SMQ_J": ["SEQN", "SMQ020"],
}

OUTPUT_FILE = Path(__file__).parent / "nhanes_2017_2018.csv"


def load_module(name):
    """Download one NHANES data file and keep the selected columns."""
    table = pd.read_sas(BASE_URL.format(name), format="xport")
    return table[COLUMNS[name]]


def main():
    """Download, merge, and save the NHANES table."""
    tables = [load_module(name) for name in COLUMNS]
    # Demographics (first table) contains all respondents; left-merge the others onto it
    merged = reduce(lambda left, right: left.merge(right, on="SEQN", how="left"), tables)
    numeric_columns = merged.select_dtypes("number").columns
    merged[numeric_columns] = merged[numeric_columns].mask(merged[numeric_columns].abs() < 1e-10, 0)
    merged["SEQN"] = merged["SEQN"].astype(int)
    merged.to_csv(OUTPUT_FILE, index=False)
    print(f"Saved {merged.shape[0]} rows and {merged.shape[1]} columns to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
