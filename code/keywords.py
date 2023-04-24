import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string
import re


nltk.download('stopwords')

df = pd.read_csv('./sp23-cs411-team089-arys/data/fixed_data.csv')

# Preprocess the titles


def preprocess(title):
    # Remove non-alphanumeric characters and lowercase
    title = re.sub(r'[^\w\s]', '', title).lower()
    # Tokenize
    tokens = word_tokenize(title)
    # Remove stop words and numbers
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [token for token in tokens if token not in stop_words and not token.isnumeric()]
    # Convert to string and return
    processed_string = ' '.join(filtered_tokens)
    return processed_string



df['title'] = df['title'].apply(preprocess)

# Remove special characters using regex
df['title'] = df['title'].apply(lambda x: re.sub(r'[^\w\s]', '', x))

# Calculate the mean view_count and likes
mean_view_count = df['view_count'].mean()

# Create a dictionary to store the frequency of each keyword along with its category_id
keyword_freq_dict = {}
for index, row in df[df['view_count'] > mean_view_count].iterrows():
    category_id = row['categoryId']
    title = row['title']
    keywords = word_tokenize(title)
    for keyword in keywords:
        # If keyword exists, already increment freq
        if keyword in keyword_freq_dict:
            keyword_freq_dict[keyword]['frequency'] += 1
            # If keyword exists, but categoryId not associated, add it
            if category_id not in keyword_freq_dict[keyword]['category_ids']:
                keyword_freq_dict[keyword]['category_ids'].append(category_id)
        # Otherwise, add keyword
        else:
            keyword_freq_dict[keyword] = {
                'frequency': 1, 'category_ids': [category_id]}

# Make df from dictionary
keywords_df = pd.DataFrame.from_dict(keyword_freq_dict, orient='index')
keywords_df.reset_index(inplace=True)
keywords_df.rename(columns={'index': 'Keyword'}, inplace=True)
keywords_df = keywords_df[['Keyword', 'frequency', 'category_ids']]

# Sort the DataFrame by frequency in descending order
keywords_df = keywords_df.sort_values('frequency', ascending=False)

# Write the DataFrame to a new CSV file
keywords_df.to_csv('./sp23-cs411-team089-arys/data/keywords.csv', index=False)
