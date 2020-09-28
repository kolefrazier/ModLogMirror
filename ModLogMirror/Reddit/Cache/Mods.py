from Redis import Cache as RedisCache

keyPrefix = "mod-"

def Insert(username, recordId):
    RedisCache.set(f"{keyPrefix}{username}", recordId)
    print(f"Cached mod: {username} ({keyPrefix}{username})")

def Get(username):
    value = RedisCache.get(f"{keyPrefix}{username}")
    if not isinstance(value, int) and value is not None:
        value = int(value)

    return value
