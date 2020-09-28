from datetime import datetime
import Reddit.Enums as RedditEnums
import Database.DatabaseDriver as DbDriver
from Reddit.Data import Subreddits, Contributers, Mods

""" Data-layer wrapper functions for Submissions """

def Upsert(submission, contributerId, subredditId, approvedByMod):
    Existing = __getExisting(submission.id)

    if(Existing is None):
        CreatedDate = datetime.utcfromtimestamp(submission.created_utc)
        SubmissionContent = submission.selftext if submission.is_self else submission.url

        CreatedSubmission = __insert(
            submission.id,
            RedditEnums.GetTypeEnumFromIDString(submission.fullname).value,
            subredditId, #Subreddits.Insert(submission.subreddit.display_name, submission.subreddit.id),
            submission.title,
            SubmissionContent,
            submission.link_flair_text,
            contributerId, # Contributers.Insert(submission.author.name),
            RedditEnums.GetStatusFromSubmissionObject(submission).value,
            CreatedDate,
            CreatedDate, # It was just created, created & updated should be the exact same.
            approvedByMod # ActingMod
        )

        __insertStats(CreatedSubmission[0])

        return CreatedSubmission[0]
    else:
        __update(
            submission.id,
            RedditEnums.GetStatusFromSubmissionObject(submission).value,
            str(datetime.utcnow()), # PRAW's docs for the Submission model does not have an "updated_at" field, so use the current datetime.
            submission.link_flair_text,
            approvedByMod
        )
        return Existing[0]

def __getExisting(id):
    return DbDriver.ExecuteQuery(
        """SELECT id
            FROM submissions
            WHERE reddit_id = %(redditId)s;""",
        {
            'redditId': id
        }
    ).fetchone()

def __insert(redditId, redditType, subredditId, title, content, flairText, contributerId, status, created, updated, approvedBy):
    return DbDriver.ExecuteQuery(
                """INSERT INTO submissions (reddit_id, reddit_type, subreddit_id, title, content, flair_text, contributer_id, submission_status, submission_date, last_updated, approved_by) 
                    VALUES (%(reddit_id)s, %(type)s, %(sub_id)s, %(title)s, %(content)s, %(flair_text)s, %(contributer_id)s, %(status)s, %(created)s, %(updated)s, %(approved_by)s)
                    RETURNING id;""", 
                {
                    'reddit_id': redditId,
                    'type': redditType,
                    'sub_id': subredditId,
                    'title': title,
                    'content': content,
                    'flair_text': flairText,
                    'contributer_id' : contributerId,
                    'status': status,
                    'created': created,
                    'updated': updated,
                    'approved_by': approvedBy
                }
            ).fetchone()
    
def __insertStats(submissionId):
    DbDriver.ExecuteQuery(
        """INSERT INTO submission_stats (submission_id)
            VALUES (%(submission_id)s);
        """,
        {
            'submission_id': submissionId
        }
    )

def __update(redditId, status, updated, flairText, approvedby):
    DbDriver.ExecuteQuery(
        """UPDATE submissions 
            SET submission_status = %(status)s, last_updated = %(updated)s, approved_by = %(approved_by)s, flair_text = %(flair_text)s
            WHERE reddit_id = %(reddit_id)s;""", 
        {
            'reddit_id': redditId,
            'status': status,
            'updated': updated,
            'flair_text': flairText,
            'approved_by': approvedby
        }
    )
