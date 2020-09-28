from datetime import datetime
import Reddit.Enums as RedditEnums
import Database.DatabaseDriver as DbDriver
from Reddit.Data import Contributers, Subreddits

""" Data-layer wrapper class for Comments """

def Upsert(comment, contributerId, subredditId):
    Existing = __getExisting(comment.id)

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

def __getExisting(id):
    return DbDriver.ExecuteQuery(
                """SELECT id, reddit_id
                    FROM comments
                    WHERE reddit_id = %(redditId)s;""",
                {
                    'redditId': id
                }
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
                }
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
                }
            )