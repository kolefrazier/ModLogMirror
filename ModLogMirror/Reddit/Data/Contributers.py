from datetime import datetime
import Reddit.Enums as RedditEnums
import Database.DatabaseDriver as DbDriver
from ..Cache import Contributers as ContributersCache

""" Data-layer wrapper for Contributers """

def Insert(username):
    # Use cached if available
    CachedId = ContributersCache.Get(username)

    if(CachedId is not None):
        return CachedId

    contributer = __getExisting(username)

    if (contributer is None):
        contributer = __insert(username)
    #else:
    #    contributer = __update(username, last_seen)

    ContributersCache.Insert(username, contributer[0])
    return contributer[0] # Return just the ID
        

def __getExisting(username):
    return DbDriver.ExecuteQuery(
               """ SELECT id, username
                   FROM contributers
                   WHERE username = %(username)s;
               """,
               {
                   'username': username
               },
                "Contributers"
           ).fetchone()

def __insert(username):
    return DbDriver.ExecuteQuery(
               """ INSERT INTO contributers(username)
                   VALUES(%(username)s)
                   RETURNING id;
               """,
               {
                   'username': username
               },
                "Contributers"
           ).fetchone()

#def __update(username, last_seen):
#    return DbDriver.ExecuteQuery(
#               """ UPDATE contributers
#                   SET last_seen = %(last_seen)s
#                   WHERE username = %(username)s
#                   RETURNING id;
#               """,
#               {
#                   'username': username,
#                   'last_seen': last_seen
#               }
#           ).fetchone()
