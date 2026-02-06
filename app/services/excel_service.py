import pandas as pd
import os

HEADERS = [
    "Name",
    "Email",
    "Mobile",
    "Skills",
    "Education",
    "Certifications",
    "Experience",
    "Publications",
    "Awards",
]
COLUMNS = HEADERS
def clean_cell(value):
    if value is None:
        return ""
    v = str(value).strip()
    return "" if v.lower() == "nan" else v

def append_row(row, output_path):
    # force row to match schema exactly
    clean_row = {col: clean_cell(row.get(col, "")) for col in COLUMNS}
    df_new = pd.DataFrame([clean_row], columns=COLUMNS)

    if os.path.exists(output_path):
        df_existing = pd.read_excel(output_path)

        # align existing data to schema (VERY IMPORTANT)
        df_existing = df_existing.reindex(columns=COLUMNS, fill_value="")

        df_final = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_final = df_new

    df_final.to_excel(output_path, index=False)
    return df_final

