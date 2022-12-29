import os
import sys
import praw


def getVar(varName):
    value = os.getenv(varName)
    if value is None:
        print(f"{varName} environment variable is not set")
        sys.exit(1)
    return value


reddit = praw.Reddit(
    client_id=getVar("MY_CLIENT_ID"),
    client_secret=getVar("MY_CLIENT_SECRET"),
    user_agent=getVar("MY_USER_AGENT"),
    username=getVar("MY_USERNAME"),
    password=getVar("MY_PASSWORD"))
