from datetime import datetime
from ..Cache import Mods as ModsCache
import Database.DatabaseDriver as DbDriver

""" Data-layer wrapper for Mods """

def Insert(username):
    # Use cached if available
    CachedId = ModsCache.Get(username)

    if(CachedId is not None):
        return CachedId

    mod = __getExisting(username)

    # If not found, insert and return the values
    if (mod is None):
        mod = __insert(username) 

    # mod[0] = row id
    ModsCache.Insert(username, mod[0])
    return mod[0] # Return just the ID

def __getExisting(username):
    return DbDriver.ExecuteQuery(
                """SELECT id, username
                    FROM moderators
                    WHERE username = %(username)s;""",
                {
                    'username': username
                },
                "Mods"
            ).fetchone()

def __insert(username):
    return DbDriver.ExecuteQuery(
                """INSERT INTO moderators(username) 
                VALUES(%(username)s)
                RETURNING id, username""", 
                {
                    'username': username
                },
                "Mods"
            ).fetchone()

#def __update(username, last_seen):
#    return DbDriver.ExecuteQuery(
#                """UPDATE moderators
#                    SET last_seen = %(last_seen)s
#                    WHERE username = %(username)s
#                    RETURNING id, username;""",
#                {
#                    'username': username,
#                    'last_seen': last_seen
#                }
#            ).fetchone()
