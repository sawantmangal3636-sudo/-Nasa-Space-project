import os
import pandas as pd
import json

#folder of current script
current_dir = os.path.dirname(os.path.abspath(__file__))

#csv path
csv_path = os.path.join(current_dir, "..", "data","SB_publication_PMC.csv")

#json path
json_path = os.path.join(current_dir, "..", "data","publication.json")

#read csv file
csv_data = pd.read_csv("../data/SB_publication_PMC.csv")
print("CSV Data:")
print(csv_data.head())

#read json
with open(json_path, "r") as f:
    json_data = json.load(f)
    print("\nJSON Data")
    print(json_data)