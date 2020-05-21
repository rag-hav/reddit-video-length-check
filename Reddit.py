import os
import praw

reddit = praw.Reddit(
    client_id=os.getenv("MY_CLIENT_ID"),
    client_secret=os.getenv("MY_CLIENT_SECRET"),
    user_agent=os.getenv("MY_USER_AGENT"),
    username=os.getenv("MY_USERNAME"),
    password=os.getenv("MY_PASSWORD"))

