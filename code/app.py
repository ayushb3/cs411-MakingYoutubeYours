import youtube_analysis
from mysql.connector import Error
import mysql.connector
from flask import Flask, render_template, request, redirect, session
import sys
import logging
import secrets
import cohere
import random
import pandas as pd

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)


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


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/index.html')
def index1():
    return render_template('index.html')


@app.route('/form.html')
def form():
    return render_template('form.html')


# Insert video data into VideoInfo table
@app.route('/insert_video.html', methods=['GET', 'POST'])
def insert():
    if request.method == 'POST':
        URL = request.form['URL']
        connection = connect()
        is_existing, new_creator_added = insert_video(URL, connection)
        if is_existing:
            return 'Video already exists in database'
        elif new_creator_added:
            return 'Video added to new creator in database'
        else:
            return 'Video added to existing creator in database'
    else:
        return render_template('insert_video.html')

# inserts a video based on a Youtube link
# returns whether or not the video already existed or if a new creator was added


def insert_video(URL, connection):
    video_id = youtube_analysis.youtube_link_to_id(URL)
    channelId, channel_title, categoryId, video_id, title, publishedAt, tags, description, comment_count, view_count, likes, dislikes = youtube_analysis.extract_video_info(
        video_id)
    # tags is a list so convert to a string
    if type(tags) == list:
        tags = ', '.join(tags)
    # connect to DB
    cursor = connection.cursor()

    # adding functionality to return whether the video already existed or a new creator was added
    video_exists = False
    new_creator_added = False

    sql = "SELECT COUNT(*) FROM VideoInfo WHERE video_id = %s"
    vals = (video_id,)
    cursor.execute(sql, vals)
    count = cursor.fetchone()[0]
    if count > 0:
        video_exists = True

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
    print('hello')
    # check if the channelId exists in Creators table
    cursor.execute("SELECT 1 FROM Creators WHERE channelId = %s", (channelId,))
    result = cursor.fetchone()

    # if the channelId does not exist, insert it into Creators table
    if not result:
        cursor.execute("INSERT INTO Creators (channelId, channelTitle, categoryId, video_id) VALUES (%s, %s, %s, %s)",
                       (channelId, channel_title, categoryId, video_id))
        new_creator_added = True
    connection.commit()
    return video_exists, new_creator_added

# Search for videos in VideoInfo table based on search term


@app.route('/search.html', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_term = request.form['search_term']
        connection = connect()
        results = search_videos(search_term, connection)
        return render_template('search.html', results=results)
    else:
        return render_template('search.html')


def search_videos(search_term, connection):
    cursor = connection.cursor()

    sql = "SELECT title FROM VideoInfo WHERE MATCH (title) AGAINST (%s IN NATURAL LANGUAGE MODE)"
    vals = (f"'{search_term}'",)

    cursor.execute(sql, vals)
    results = cursor.fetchall()

    if len(results) == 0:
        return
    return results


@app.route('/insert_user.html', methods=['GET', 'POST'])
def insert_user():
    app.logger.info('INSIDE INSERT USER')
    if request.method == 'POST':
        username = request.form['name']
        password = request.form['password']
        email = request.form['email']
        channel_title = request.form['channel_title']
        connection = connect()
        app.logger.info('HERE1')

        result = insert_website_user(
            username, password, email, channel_title, connection)
        app.logger.info('HERE2')

        if result == "Succesfully inserted user.":
            return result
        elif result == "I need a video link.":
            app.logger.info('HERE3')
            session['name'] = request.form['name']
            session['password'] = request.form['password']
            session['email'] = request.form['email']
            return redirect('/insert_user_with_video_link.html')
    else:
        return render_template('insert_user.html')


def insert_website_user(username, password, email, channel_title, connection):
    cursor = connection.cursor()

    # check if email already exists in WebsiteUsers table
    sql = "SELECT COUNT(*) FROM WebsiteUsers WHERE email = %s"
    vals = (email,)
    cursor.execute(sql, vals)
    result = cursor.fetchone()

    if result[0] > 0:
        return (f"Cannot insert user. Email already exists in the database.")

    # check if channel_title exists in Creators table
    sql = "SELECT channelId FROM Creators WHERE channelTitle = %s"
    vals = (channel_title,)
    cursor.execute(sql, vals)
    results = cursor.fetchall()
    print('here3')
    # if there are no results or multiple results, ask for a video link to identify the correct channelId
    if not results or len(results) > 1:
        print('here4')
        return "I need a video link."
    else:
        channel_id = results[0][0]

    # insert the website user
    sql = "INSERT INTO WebsiteUsers (username, password, email, channelId) VALUES (%s, %s, %s, %s)"
    vals = (username, password, email, channel_id)
    cursor.execute(sql, vals)

    connection.commit()
    return "Successfully inserted user."


@app.route('/insert_user_with_video_link.html', methods=['GET', 'POST'])
def insert_user_with_video_link():
    print('here4')

    username = session.get('name')
    password = session.get('password')
    email = session.get('email')
    if request.method == 'POST':
        video_link = request.form['video_link']
        connection = connect()
        channel_id = get_channel_id(video_link, connection)
        # insert the website user
        cursor = connection.cursor()
        sql = "INSERT INTO WebsiteUsers (username, password, email, channelId) VALUES (%s, %s, %s, %s)"
        vals = (username, password, email, channel_id)
        cursor.execute(sql, vals)

        connection.commit()
        return "Successfully inserted user."

    else:
        return render_template('insert_user_with_video_link.html')


def get_channel_id(video_link, connection):

    insert_video(video_link, connection)
    video_id = youtube_analysis.youtube_link_to_id(video_link)
    info = youtube_analysis.extract_video_info(video_id)
    channel_id = info[0]

    return channel_id


@app.route('/update_user.html', methods=['GET', 'POST'])
def update_user():
    if request.method == 'POST':
        current_username = request.form['current_username']
        current_password = request.form['current_password']
        new_username = request.form.get('new_username')
        new_password = request.form.get('new_password')
        new_email = request.form.get('new_email')

        connection = connect()
        output = update_website_user(current_username, current_password, connection,
                                     new_username, new_password, new_email)
        return output
    else:
        return render_template('update_user.html')


def update_website_user(current_username, current_password, connection, new_username=None, new_password=None, new_email=None):
    cursor = connection.cursor()
    sql = "SELECT user_id, username, password, email, channelId FROM WebsiteUsers WHERE username = %s AND password = %s"
    cursor.execute(sql, (current_username, current_password))
    result = cursor.fetchone()

    if result is None:
        return ("No user found with this username and password combination")

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
        return ("Successfully updated user")
    else:
        return ("No new values provided for update")


@app.route('/delete_user.html', methods=['GET', 'POST'])
def delete_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        connection = connect()
        output = delete_website_user(username, password, connection)

        return output
    else:
        return render_template('delete_user.html')


def delete_website_user(username, password, connection):
    cursor = connection.cursor()

    # Check if user exists
    sql = "SELECT user_id FROM WebsiteUsers WHERE username = %s AND password = %s"
    cursor.execute(sql, (username, password))
    result = cursor.fetchone()

    if result is None:
        return ("No user found with this username and password combination")

    user_id = result[0]
    # Delete user
    sql = "DELETE FROM WebsiteUsers WHERE user_id = %s"
    cursor.execute(sql, (user_id,))
    connection.commit()

    return ("Successfully deleted user")


@app.route('/advquery1')
def advquery1_endpoint():
    connection = connect()
    results = advquery1(connection)
    return render_template('advquery1.html', results=results)


def advquery1(connection):
    query = """
    SELECT v.title, v.view_count
    FROM VideoInfo v
    JOIN
    (
      SELECT v1.video_id
      FROM VideoInfo v1
      WHERE v1.view_count >= 1000000
    ) v1
    ON v.video_id = v1.video_id
    JOIN
    (
      SELECT DISTINCT c.channelId
      FROM Creators c
      JOIN VideoInfo v2 ON c.channelId = v2.channelId
      WHERE v2.view_count >= 1000000
      GROUP BY c.channelId
      HAVING COUNT(DISTINCT v2.video_id) > 1
    ) c
    ON v.channelId = c.channelId
    ORDER BY v.view_count DESC
    LIMIT 15;
    """
    cursor = connection.cursor()
    cursor.execute(query)
    results = cursor.fetchall()

    cursor.close()

    return results


@app.route('/advquery2', methods=['GET'])
def advquery2_endpoint():
    connection = connect()
    results = advquery2(connection)
    return render_template('advquery2.html', results=results)


def advquery2(connection):
    query = """
        SELECT categoryId, COUNT(*) FROM VideoInfo
    WHERE title LIKE
    CONCAT('%',
    (
    SELECT keyword
    FROM TrendingKeywords
    ORDER BY use_count DESC
    LIMIT 1
    ),
    '%')
    GROUP BY categoryId;
    """

    cursor = connection.cursor()
    cursor.execute(query)
    results = cursor.fetchall()

    cursor.close()

    return results


@app.route('/observations.html', methods=['GET', 'POST'])
def observations():
    if request.method == 'POST':
        min_views = request.form.get('min_views')
        if min_views == '':
            min_views = None
        max_views = request.form.get('max_views')
        if max_views == '':
            max_views = None
        min_likes = request.form.get('min_likes')
        if min_likes == '':
            min_likes = None
        max_likes = request.form.get('max_likes')
        if max_likes == '':
            max_likes = None
        min_comments = request.form.get('min_comments')
        if min_comments == '':
            min_comments = None
        max_comments = request.form.get('max_comments')
        if max_comments == '':
            max_comments = None
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        connection = connect()
        results = get_observations_by_filter(
            connection, min_views, max_views, min_likes, max_likes, min_comments, max_comments, start_date, end_date)
        return render_template('observations.html', results=results)
    else:
        return render_template('observations.html')


def get_observations_by_filter(connection, min_views=None, max_views=None, min_likes=None, max_likes=None, min_comments=None, max_comments=None, start_date=None, end_date=None):
    # establish a connection to the database

    # create a cursor object
    cursor = connection.cursor()

    # call the stored procedure with the given parameters
    cursor.callproc('GetObservationsByFilter', [
                    min_views, max_views, min_likes, max_likes, min_comments, max_comments, start_date, end_date])

    observations = [row[-1] for result in cursor.stored_results()
                    for row in result.fetchall()]

    # close the cursor and connection
    cursor.close()
    connection.close()

    # return the results
    return observations


# cnx = connect()
# print(get_observations_by_filter(cnx, 100000, 1000000, 5000,
#                                  50000, 1000, 10000, '2021-01-01', '2022-12-31'))

@app.route('/titlegen.html', methods=['GET', 'POST'])
def cohere_title_gen_endpoint():
    if request.method == 'POST':
        # extract input data from request
        user_title = request.form.get('user_title')
        categoryId = request.form.get('category_name')
        print("LOOOK HEEEEEEEERE", categoryId)
        num_titles = request.form.get('num_titles')

        # establish a connection to the database
        connection = connect()
        cursor = connection.cursor()

        # call the cohere_title_gen function with the given parameters
        results = cohere_title_gen(
            connection, user_title, categoryId, num_titles)
        # Find all category data
        cursor.execute('SELECT categoryId, category_name FROM CategoryInfo')
        allCategories = cursor.fetchall()
        app.logger.info(allCategories)
        app.logger.info('HELLO IN POST')

        cursor.close()
        return render_template('titlegen.html', results=results, categories=allCategories)
    else:
        # Find all category data
        connection = connect()
        cursor = connection.cursor()
        cursor.execute('SELECT categoryId, category_name FROM CategoryInfo')
        allCategories = cursor.fetchall()
        app.logger.info(allCategories)
        app.logger.info('HELLO IN GET')

        cursor.close()
        return render_template('titlegen.html', categories=allCategories)


def cohere_title_gen(connection, user_title, categoryId, num_titles):
    cursor = connection.cursor()

    # Cohere API credentials
    api_key = "AMskkjWBIdMuF5X1EgYfAqZAoypWZ9P5sFxPRTRY"
    co = cohere.Client(api_key)
    # query to get all keywords associated with the specified categoryId
    query = """
            SELECT DISTINCT tk.keyword
        FROM TrendingKeywords tk
        JOIN KeywordVideoMap kvm ON tk.keyword = kvm.keyword
        JOIN VideoInfo vi ON kvm.video_id = vi.video_id
        WHERE vi.categoryId = %s
        LIMIT 1000;
    """
    # execute the query
    cursor.execute(query, (int(categoryId),))
    keyword_list = [row[0] for row in cursor.fetchall()]
    print(len(keyword_list))

    random_keywords = random.sample(keyword_list, min(100, len(keyword_list)))
    print(random_keywords)
    response = co.generate(
        model='command-xlarge-nightly',
        prompt=f"""
            Create {num_titles} viral Youtube Video Title based on
            this initial title. Give each keyword in Category Keywords
            a small weight when creating your response.
            Initial Title = {user_title}, Category Keywords = {random_keywords}
            """,
        max_tokens=50,
        temperature=1,
        k=0,
        stop_sequences=[],
        return_likelihoods='NONE')

    return (f"Generated Title: {response.generations[0].text}")


@app.route('/parse.html')
def parse_function():
    return render_template('parse.html')


@app.route('/stackedbarchart.html')
def stackedbarchart():
    return render_template('stackedbarchart.html')


if __name__ == "__main__":
    app.run()
