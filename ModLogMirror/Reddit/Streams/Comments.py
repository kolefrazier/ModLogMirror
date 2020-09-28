import praw
from ..Data import Comments, Subreddits, Contributers


def Get(subreddits):
    for comment in subreddits.stream.comments(pause_after=1):
        if(comment is None):
            break

        # From: https://praw.readthedocs.io/en/latest/tutorials/comments.html#extracting-comments-with-praw
        # Comment forests can contain 'MoreComments' ("load more comments") placeholders objects, which don't have the "body" property.
        # Thus, if it's an instance of this, safely skip it. Otherwise, we may receive "AttributeError: object has no attribute 'body'."
        if isinstance(comment, praw.models.MoreComments):
            continue

        contributerId = Contributers.Insert(comment.author.name)
        subredditId = Subreddits.Insert(comment.subreddit.display_name, comment.subreddit.id)
        Comments.Upsert(comment, contributerId, subredditId)
