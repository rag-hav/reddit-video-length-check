import json

from Reddit import reddit

class Config():

    configDict = None

    def getConfigDict(self):
        if self.configDict is None:
            wikipage = reddit.subreddit("porninaminute").wiki["porninaminutebot"]
            configStr = wikipage.content_md
            self.configDict = json.loads(configStr)
        return self.configDict


    def __getattr__(self, key):
        return self.getConfigDict()[key]

config = Config()
