import time
from prawcore.exceptions import RequestException, ServerError
from Reddit import reddit
from configs import configs
from utils import (
    isVideoOfAccepatableLength,
    SignalHandler,
    debugPrint,
)

signalHandler = SignalHandler()

def main():

    MULTI_REDDIT = configs["MULTI_REDDIT"]
    for submission in reddit.subreddit(MULTI_REDDIT).stream.submissions():

        if submission.saved:
            debugPrint("Skipping Saved: " + submission.id)
            continue

        signalHandler.loopStart()

        debugPrint()
        print("Discovered: " + submission.id)

        if not submission.is_self:
            config = configs[submission.subreddit.display_name.lower()]
            if not isVideoOfAccepatableLength(submission, config):
                submission.mod.remove(reason_id=config.REASON_ID)
                submission.mod.send_removal_message(config.REMOVAL_MESSAGE)
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
            raise Exception("Program Finished Abnormally")
