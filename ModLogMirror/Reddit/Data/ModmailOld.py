from datetime import datetime
import Database.DatabaseDriver as DbDriver
from Reddit.Data import Contributers, Subreddits

def Insert(mail, subredditId, contributerId):
    createdDate = datetime.utcfromtimestamp(mail.created_utc)
    __insert(mail.id, contributerId, subredditId, mail.subject, mail.body, createdDate, mail.parent_id)

def __insert(redditId, contributerId, subredditId, subject, body, createdDate, parentId):
    DbDriver.ExecuteQuery(
        """INSERT INTO modmail_old_messages (reddit_id, contributer_id, subreddit_id, subject, body, created, parent_id)
            VALUES(%(reddit_id)s, %(contributer_id)s, %(subreddit_id)s, %(subject)s, %(body)s, %(created)s, %(parent_id)s);
        """,
        {
            'reddit_id': redditId,
            'contributer_id': contributerId,
            'subreddit_id': subredditId,
            'subject': subject,
            'body': body,
            'created': createdDate,
            'parent_id': parentId
        }
    )
