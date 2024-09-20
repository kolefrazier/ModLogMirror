from datetime import datetime
import Database.DatabaseDriver as DbDriver
from Reddit.Data import Contributers, Subreddits
from Reddit.Utility import TextHelpers

def Insert(mail, subredditId, contributerId):
    createdDate = datetime.utcfromtimestamp(mail.created_utc)
    __insert(mail.id, contributerId, subredditId, mail.subject, mail.body, createdDate, mail.parent_id)

def GetUnnotified(subredditId):
    QueryResults = DbDriver.ExecuteQuery(
        """SELECT m.id, m.reddit_id, c.username, m.subject, m.body, m.created, m.parent_id
           FROM modmail_old_messages m
           JOIN contributers c on c.id = m.contributer_id
           WHERE subreddit_id = %(subredditId)s
           AND discord_notified = false
           ORDER BY m.id ASC;
        """,
        {
            "subredditId": subredditId
        }
    ).fetchall()

    Messages = []
    for message in QueryResults:
        Messages.append({
            "id": message[0],
            "reddit_id": message[1],
            "link": f"https://www.reddit.com/message/messages/{message[1]}",
            "author": message[2],
            "subject": message[3],
            "body": message[4],
            "created": message[5],
            "parent_id": message[6]
        })

    return Messages

def MarkNotified(messageIds):
    # =-- Original Mass-Update Query ---
    # (Saving just incase the current one doesn't work, and since I spent good time on it.)
    #
    #"""UPDATE modmail_old_messages m
    #   SET m.discord_notified = true
    #   FROM (values (%(Ids)s)) AS IdTable(id)
    #   WHERE m.id = IdTable.id
    #""",


    # NOTE: The way messageIds and %(Ids)s are being used is correct!
    #
    # Psycopg2 converts Python lists to SQL ARRAY values. The WHERE clause wants a
    #   tuple-link structure for comparing values with an IN clause.
    # Converting the tuple to a string (as the psycopg2 docs repeatedly detail) without surrounding
    #    parenthesis is goood as well, since the tuple-to-string conversion will add them.
    #
    # Reference psycopg documentation sections:
    # * Query Parameters: https://www.psycopg.org/docs/usage.html#query-parameters
    # * Problems with type conversions: https://www.psycopg.org/docs/faq.html#problems-with-type-conversions
    
    DbDriver.ExecuteQuery(
        """
            UPDATE modmail_old_messages
            SET discord_notified = true
            WHERE id IN %(ids)s;
        """,
        {
            "ids": tuple(messageIds)
        }
    )

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
        },
        "ModmailOld" # Note to future self: this is a legitimate parameter, "source", not a typo. Don't delete!
    )
