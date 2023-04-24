import json
import pandas as pd

# Load the JSON file
with open('./sp23-cs411-team089-arys/data/US_category_id.json', 'r') as f:
    data = json.load(f)


# Extract the category ID and category name from the JSON data
categories = [(item['id'], item['snippet']['title']) for item in data['items']]

# Convert the data to a Pandas DataFrame
df = pd.DataFrame(categories, columns=['category_id', 'category_name'])

# View the resulting DataFrame
print(df)
