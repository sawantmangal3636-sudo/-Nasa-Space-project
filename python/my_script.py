# import os
# import pandas as pd
# import json

# #folder of current script
# current_dir = os.path.dirname(os.path.abspath(__file__))

# #csv path
# csv_path = os.path.join(current_dir, "..", "data","SB_publication_PMC.csv")

# #json path
# json_path = os.path.join(current_dir, "..", "data","publication.json")

# #read csv file
# csv_data = pd.read_csv("../data/SB_publication_PMC.csv")
# print("CSV Data:")
# print(csv_data.head())

# #read json
# with open(json_path, "r") as f:
#     json_data = json.load(f)
#     print("\nJSON Data")
#     print(json_data)

import os
import pandas as pd
import json

# folder of current script
current_dir = os.path.dirname(os.path.abspath(__file__))

# csv path (data folder is inside python/)
csv_path = os.path.join(current_dir, "data", "SB_publication_PMC.csv")

# json path (will also be inside data)
json_path = os.path.join(current_dir, "data", "publication.json")

# --- Read CSV ---
if os.path.exists(csv_path):
    csv_data = pd.read_csv(csv_path)
    print("✅ CSV Data:")
    print(csv_data.head())
else:
    print(f"❌ CSV not found at {csv_path}")

# --- Read JSON ---
if os.path.exists(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        json_data = json.load(f)
        print("\n✅ JSON Data:")
        print(json_data)
else:
    print(f"❌ JSON not found at {json_path}")
