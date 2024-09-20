from datetime import datetime
import Reddit.Enums as RedditEnums
import Database.DatabaseDriver as DbDriver
from Reddit.Data import Contributers, Subreddits

def Insert(entry, subredditId, modId, contributerId):
    # If not in cache, check if in the DB
    Existing = __getExisting(entry.id)

    # If not found, insert, cache and return the values
    if (Existing is None):
        # Not all actions have actioned on a Thing.
        redditType = None
        name = None
        if(entry.target_fullname is not None):
            redditType = RedditEnums.GetTypeEnumFromIDString(entry.target_fullname).value
            name = entry.target_fullname.split("_")[1]

        createdDate = datetime.utcfromtimestamp(entry.created_utc)
        __insert(entry.id, subredditId, modId, contributerId, entry.action, entry.description, entry.details, entry.target_title, name, redditType, entry.target_permalink, createdDate)

def GetUnnotified(subredditId):
    QueryResults = DbDriver.ExecuteQuery(
        # The username aliases are not used, but I"m leaving them in for future clarification on which username is for what.
        # LIMIT 25 is to help prevent discord message length issues. (It caps at 6000 characters. 25 seems to cut it close, though ~5500)
        """SELECT ml.id, m.username AS ActingMod, c.username AS TargetAuthor, ml.action, ml.description, ml.details, ml.target_permalink, ml.created
           FROM mod_log ml
           LEFT JOIN moderators m ON m.id = ml.mod_id
           LEFT JOIN contributers c ON c.id = ml.contributer_id
           WHERE subreddit_id = %(subredditId)s
           AND discord_notified = false
           ORDER BY ml.id ASC
           LIMIT 25;
        """,
        {
            "subredditId": subredditId
        }
    ).fetchall()

    LogEntries = []
    for entry in QueryResults:
        # m.username, c.username, ml.action, ml.description, ml.details, ml.target_permalink, ml.created
        LogEntries.append({
            "id": entry[0],
            "acting_mod": entry[1],
            "target_author": entry[2],
            "action": entry[3],
            "description": entry[4],
            "details": entry[5],
            "target_permalink": entry[6],
            "created": entry[7],
        })

    return LogEntries

def MarkNotified(messageIds):
    DbDriver.ExecuteQuery(
        """UPDATE mod_log
           SET discord_notified = true
           WHERE id IN %(ids)s;
        """,
        {
            "ids": tuple(messageIds)
        }
    )

def __getExisting(redditId):
    return DbDriver.ExecuteQuery(
                """ SELECT id
                    FROM mod_log
                    WHERE reddit_id = %(reddit_id)s;
                """,
                {
                    'reddit_id': redditId
                },
                "ModLog"
            ).fetchone()

def __insert(redditId, subredditId, modId, contributerId, action, description, details, targetTitle, targetName, targetRedditType, targetPermalink, dateCreated):
    DbDriver.ExecuteQuery(
            """ INSERT INTO mod_log(reddit_id, subreddit_id, mod_id, contributer_id, action, description, details, target_title, target_name, target_reddit_type, target_permalink, created)
                VALUES(%(reddit_id)s, %(subreddit_id)s, %(mod_id)s, %(contributer_id)s, %(action)s, %(description)s, %(details)s, %(target_title)s, %(target_name)s, %(target_reddit_type)s, %(target_permalink)s, %(created)s);
            """,
            {
                'reddit_id': redditId,
                'subreddit_id': subredditId,
                'mod_id': modId,
                'contributer_id': contributerId,
                'action': action,
                'description': description,
                'details': details,
                'target_title': targetTitle,
                'target_name': targetName,
                'target_reddit_type': targetRedditType,
                'target_permalink': targetPermalink,
                'created': dateCreated,
            },
            "ModLog"
        )
