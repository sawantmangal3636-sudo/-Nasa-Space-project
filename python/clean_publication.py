import os
import pandas as pd
import re
import subprocess


#  CLEAN DATA
url = "https://raw.githubusercontent.com/jgalazka/SB_publications/refs/heads/main/SB_publication_PMC.csv"
df = pd.read_csv(url)

df.drop_duplicates(inplace=True)
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

# Example
def extract_year(text):
    match = re.search(r"(19|20)\d{2}", str(text))
    return int(match.group()) if match else None
df["year"] = df["title"].apply(extract_year)

df.to_csv("cleaned_publications.csv", index=False)
print(" Cleaned data saved")


# AUTO-REFRESH POWER BI
# Path to your PBIX file
pbix_file = r"D:\HackNASA_Dashboard.pbix"

# Path to Power BI Desktop executable 
powerbi_exe = r"C:\Program Files\Microsoft Power BI Desktop\bin\PBIDesktop.exe"

# Power BI open your report
subprocess.Popen([powerbi_exe, pbix_file])

