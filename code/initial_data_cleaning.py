import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

# This part is used to clean duplicate entries in the initial dataset

# load the downloaded dataset into a Pandas dataframe
df = pd.read_csv('data/US_youtube_trending_data.csv')
# drop any duplicate videos keeping the entry with the highest view_count
# this should be the most recent entry which is most useful to our project
dropped = df.sort_values(
    'view_count', ascending=False).drop_duplicates('video_id')
# convert to cleaned dataset to a csv file which we can import into GCP
dropped.to_csv('data/fixed_data.csv', index=False)
