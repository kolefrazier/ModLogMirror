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

def __getExisting(redditId):
    return DbDriver.ExecuteQuery(
                """ SELECT id
                    FROM mod_log
                    WHERE reddit_id = %(reddit_id)s;
                """,
                {
                    'reddit_id': redditId
                }
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
            }
        )
