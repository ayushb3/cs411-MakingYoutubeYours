import mysql.connector
from mysql.connector import Error
import youtube_analysis


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


def insert_video(URL, connection):
    video_id = youtube_analysis.youtube_link_to_id(URL)
    channelId, channel_title, categoryId, video_id, title, publishedAt, tags, description, comment_count, view_count, likes, dislikes = youtube_analysis.extract_video_info(
        video_id)
    # tags is a list so convert to a string
    if type(tags) == list:
        tags = ', '.join(tags)
    # connect to DB
    cursor = connection.cursor()
    # insert video; if id already exists, update the values since this will be more up to date
    sql = "INSERT INTO VideoInfo (video_id, title, publishedAt, tags, description, channelId, categoryId, view_count, likes, dislikes, comment_count) \
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
            ON DUPLICATE KEY UPDATE \
                title = VALUES(title), \
                publishedAt = VALUES(publishedAt), \
                tags = VALUES(tags), \
                description = VALUES(description), \
                channelId = VALUES(channelId), \
                categoryId = VALUES(categoryId), \
                view_count = VALUES(view_count), \
                likes = VALUES(likes), \
                dislikes = VALUES(dislikes), \
                comment_count = VALUES(comment_count)"
    vals = (
        video_id,
        title,
        publishedAt,
        tags,
        description,
        channelId,
        categoryId,
        view_count,
        likes,
        dislikes,
        comment_count
    )
    cursor.execute(sql, vals)

    # check if the channelId exists in Creators table
    cursor.execute("SELECT 1 FROM Creators WHERE channelId = %s", (channelId,))
    result = cursor.fetchone()

    # if the channelId does not exist, insert it into Creators table
    if not result:
        cursor.execute("INSERT INTO Creators (channelId, channelTitle, categoryId, video_id) VALUES (%s, %s, %s, %s)",
                       (channelId, channel_title, categoryId, video_id))

    connection.commit()


def search_videos(connection):
    cursor = connection.cursor()

    search_term = input("Enter search term: ")

    sql = "SELECT title FROM VideoInfo WHERE MATCH (title) AGAINST (%s IN NATURAL LANGUAGE MODE)"
    vals = (f"'{search_term}'",)

    cursor.execute(sql, vals)
    results = cursor.fetchall()

    if len(results) == 0:
        return "No results found."
    return results


def insert_website_user(username, password, email, channel_title, connection):
    cursor = connection.cursor()

    # check if email already exists in WebsiteUsers table
    sql = "SELECT COUNT(*) FROM WebsiteUsers WHERE email = %s"
    vals = (email,)
    cursor.execute(sql, vals)
    result = cursor.fetchone()

    if result[0] > 0:
        print(f"Cannot insert user. Email already exists in the database.")
        return

    # check if channel_title exists in Creators table
    sql = "SELECT channelId FROM Creators WHERE channelTitle = %s"
    vals = (channel_title,)
    cursor.execute(sql, vals)
    results = cursor.fetchall()

    # if there are no results or multiple results, ask for a video link to identify the correct channelId
    if not results:
        video_link = input(
            f"No unique channelId found for {channel_title}. Please provide a video link to identify the correct channel: ")
        insert_video(video_link, connection)
        video_id = youtube_analysis.youtube_link_to_id(video_link)
        info = youtube_analysis.extract_video_info(video_id)
        channel_id = info[0]

    elif len(results) > 1:
        video_link = input(
            f"No unique channelId found for {channel_title}. Please provide a video link to identify the correct channel: ")
        video_id = youtube_analysis.youtube_link_to_id(video_link)
        sql = "SELECT channelId FROM Creators WHERE channelTitle = %s AND video_id = %s"
        vals = (channel_title, video_id)
        cursor.execute(sql, vals)
        results = cursor.fetchall()
        # get the channelId from the results
        channel_id = results[0][0]
    else:
        channel_id = results[0][0]

    # insert the website user
    sql = "INSERT INTO WebsiteUsers (username, password, email, channelId) VALUES (%s, %s, %s, %s)"
    vals = (username, password, email, channel_id)
    cursor.execute(sql, vals)

    connection.commit()


def update_website_user(current_username, current_password, connection, new_username=None, new_password=None, new_email=None):
    cursor = connection.cursor()
    sql = "SELECT user_id, username, password, email, channelId FROM WebsiteUsers WHERE username = %s AND password = %s"
    cursor.execute(sql, (current_username, current_password))
    result = cursor.fetchone()

    if result is None:
        print(f"No user found with this username and password combination")
        return

    user_id, username, password, email, channelId = result

    if new_username:
        username = new_username
    if new_password:
        password = new_password
    if new_email:
        email = new_email

    # Only update if at least one new value was provided
    if new_username or new_password or new_email:
        sql = "UPDATE WebsiteUsers SET username = %s, password = %s, email = %s, channelId = %s WHERE user_id = %s"
        vals = (username, password, email, channelId, user_id)
        cursor.execute(sql, vals)
        connection.commit()
        print("Successfully updated user")
    else:
        print("No new values provided for update")


def delete_website_user(username, password, connection):
    cursor = connection.cursor()

    # Check if user exists
    sql = "SELECT user_id FROM WebsiteUsers WHERE username = %s AND password = %s"
    cursor.execute(sql, (username, password))
    result = cursor.fetchone()

    if result is None:
        print("No user found with this username and password combination")
        return
    user_id = result[0]
    # Delete user
    sql = "DELETE FROM WebsiteUsers WHERE user_id = %s"
    cursor.execute(sql, (user_id,))
    connection.commit()

    print("Successfully deleted user")


def check_video_exists(video_id, connection):
    cursor = connection.cursor()
    sql = "SELECT 1 FROM VideoInfo WHERE video_id = %s"
    cursor.execute(sql, (video_id,))
    result = cursor.fetchone()
    return result is not None


def main():
    # Connect to the MySQL database
    connection = connect()

    # Insert a video into the database
    video_link = input("Enter a YouTube video link: ")
    insert_video(video_link, connection)
    print("Video info has been inserted into the database.")

    # Search for videos in the database
    results = search_videos(connection)
    print(f"Search Results: {results}")

    # Insert a website user into the database
    username = input("Enter a username: ")
    password = input("Enter a password: ")
    email = input("Enter an email address: ")
    channel_title = input("Enter the title of the YouTube channel: ")
    insert_website_user(username, password, email, channel_title, connection)
    print("Website user has been inserted into the database.")

    # Update a website user in the database
    current_username = input("Enter the current username: ")
    current_password = input("Enter the current password: ")
    new_username = input(
        "Enter a new username (leave blank to keep current): ")
    new_password = input(
        "Enter a new password (leave blank to keep current): ")
    new_email = input(
        "Enter a new email address (leave blank to keep current): ")
    update_website_user(current_username, current_password,
                        connection, new_username, new_password, new_email)
    print("Website user has been updated in the database.")

    # Close the database connection
    connection.close()


main()
