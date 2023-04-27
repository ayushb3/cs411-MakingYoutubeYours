import pandas as pd
from mysql.connector import Error
import mysql.connector
import csv
import ast
from tqdm import tqdm


def connect():
    try:
        connection = mysql.connector.connect(
            host='35.193.136.209',
            database='YoutubeTrending',
            user='root',
            password='test1234')
        if connection.is_connected():
            print('Connected to MySQL database')
            return connection
    except Error as e:
        print(f'Error connecting to MySQL database: {e}')


connection = connect()
cursor = connection.cursor()

# Add the category_name column to the CategoryInfo table
cursor.execute("ALTER TABLE CategoryInfo ADD category_name VARCHAR(255)")

# Open the CSV file and read the data
with open('./sp23-cs411-team089-arys/data/categories.csv', 'r', encoding='utf-8') as csvfile:
    csvreader = csv.reader(csvfile)
    next(csvreader)  # skip the header row
    for row in csvreader:
        category_id = int(row[0])
        category_name = row[1]
        # Update the category_name column in the CategoryInfo table for the current category_id
        cursor.execute(
            "UPDATE CategoryInfo SET category_name = %s WHERE categoryId = %s", (category_name, category_id))

# Commit the changes and close the connection
connection.commit()


# Read data from the CSV file and insert it into the VideoInfo table
with open('./sp23-cs411-team089-arys/data/fixed_data.csv', 'r', encoding='utf-8') as csvfile:
    csvreader = csv.DictReader(csvfile)
    print('here')
    for row in csvreader:
        cursor.execute('''INSERT IGNORE  INTO VideoInfo
                     (video_id, title, publishedAt, tags, description, channelId, categoryId, view_count, likes, dislikes, comment_count, publishedAtDate)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                       (row['video_id'], row['title'], row['publishedAt'], row['tags'], row['description'], row['channelId'], row['categoryId'], row['view_count'], row['likes'], row['dislikes'], row['comment_count'], row['publishedAtDate']))

# Save changes to the database and close the connection
connection.commit()

# Read data from the CSV file and insert it into the Creators table
with open('./sp23-cs411-team089-arys/data/fixed_data.csv', 'r', encoding='utf-8') as csvfile:
    csvreader = csv.DictReader(csvfile)
    print('here')
    for row in csvreader:
        print(row)
        cursor.execute('''INSERT INTO Creators
                         (channelId, channelTitle, categoryId, video_id)
                         VALUES (%s, %s, %s, %s)
                         ON DUPLICATE KEY UPDATE
                         channelId = VALUES(channelId),
                         channelTitle = VALUES(channelTitle),
                         categoryId = VALUES(categoryId),
                         video_id = VALUES(video_id)''',
                       (row['channelId'], row['channelTitle'], row['categoryId'], row['video_id']))

# Save changes to the database and close the connection
connection.commit()


# Insert data into TrendingKeywords table
with open('./sp23-cs411-team089-arys/data/keywords.csv', 'r', encoding='utf-8') as csvfile:
    csvreader = csv.reader(csvfile)
    next(csvreader)  # skip header row
    for row in csvreader:
        keyword, use_count, _ = row
        # Use INSERT IGNORE to avoid errors when inserting duplicate rows
        query = "INSERT IGNORE INTO TrendingKeywords (keyword, use_count) VALUES (%s, %s)"
        values = (keyword, use_count)
        cursor.execute(query, values)
        if cursor.rowcount == 0:  # Check if the row was actually inserted
            print(
                f"Row already exists for keyword {keyword}. Skipping insertion.")
connection.commit()


# Insert data into KeywordVideoMap table
with open('./sp23-cs411-team089-arys/data/keywords.csv', 'r', encoding='utf-8') as csvfile:
    csvreader = csv.reader(csvfile)
    next(csvreader)  # skip header row
    for row in csvreader:
        keyword, _, category_ids = row
        # Check if keyword is present in VideoInfo.title
        cursor.execute(
            "SELECT video_id FROM VideoInfo WHERE MATCH (title) AGAINST (%s IN NATURAL LANGUAGE MODE)", (keyword,))
        video_ids = [row[0] for row in cursor.fetchall()]
        # Insert mappings into KeywordVideoMap table
        for video_id in video_ids:
            cursor.execute(
                "INSERT IGNORE INTO KeywordVideoMap (video_id, keyword) VALUES (%s, %s)", (video_id, keyword))
            if cursor.rowcount == 0:  # Check if the row was actually inserted
                print(
                    f"Row already exists for keyword {keyword}. Skipping insertion.")
connection.commit()

# Insert data into KeywordCategoryMap table
with open('./sp23-cs411-team089-arys/data/keywords.csv', 'r', encoding='utf-8') as csvfile:
    csvreader = csv.reader(csvfile)
    next(csvreader)  # skip header row
    for row in csvreader:
        keyword, _, category_ids = row
        category_ids = ast.literal_eval(category_ids)
        for category_id in category_ids:
            query = "INSERT IGNORE INTO KeywordCategoryMap (keyword, categoryId) " \
                    "VALUES (%s, %s) "
            values = (keyword, category_id)
            cursor.execute(query, values)
            if cursor.rowcount == 0:  # Check if the row was actually inserted
                print(
                    f"Row already exists for keyword {keyword}. Skipping insertion.")
connection.commit()

cursor.close()
connection.close()
