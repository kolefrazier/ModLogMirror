import praw
from ..Cache import Subreddits as SubredditsCache
import Database.DatabaseDriver as DbDriver

""" Data-layer wrapper class for Subreddits """

def Insert(name, id):
    # Use cached, if available
    CachedId = SubredditsCache.Get(name)

    if (CachedId is not None):
        return CachedId

    sub = __getExisting(name)

    if (sub is None):
        sub = __insert(name, id)

    SubredditsCache.Insert(name, sub[0])
    return sub[0] # [0] = id

# Gets subreddit ID (database ID, not reddit ID) by the name of the sub
def GetIdByName(name):
    # Use cached, if available
    CachedId = SubredditsCache.Get(name)

    if (CachedId is not None):
        return CachedId

    sub = __getExisting(name)
    if sub == None:
        raise Exception(f"[Reddit.Data.Subreddits.GetIdByName] No ID found for subreddit {name}. Was the database reset?")

    return sub[0] # [0] = id

def __getExisting(name):
    return DbDriver.ExecuteQuery(
        """ SELECT id, subreddit_name, reddit_id
            FROM subreddits
            WHERE subreddit_name = %(subreddit_name)s;
        """,
        {
            'subreddit_name': name
        },
        "Subreddits"
    ).fetchone()

def __insert(name, id):
    return DbDriver.ExecuteQuery(
        """ INSERT INTO subreddits(subreddit_name, reddit_id)
            VALUES(%(subreddit_name)s, %(subreddit_id)s)
            RETURNING id, subreddit_name, reddit_id
        """,
        {
            'subreddit_name': name,
            'subreddit_id': id
        },
        "Subreddits"
    ).fetchone()
