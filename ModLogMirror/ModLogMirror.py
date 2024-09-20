import sys
from time import sleep
import time as t
import logging
import traceback
import pprint

# Project Module Imports
from Config import Environment as EnvironmentConfig, Reddit as RedditConfig, Database as DbConfig
from Reddit.Streams import Submissions, Comments, ModmailOld, ModmailNew, Reports, ModLog
from Reddit.Subreddit import Automoderator


# Global Module Imports
import praw
import prawcore.exceptions as PrawExcept #import NotFound, ServerError, ResponseError

# Dev Stuff - Remove Later?
import Database.DatabaseDriver as DbDriver
from ImageProcessing import Utility as ImageUtility, Data as ImageData
import Reddit.Data.Submissions as RedditSubmissions

import Redis.Cache as RedisCache

logger = logging.getLogger("reddit-modlogmirror")
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename="modlogmirror.log", encoding="utf-8", mode="a")
handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
logger.addHandler(handler)

ServerErrorCounter = 0

def DevelopmentEnvironmentTasks():
    print("--- START ---")

    # Logging
    logger.setLevel(logging.DEBUG)

    # Redis
    if len(RedditSubmissions.GetAny()) == 0:
        RedisCache._redis.flushall()
        print("Flushed all Redis keys")
    else:
        print("Submissions found - skipping Redis flush")

    # ImageProcessing Files
    if len(ImageData.GetAny()) == 0:
        ImageUtility.EmptyImageSaveDirectory()
    else:
        print("Image processing data found - skipping directory clear.")

    # Post Task Announcement
    print("--- Dev env tasks completed! ---\n\n")

def WaitForServices():
    StartupWaitCounter = 1
    while True:
        logger.info(f"[Startup] (Wait Counts: {StartupWaitCounter}) Waiting for other services to start.")
        try:
            if RedditSubmissions.GetAny():
                logger.info("[Startup] Record retrieved from DB. Waiting completed.")
                break
        finally:
            sleep(5 * StartupWaitCounter)

def SleepOnError(error, printTraceback):
    global ServerErrorCounter
    IncrementSleepCounter()

    logger.error(f"{str(error)}\n\nSleeping 30s * {ServerErrorCounter}")
    print(f"{str(error)}\n\nSleeping 30s * {ServerErrorCounter}")

    if EnvironmentConfig.Environment == "dev" or printTraceback:
        traceback.print_exc()
        logger.error(f"Full traceback:\n{traceback.print_exc()}")

    sleep(ServerErrorCounter)

def IncrementSleepCounter():
    global ServerErrorCounter
    if ServerErrorCounter >= 10:
        return 10
    else:
        ServerErrorCounter += 1

def ResetSleepCounter():
    global ServerErrorCounter
    ServerErrorCounter = 0

def main():
    logger.info("ModLogMirror.py startup")
    if EnvironmentConfig.Environment == "dev":
        DevelopmentEnvironmentTasks()
    if EnvironmentConfig.Environment == "prod":
        WaitForServices()

    DbConfig.EnableStats()

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
            RedisCache.resetStats()
            # timerStart = t.time()

            # Subreddit General Streams
            timerSubmissionsStart = t.time()
            Submissions.Get(AllSubreddits)
            timerSubmissionsEnd = t.time()

            # DISABLED UNTIL TESTING IS DONE
            ## Subreddit Moderation Streams
            #timerModMailNewStart = t.time()
            #ModmailNew.Get(ModeratedSubreddits)
            #timerModMailNewEnd = t.time()

            timerReportsStart = t.time()
            Reports.Get(ModeratedSubreddits)
            timerReportsEnd = t.time()

            timerLogStart = t.time()
            ModLog.Get(ModeratedSubreddits)
            timerLogEnd = t.time()

            timerTimes = {
                "submissions": timerSubmissionsEnd - timerSubmissionsStart,
                # "modmail new": timerModMailNewEnd - timerModMailNewStart,
                "reports": timerReportsEnd - timerReportsStart,
                "mod log": timerLogEnd - timerLogStart
            }
            timerTotal = timerTimes["submissions"] + timerTimes["reports"] + timerTimes["mod log"] # timerTimes["modmail new"]

            # Print stats
            if EnvironmentConfig.Environment == "dev":
                DbDriver.printStats()
                RedisCache.printStats()
                print(f"\nTimer totals: {timerTotal}")
                pp.pprint(str(timerTimes))
                print("\n")

            # Sleep stuff
            ResetSleepCounter() # Reset after a successful run
            sleep(90)
        except PrawExcept.ServerError as se:
            SleepOnError(f"ServerError Thrown: {str(se)}", False)
        except PrawExcept.ResponseException as re:
            SleepOnError(f"[ResponseException] Prawcore.ResponseException Thrown: {str(re)}", False)
        except PrawExcept.NotFound as nf:
            # SleepOnError(f"Reddit 404", False) # Do 404s need to do a full sleep..? I would assume no.
            sleep(5)
        except Exception as e:
            SleepOnError(f"An unknown error occurred: {str(e)}", True)

if __name__ == '__main__':
    main()