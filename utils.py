from youtube_dl import YoutubeDL
from youtube_dl.utils import YoutubeDLError
from Reddit import reddit
import sys


DEBUG = False


def isVideoOfAccepatableLength(submission, config):

    duration, error = getVideoDurationFromLink(submission.url)

    if duration is None:
        assert error
        return ambiguousLinkAction(submission, error, config)

    else:
        assert not error
        return config.LOWER_DURATION_LIMIT < duration < config.UPPER_DURATION_LIMIT


def getVideoDurationFromLink(url, forceGeneric=False):
    '''Checks for duration data on webpage itself, with Youtube-dl.
    calls ffprobe if duration data is not found'''

    debugPrint("Checking Url: " + url)

    ydlOpts = {
        "no_warnings": True,
        "quiet": True,
        "force_generic_extractor": forceGeneric,
    }

    try:
        with YoutubeDL(ydlOpts) as ydl:
            result = ydl.extract_info(url, download=False,
                                      force_generic_extractor=forceGeneric)

            if not isinstance(result, dict):
                raise YoutubeDLError()

            if "duration" in result.keys():
                duration = float(result["duration"])
                debugPrint("Found duration on webpage: " + str(duration))
                return duration, None

            else:
                return getDurationUsingFFprobe(result)

    except YoutubeDLError as _:
        if not forceGeneric:
            print("Retrying with generic Extractor")
            return getVideoDurationFromLink(url, forceGeneric=True)

        return None, "YoutubeDL Failed"


def getDurationUsingFFprobe(result):
    '''Uses FFprobe application to get duration metadata from true video url
    adapted from https://stackoverflow.com/a/3844467'''

    output = None

    import subprocess
    for trueUrl in getTrueUrlsFromResult(result):
        debugPrint("Using FFprobe: " + trueUrl)
        output = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                                 "format=duration", "-of",
                                 "default=noprint_wrappers=1:nokey=1", trueUrl],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)

        try:
            duration = float(output.stdout)
            debugPrint("Found duration with FFprobe: " + str(duration))
            return duration, None

        except ValueError:
            continue

    # If the program reaches here, then an error has already occured
    if output:
        error_msg = str(output.stdout)
    else:
        error_msg = "Couldnt find any true url"

    return None, "FFprobe Failed: " + error_msg


def getTrueUrlsFromResult(result):

    if result.get("_type") == "video" or result.get("_type") is None:
        if result.get("url"):
            yield result["url"]
        if result.get("formats"):
            for format_ in result.get("formats"):
                yield format_["url"]

    elif result.get("_type") == "playlist":
        if len(result["entries"]) > 1:
            print("WARNING: more than one video linked, will only check first")
        for result_ in result["entries"]:
            yield from getTrueUrlsFromResult(result_)


def ambiguousLinkAction(submission, error, config):
    '''Actions to be taken if duration of video can not be determined.
    This can happen when the link doesnt point to a video, or a known
    video source or due to a million of other reason that only a human can tell
    if the bot has a bug or not'''

    print("Error with: " + submission.id + " url: " + submission.url)
    print(error)
    if config.REPORT_POSTS_ON_WHICH_BOT_FAILS:
        submission.report(config.BOT_ERROR_MESSAGE)
    if config.MODMAIL_POSTS_ON_WHICH_BOT_FAILS:
        reddit.subreddit(config.SUBREDDIT).message(
            config.BOT_ERROR_MESSAGE, submission.permalink)
    return True


def debugPrint(string=''):
    if DEBUG:
        if string:
            print("DEBUG\t" + string)
        else:
            print()


class SignalHandler():
    ''' To ensure processing a post is not interrupted during
    heroku's cycle'''

    def __init__(self):
        import signal
        signal.signal(signal.SIGINT, self._signalHandler)
        signal.signal(signal.SIGTERM, self._signalHandler)
        self.exitCondition = False
        self.inLoop = False

    def _signalHandler(self, signal, _):
        print(f"RECIEVED SIGNAL: {signal}, Bye")
        if not self.inLoop:
            sys.exit(0)
        else:
            self.exitCondition = True

    def loopEnd(self):
        self.inLoop = False

        if self.exitCondition:
            sys.exit(0)

    def loopStart(self):
        self.inLoop = True
