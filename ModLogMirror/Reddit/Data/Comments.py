from datetime import datetime
import Reddit.Enums as RedditEnums
import Database.DatabaseDriver as DbDriver
from Reddit.Data import Contributers, Subreddits

""" Data-layer wrapper class for Comments """

def Upsert(comment, contributerId, subredditId):
    Existing = Get(comment.id)

    # There will always be a small difference between Reddit's creation date and DateTime.Now, 
    #   so just use Reddit's date for the updated column. Tracking when the record was created really isn't a big need.
    createdTimestamp = str(datetime.utcfromtimestamp(comment.created_utc))

    if (Existing is None):
        SubmittedComment = __insert(
            comment.id,
            contributerId,
            subredditId,
            createdTimestamp,
            comment.parent_id,
            comment.body,
            createdTimestamp 
        )

        return SubmittedComment[0]

    elif (Existing is not None and comment.edited):
        __update(Existing[0], comment.body, str(datetime.utcnow()))
        return Existing[0]

def Get(id):
    return DbDriver.ExecuteQuery(
        """SELECT id, reddit_id
            FROM comments
            WHERE reddit_id = %(redditId)s;""",
        {
            'redditId': id
        },
        "Comments"
    ).fetchone()

def GetWithAuthorInfo(id):
    # Only gets the author username. Currently don't need the author ID, and last_seen isn't being used/populated.
    return DbDriver.ExecuteQuery(
        """SELECT cm.*, c.username
           FROM comments cm
           JOIN contributers c ON c.id = cm.contributer_id
           WHERE s.reddit_id = %(redditId)s;""",
        {
            'redditId': id
        },
        "Submissions"
    ).fetchone()

def __insert(commentRedditId, contributerId, subredditId, created, parentId, body, updated):
    return DbDriver.ExecuteQuery(
        """INSERT INTO comments(reddit_id, contributer_id, subreddit_id, created, parent_reddit_id, body, last_updated)
            VALUES(%(redditId)s, %(contributer)s, %(subreddit)s, %(created)s, %(parentRedditId)s, %(body)s, %(updated)s)
            RETURNING id;""",
        {
            'redditId': commentRedditId,
            'contributer': contributerId,
            'subreddit': subredditId,
            'created': created,
            'parentRedditId': parentId,
            'body': body,
            'updated': updated
        },
        "Comments"
    ).fetchone()

def __update(recordId, body, updated):
    return DbDriver.ExecuteQuery(
        """UPDATE comments
            SET body = %(body)s, last_updated = %(updated)s
            WHERE id = %(existingId)s;""",
        {
            'existingId': recordId,
            'body': body,
            'updated': str(updated)
        },
        "Comments"
    )