from time import sleep
import time as t
import logging
import requests.exceptions as RequestExceptions
from Reddit.Data import Submissions
import praw

from Config import Environment as EnvironmentConfig, Reddit as RedditConfig

logger = logging.getLogger("selfpromochecker-modlogmirror")
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename="selfpromochecker.log", encoding="utf-8", mode="a")
handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
logger.addHandler(handler)

def main():
    if EnvironmentConfig.Environment == "dev":
        logger.setLevel(logging.DEBUG)

    RedditBot = praw.Reddit(user_agent=RedditConfig.UserAgent, 
                            client_id=RedditConfig.ClientId, client_secret=RedditConfig.ClientSecret, 
                            username=RedditConfig.Username, password=RedditConfig.Password)

    PRINT_DEBUG = True
    authors = []
    while True:
        submissions = Submissions.GetHistoryCheckNeeded()
        for sub in submissions:
            # Check Redis for a 24-hour indicator key.
            #   If found, report item as multiple posts in 24 hours.
            # Then, check post flair - if not one of concern (eg phasion), skip.
            # Get author
            # Check author history
            #   Then act on result
            #   Then update item in DB
            author = RedditBot.redditor(sub["author"])

            if(author.name in authors):
                continue

            submissions = get_submissions(author, print_debug=PRINT_DEBUG)
            comments = get_comments(author, print_debug=PRINT_DEBUG)
            authors.append(author.name)
        print("asdf")
        sleep(90)

def get_submissions(redditor, print_debug=False):
    posts = []
    for post in redditor.submissions.new(limit=25):
        if(post.subreddit.display_name.lower() != "pso2"):
            continue
        posts.append(post)

    if(print_debug):
        print(f"{redditor.name}: {len(posts)} posts")

    return posts

def get_comments(redditor, print_debug=False):
    comments = []
    for comment in redditor.comments.new(limit=25):
        if(comment.subreddit.display_name.lower() != "pso2"):
            continue
        comments.append(comment)

    if(print_debug):
        print(f"{redditor.name}: {len(comments)} posts")

    return comments

if __name__ == '__main__':
    main()