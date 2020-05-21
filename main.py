import time
from prawcore.exceptions import RequestException, ServerError
from Reddit import reddit
from configs import config
from utils import (
    isVideoOfAccepatableLength,
    SignalHandler,
    debugPrint,
)

signalHandler = SignalHandler()

def main():
    REMOVAL_MESSAGE = config.REMOVAL_MESSAGE

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
