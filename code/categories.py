import json
import pandas as pd

# Load the JSON file
with open('./sp23-cs411-team089-arys/data/US_category_id.json', 'r') as f:
    data = json.load(f)


# Extract the category ID and category name from the JSON data
categories = [(item['id'], item['snippet']['title']) for item in data['items']]

# Convert the data to a Pandas DataFrame
categories_df = pd.DataFrame(
    categories, columns=['category_id', 'category_name'])

# Write the DataFrame to a new CSV file
categories_df.to_csv(
    './sp23-cs411-team089-arys/data/categories.csv', index=False)
