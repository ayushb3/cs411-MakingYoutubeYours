import pandas as pd

# This part is used to clean duplicate entries in the initial dataset

# load the downloaded dataset into a Pandas dataframe
df = pd.read_csv('./sp23-cs411-team089-arys/data/US_youtube_trending_data.csv')

# convert the 'publishedAt' column to a pandas datetime object
df['publishedAt'] = pd.to_datetime(df['publishedAt'])

# extract the date portion of the datetime object
df['publishedAtDate'] = df['publishedAt'].dt.date

# drop any duplicate videos keeping the entry with the highest view_count
# this should be the most recent entry which is most useful to our project
dropped = df.sort_values(
    'view_count', ascending=False).drop_duplicates('video_id')
# convert to cleaned dataset to a csv file which we can import into GCP
dropped.to_csv('./sp23-cs411-team089-arys/data/fixed_data.csv', index=False)
