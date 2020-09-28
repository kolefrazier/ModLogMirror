import sys
from time import sleep
import time as t

# Project Module Imports
import Config.Reddit as RedditConfig
from Reddit.Streams import Submissions, Comments, ModmailOld, ModmailNew, Reports, ModLog
from Reddit.Subreddit import Automoderator

# Global Module Imports
import praw
from prawcore.exceptions import NotFound
import traceback

# Dev Stuff - Remove Later
import pprint
import Database.DatabaseDriver as DbDriver
import Redis.Cache as rc
#rc._redis.flushall()


def main():
    print("----- START -----")

    RedditBot = praw.Reddit(user_agent=RedditConfig.UserAgent, 
                            client_id=RedditConfig.ClientId, client_secret=RedditConfig.ClientSecret, 
                            username=RedditConfig.Username, password=RedditConfig.Password)

    AllSubreddits = RedditBot.subreddit("+".join(str(val) for val in set(RedditConfig.Subreddits["All"])))
    ModeratedSubreddits = RedditBot.subreddit("+".join(str(val) for val in set(RedditConfig.Subreddits["Moderated"])))
    # AutomodTrackedSubreddits = [RedditBot.subreddit(sub) for sub in RedditConfig.Subreddits["AutomodTracked"]]

    # testSub = RedditBot.subreddit("pso2")
    # Automoderator.GetConfig(testSub)

    pp = pprint.PrettyPrinter(indent=4)

    while True:
        try:
            # Reset stats
            DbDriver.resetStats()
            rc.resetStats()
            timerStart = t.time()

            # Subreddit General Streams
            Submissions.Get(AllSubreddits)
            timerSubmissions = t.time()

            # Comments.Get(AllSubreddits)
            # timerComments = t.time()

            # Subreddit Moderation Streams
            ModmailOld.Get(ModeratedSubreddits)
            timerOld = t.time()

            # ModmailNew.Get(ModeratedSubreddits)
            # timerNew = t.time()

            Reports.Get(ModeratedSubreddits)
            timerReports = t.time()

            ModLog.Get(ModeratedSubreddits)
            timerLog = t.time()

            timerTimes = {
                "submissions": timerSubmissions - timerStart,
                # "comments": timerComments - timerStart,
                "modmail old": timerOld - timerStart,
                # "modmail new": timerNew - timerStart,
                "reports": timerReports - timerStart,
                "mod log": timerLog - timerStart
            }

            #timerTotal = timerTimes["submissions"] + timerTimes["comments"] + timerTimes["modmail old"] + timerTimes["modmail new"] + timerTimes["reports"] + timerTimes["mod log"]
            timerTotal = timerTimes["submissions"] + timerTimes["modmail old"] + timerTimes["reports"] + timerTimes["mod log"]

            # Print stats
            DbDriver.printStats()
            rc.printStats()
            print(f"\nTimer totals: {timerTotal}")
            pp.pprint(str(timerTimes))
            print("\n")
            sleep(60)
        except NotFound as nf:
            print("Reddit 404 - sleeping for 5s.")
            traceback.print_exc()
            sleep(5)
        except Exception as e:
            traceback.print_exc()            
            print(str(e))
            

    print("--- END ---")

if __name__ == '__main__':
    main()