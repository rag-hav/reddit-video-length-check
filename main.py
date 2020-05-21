import time
from prawcore.exceptions import RequestException, ServerError
import praw
import os
from utils import (
    isVideoOfAccepatableLength,
    SignalHandler,
    debugPrint,
)

signalHandler = SignalHandler()

REMOVAL_MESSAGE = "Your post has been removed for breaking the rule 7. " \
                "Video must be 60 seconds long.  " \
                "\n\nContact the moderators of this sub, if " \
                "you think this was a mistake.  \n\n***\n" \
                "^(I am a bot and this action was performed automatically.)"
def main():

    for submission in reddit.subreddit("porninaminute").stream.submissions():

        if submission.saved:
            debugPrint("Skipping Saved: " + submission.id)
            continue

        signalHandler.loopStart()

        debugPrint()
        print("Discovered: " + submission.id)

        if not submission.is_self:
            if not isVideoOfAccepatableLength(submission):
                submission.mod.remove(reason_id="1505bpacczeq7")
                submission.mod.send_removal_message(REMOVAL_MESSAGE)
                print("Removed: " + submission.permalink)

        submission.save()
        signalHandler.loopEnd()

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
