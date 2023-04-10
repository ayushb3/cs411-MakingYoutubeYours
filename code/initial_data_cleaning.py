import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

#This part is used to clean duplicate entries in the initial dataset

#load the downloaded dataset into a Pandas dataframe
df = pd.read_csv('data/US_youtube_trending_data.csv')
#drop any duplicate videos keeping the entry with the highest view_count
#this should be the most recent entry which is most useful to our project
dropped = df.sort_values('view_count', ascending=False).drop_duplicates('video_id')
#convert to cleaned dataset to a csv file which we can import into GCP
dropped.to_csv('data/fixed_data.csv', index=False)

#This part is to populate keywords based on the most commonly used words from the titles of all the videos

# load the CSV file into a pandas DataFrame
df = pd.read_csv("data/fixed_data.csv")

# extract the text data from the DataFrame
docs = df["title"].dropna().tolist()

# create a TF-IDF vectorizer object
vectorizer = TfidfVectorizer()

# fit the vectorizer to the documents
vectorizer.fit(docs)

# transform the documents into a TF-IDF matrix
tfidf_matrix = vectorizer.transform(docs)

# convert the TF-IDF matrix into a pandas DataFrame
df_tfidf = pd.DataFrame(tfidf_matrix.toarray(), columns=vectorizer.get_feature_names_out())
df_tfidf.to_csv('data/keywords.csv')
