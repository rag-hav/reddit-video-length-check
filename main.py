import time
from prawcore.exceptions import RequestException, ServerError
import praw
import os
from utils import (
    isVideoOfAccepatableLength,
    debugPrint,
)


def main():

    for submission in reddit.subreddit("porninaminute").stream.submissions():

        debugPrint("Discovered: " + submission.id)

        if submission.saved:
            debugPrint("Skipping Saved: " + submission.id)
            continue

        if not submission.is_self:
            if not isVideoOfAccepatableLength(submission):
                # submission.mod.remove()
                submission.report("Reported by bot for not being a minute long")
                print("Removed: " + submission.permalink)

        submission.save()

reddit = praw.Reddit(
    client_id=os.getenv("MY_CLIENT_ID"),
    client_secret=os.getenv("MY_CLIENT_SECRET"),
    user_agent=os.getenv("MY_USER_AGENT"),
    username=os.getenv("MY_USERNAME"),
    password=os.getenv("MY_PASSWORD"))


if __name__ == "__main__":

    print("Starting the bot")
    while(True):
        try:
            main()
        # Network Issues
        except (RequestException, ServerError) as e:
            print(e)
            time.sleep(60)
        else:
            raise "Program Finished Abnormally"
