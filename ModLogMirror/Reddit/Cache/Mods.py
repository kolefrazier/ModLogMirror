from Redis import Cache as RedisCache

keyPrefix = "mod-"
keyPrefixDbId = "mod-db-"

def Insert(username, recordId):
    RedisCache.set(f"{keyPrefix}{username}", recordId) # Example: mod-foo
    RedisCache.set(f"{keyPrefixDbId}{recordId}", username) # Example: mod-db-1
    print(f"Cached mod: {username} ({keyPrefix}{username})")

def Get(username):
    value = RedisCache.get(f"{keyPrefix}{username}")
    if not isinstance(value, int) and value is not None:
        value = int(value)

    return value

# Get the mod based on the Database ID
# Useful when retrieving records with a mod ID.
# (Used in getting submissions, where joins get iffy due to submissions.approved_by being nullable.
#   I couldn't figure out a clean query to get all rows when approved_by values were null AND not null.)
def GetByDatabaseId(id):
    # Returned without value checking, as we know we want a string and Redis will return a string.
    return RedisCache.get(f"{keyPrefixDbId}{id}")
