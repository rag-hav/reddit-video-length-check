from youtube_dl import YoutubeDL
from youtube_dl.utils import YoutubeDLError
from pprint import pprint
import os
import subprocess
import sys
import signal


LOWER_DURATION_LIMIT = 55
UPPER_DURATION_LIMIT = 65

DEBUG = False


def isVideoOfAccepatableLength(submission):
    filename = submission.id
    url = submission.url
    duration, error = getVideoDurationFromLink(url)

    if duration is None:
        assert error
        return ambiguousLinkAction(submission, error)

    else:
        assert not error
        return LOWER_DURATION_LIMIT < duration < UPPER_DURATION_LIMIT

    
def getVideoDurationFromLink(url):
    '''Checks for duration data on webpage itself, with Youtube-dl.
    calls ffprobe if duration data is not found'''

    debugPrint("Checking Url: " + url)

    ydlOpts = {
        "quiet": True,
        "no_warnings": True,
    }

    try:
        with YoutubeDL(ydlOpts) as ydl:
            result = ydl.extract_info(url, download=False)

            if "duration" in result.keys():
                duration = float(result["duration"])
                debugPrint("Found duration on webpage: " + str(duration))
                return duration, None

            else:
                return getDurationUsingFFprobe(result)

    except YoutubeDLError as e:
        return None, "YoutubeDL Failed: " + str(e.exc_info[0])
        

def getDurationUsingFFprobe(result):
    
    '''Uses FFprobe application to get duration metadata from true video url
    adapted from https://stackoverflow.com/a/3844467'''

    output = None

    for trueUrl in getTrueUrlsFromResult(result):
        debugPrint("Using FFprobe: " + trueUrl )
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


def ambiguousLinkAction(submission, error):
    '''Actions to be taken if duration of video can not be determined.
    This can happen when the link doesnt point to a video, or a known
    video source or due to a million of other reason that only a human can tell
    if the bot has a bug or not'''

    print("Error with: " + submission.id  + " url: " + submission.url)
    print(error + '\n')
    # TODO
    return True


def debugPrint(string):
    if DEBUG:
        print("DEBUG\t" + string)
