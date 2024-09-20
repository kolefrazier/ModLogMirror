from datetime import datetime
import Reddit.Enums as RedditEnums
import Database.DatabaseDriver as DbDriver
from Reddit.Cache import Mods as ModsCache
from Reddit.Data import Subreddits, Contributers, Mods
from Reddit.Utility import TextHelpers

""" Data-layer wrapper functions for Submissions """

# Upsert the submission.
# Returns the submission ID and a bool indicating whether it's a new insert (True) or not (False)
def Upsert(submission, contributerId, subredditId, approvedByMod):
    Existing = Get(submission.id)

    if(Existing is None):
        CreatedDate = datetime.utcfromtimestamp(submission.created_utc)
        SubmissionContent = submission.selftext if submission.is_self else submission.url
        SubmissionDomain = None if submission.is_self else submission.domain

        CreatedSubmission = __insert(
            submission.id,
            RedditEnums.GetTypeEnumFromIDString(submission.fullname).value,
            subredditId, #Subreddits.Insert(submission.subreddit.display_name, submission.subreddit.id),
            submission.title,
            SubmissionContent,
            SubmissionDomain,
            submission.link_flair_text,
            contributerId, # Contributers.Insert(submission.author.name),
            RedditEnums.GetStatusFromSubmissionObject(submission).value,
            CreatedDate,
            CreatedDate, # It was just created, so created & updated should be the exact same.
            approvedByMod, # ActingMod
            submission.over_18, # Is NSFW
            submission.spoiler, # Is spoiler
            submission.permalink # Link to the comments. In form of "/r/subreddit/comments/id/title_string"
        )

        __insertStats(CreatedSubmission[0])

        return CreatedSubmission[0], True
    else:
        __update(
            submission.id,
            RedditEnums.GetStatusFromSubmissionObject(submission).value,
            str(datetime.utcnow()), # PRAW's docs for the Submission model does not have an "updated_at" field, so use the current datetime.
            submission.link_flair_text,
            approvedByMod,
            submission.over_18,
            submission.spoiler
        )
        return Existing[0], False

def GetUnnotified(subredditId, limit=5):
    QueryResults = DbDriver.ExecuteQuery(
        # Query does not join on the moderators table due to issues getting all submission rows where the approved_by value is NULL or NOT NULL
        # 0  s.id
        # 1  s.reddit_id
        # 2  s.title
        # 3  s.content
        # 4  s.domain
        # 5  s.flair_text
        # 6  s.submission_status
        # 7  c.username
        # 8  s.approved_by
        # 9  s.reddit_type
        # 10 s.over_18
        # 11 s.spoiler
        # 12 s.permalink
        """SELECT s.id, s.reddit_id, s.title, s.content, s.domain, s.flair_text, s.submission_status, c.username, s.approved_by, s.reddit_type, s.over_18, s.spoiler, s.permalink
           FROM submissions s
           JOIN contributers c on s.contributer_id = c.id
           WHERE discord_notified = false
           AND s.subreddit_id = %(subredditId)s
           ORDER BY s.id ASC LIMIT %(limit)s;
        """,
        {
            "subredditId": subredditId,
            "limit": limit
        }
    ).fetchall()

    Submissions = []
    for submission in QueryResults:
        ContentTrimmed = TextHelpers.TrimContent(submission[3])
        ModUsername = ModsCache.GetByDatabaseId(submission[8])
        SubmissionStatus = RedditEnums.SubmissionStatus(submission[6]).name
        RedditType = "Self" if submission[4] is None else "Link" # Checked this way, as the proper Reddit Type would just be "Link" (t3_id)

        Submissions.append({
            "id": submission[0],
            "reddit_id": submission[1],
            "shortlink": f"https://redd.it/{submission[1]}",
            "title": submission[2],
            "content": ContentTrimmed,
            "domain": submission[4],
            "submissionType": RedditType,
            "flair": submission[5],
            "status": SubmissionStatus,
            "author": submission[7],
            "mod": ModUsername,
            "over_18": submission[10],
            "spoiler": submission[11],
            "permalink": submission[12]
        })

    return Submissions

def MarkNotified(submissionIds):
    DbDriver.ExecuteQuery(
        """UPDATE submissions
           SET discord_notified = true
           WHERE id IN %(ids)s;
        """,
        {
            "ids": tuple(submissionIds)
        }
    )

def GetAny():
    """ Get the very first record. Used to check if the table is empty or not. """
    return DbDriver.ExecuteQuery(
        """ SELECT id
            FROM submissions
            ORDER BY id ASC LIMIT 1
        """
    ).fetchall()

def Get(id):
    return DbDriver.ExecuteQuery(
        """SELECT id
            FROM submissions
            WHERE reddit_id = %(redditId)s;""",
        {
            'redditId': id
        },
        "Submissions"
    ).fetchone()

def GetWithAuthorInfo(id):
    # Only gets the author username. Currently don't need the author ID, and last_seen isn't being used/populated.
    return DbDriver.ExecuteQuery(
        """SELECT s.*, c.username
           FROM submissions s
           JOIN contributers c ON c.id = s.contributer_id
           WHERE s.reddit_id = %(redditId)s;""",
        {
            'redditId': id
        },
        "Submissions").fetchone()

def GetHistoryCheckNeeded():
    # Query does not join on the moderators table due to issues getting all submission rows where the approved_by value is NULL or NOT NULL
    # 0  s.id
    # 1  s.reddit_id
    # 2  s.title
    # 3  s.content
    # 4  s.domain
    # 5  s.flair_text
    # 6  s.submission_status
    # 7  c.username
    # 8  s.approved_by
    # 9  s.reddit_type
    # 10 s.over_18
    # 11 s.spoiler
    # 12 s.permalink
    QueryResults = DbDriver.ExecuteQuery(
        """SELECT s.id, s.reddit_id, s.title, s.content, s.domain, s.flair_text, s.submission_status, c.username, s.approved_by, s.reddit_type, s.over_18, s.spoiler, s.permalink
           FROM submissions s
           JOIN contributers c on s.contributer_id = c.id
           WHERE self_promo_check = false;
        """
    )

    Submissions = []
    for submission in QueryResults:
        ContentTrimmed = TextHelpers.TrimContent(submission[3])
        ModUsername = ModsCache.GetByDatabaseId(submission[8])
        SubmissionStatus = RedditEnums.SubmissionStatus(submission[6]).name
        RedditType = "Self" if submission[4] is None else "Link" # Checked this way, as the proper Reddit Type would just be "Link" (t3_id)

        Submissions.append({
            "id": submission[0],
            "reddit_id": submission[1],
            "shortlink": f"https://redd.it/{submission[1]}",
            "title": submission[2],
            "content": ContentTrimmed,
            "domain": submission[4],
            "submissionType": RedditType,
            "flair": submission[5],
            "status": SubmissionStatus,
            "author": submission[7],
            "mod": ModUsername,
            "over_18": submission[10],
            "spoiler": submission[11],
            "permalink": submission[12]
        })

    return Submissions

def __insert(redditId, redditType, subredditId, title, content, domain, flairText, contributerId, status, created, updated, approvedBy, over_18, spoiler, permalink):
    return DbDriver.ExecuteQuery(
                """INSERT INTO submissions (reddit_id, reddit_type, subreddit_id, title, content, domain, flair_text, contributer_id, submission_status, submission_date, last_updated, approved_by, over_18, spoiler, permalink) 
                    VALUES (%(reddit_id)s, %(type)s, %(sub_id)s, %(title)s, %(content)s, %(domain)s, %(flair_text)s, %(contributer_id)s, %(status)s, %(created)s, %(updated)s, %(approved_by)s, %(over_18)s, %(spoiler)s, %(permalink)s)
                    RETURNING id;""", 
                {
                    'reddit_id': redditId,
                    'type': redditType,
                    'sub_id': subredditId,
                    'title': title,
                    'content': content,
                    'domain': domain,
                    'flair_text': flairText,
                    'contributer_id' : contributerId,
                    'status': status,
                    'created': created,
                    'updated': updated,
                    'approved_by': approvedBy,
                    'over_18': over_18,
                    'spoiler': spoiler,
                    'permalink': permalink
                },
                 "Submissions"
            ).fetchone()
    
def __insertStats(submissionId):
    DbDriver.ExecuteQuery(
        """INSERT INTO submission_stats (submission_id)
            VALUES (%(submission_id)s);
        """,
        {
            'submission_id': submissionId
        },
        "Submissions"
    )

def __update(redditId, status, updated, flairText, approvedby, over_18, spoiler):
    DbDriver.ExecuteQuery(
        """UPDATE submissions 
            SET submission_status = %(status)s, last_updated = %(updated)s, approved_by = %(approved_by)s, flair_text = %(flair_text)s, over_18 = %(over_18)s, spoiler = %(spoiler)s
            WHERE reddit_id = %(reddit_id)s;""", 
        {
            'reddit_id': redditId,
            'status': status,
            'updated': updated,
            'flair_text': flairText,
            'approved_by': approvedby,
            'over_18': over_18,
            'spoiler': spoiler
        },
        "Submissions"
    )
