import json
from Reddit import reddit

# This list contains tuples of format: 
# (subredditname, nameOfWikiWhereConfigsAre)

SUBREDDITS = [("porninaminute", "porninaminutebot"),
        ]


class Config():
     '''Class to lazily get configs from a subreddit'''

    configDict = None

    def __init__(self, subreddit):
        self.SUBREDDIT = subreddit.lower()
        self.WIKINAME = wikiname

    def getConfigDict(self):
        if self.configDict is None:
            wikipage = reddit.subreddit(self.SUBREDDIT).wiki[self.WIKINAME]
            configStr = wikipage.content_md
            self.configDict = json.loads(configStr)
        return self.configDict


    def __getattr__(self, key):
        return self.getConfigDict()[key]

# This dict will contain all Config class objects.
# Additionally it has MULTI_REDDIT string which is simply
# "subreddit1+subreddit2+subreddit3" and so on
configs = {"MULTI_REDDIT" : '+'.join(a[0] for a in SUBREDDITS)}

for subreddit, wikiname in SUBREDDITS:
    configs[subreddit.lower()] = Config(subreddit, wikiname)
