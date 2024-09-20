import sys
from time import sleep
import time as t
from datetime import datetime

# Project Module Imports
import Config.Environment as EnvironmentConfig
import Config.Reddit as RedditConfig
from Reddit.Streams import Submissions, Comments, ModmailOld, ModmailNew, Reports, ModLog
from Reddit.Subreddit import Automoderator


# Global Module Imports
import praw
from prawcore.exceptions import NotFound, ServerError
import traceback

def main():
    RedditBot = praw.Reddit(user_agent=RedditConfig.UserAgent, 
                            client_id=RedditConfig.ClientId, client_secret=RedditConfig.ClientSecret, 
                            username=RedditConfig.Username, password=RedditConfig.Password)

    id = praw.models.Submission.id_from_url(url="")

    ServerErrorCounter = 0
    previousScore = 0
    currentScore = 0

    while(True):
        try:
            targetSubmission = praw.models.Submission(reddit=RedditBot, id=id)

            previousScore = currentScore
            currentScore = targetSubmission.score

            # Send data to file
            checkTime = str(datetime.utcnow())
            with open("Guaxichan_ModPost_Scores_Tracker.txt", "a") as f:
                f.write(f"{currentScore}|{currentScore-previousScore}|{checkTime}\n")
                print(f"Updated: {currentScore}|{checkTime}")

            # End of loop stuff
            ServerErrorCounter = 0
            sleep(5*60)
        except ServerError as se: #praw error
            ServerErrorCounter += 1 # Increase counter first
            sleep(30 * ServerErrorCounter)
            print(f"[HTTP 503] ServerError Thrown, sleeping 30s * {ServerErrorCounter}")
        except NotFound as nf: # Praw error
            print("Reddit 404 - sleeping for 5s.")
            traceback.print_exc()
            sleep(5)
        except Exception as e:
            print(f"Unhandled exception: {str(e)}")
            traceback.print_exc()            


if __name__ == "__main__":
    main()