from googleapiclient.errors import HttpError
import json
from pytube import extract
import os

import google_auth_oauthlib.flow
import googleapiclient.errors
import googleapiclient.discovery
from settings import YOUTUBE_DEVELOPER_KEY


# extract the video id from a given youtube URL


def youtube_link_to_id(url):
    try:
        id = extract.video_id(url)
    except:
        print("Invalid URL entered.")
    return id


# extract all the infomation from a video given the video_id in this order:
# channel_id, channel_title, category_id,
# video_id, title, published_at, tags, description,
# comment_count, view_count, likes
def extract_video_info(video_id):

    # set up API credentials and build the YouTube API client
    DEVELOPER_KEY = YOUTUBE_DEVELOPER_KEY
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"
    youtube = googleapiclient.discovery.build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                                              developerKey=DEVELOPER_KEY)

    try:
        # retrieve the video metadata from the YouTube API
        response = youtube.videos().list(
            part="snippet,statistics",
            id=video_id
        ).execute()

        # extract the desired data
        if 'snippet' in response['items'][0]:
            if 'channelId' in response['items'][0]['snippet']:
                channel_id = response['items'][0]['snippet']['channelId']
            else:
                channel_id = None

            if 'channelTitle' in response['items'][0]['snippet']:
                channel_title = response['items'][0]['snippet']['channelTitle']
            else:
                channel_title = None

            if 'categoryId' in response['items'][0]['snippet']:
                category_id = response['items'][0]['snippet']['categoryId']
            else:
                category_id = None

            if 'id' in response['items'][0]:
                video_id = response['items'][0]['id']
            else:
                video_id = None

            if 'title' in response['items'][0]['snippet']:
                title = response['items'][0]['snippet']['title']
            else:
                title = None

            if 'publishedAt' in response['items'][0]['snippet']:
                published_at = response['items'][0]['snippet']['publishedAt']
            else:
                published_at = None

            if 'tags' in response['items'][0]['snippet']:
                tags = response['items'][0]['snippet']['tags']
            else:
                tags = None

            if 'description' in response['items'][0]['snippet']:
                description = response['items'][0]['snippet']['description']
            else:
                description = None

        if 'statistics' in response['items'][0]:
            if 'commentCount' in response['items'][0]['statistics']:
                comment_count = response['items'][0]['statistics']['commentCount']
            else:
                comment_count = None

            if 'viewCount' in response['items'][0]['statistics']:
                view_count = response['items'][0]['statistics']['viewCount']
            else:
                view_count = None

            if 'likeCount' in response['items'][0]['statistics']:
                likes = response['items'][0]['statistics']['likeCount']
            else:
                likes = None
        # Youtube no longer allows access to dislikes
        dislikes = -1

        # return all the information
        return channel_id, channel_title, category_id, video_id, title, published_at, tags, description, comment_count, view_count, likes, dislikes

    except HttpError as error:
        print("An HTTP error %d occurred:\n%s" %
              (error.resp.status, error.content))
