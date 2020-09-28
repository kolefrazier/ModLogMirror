from Redis import Cache as RedisCache

def Insert(username, recordId):
    RedisCache.set(username, recordId)
    print(f"Cached contributer: {username}")

def Get(username):
    value = RedisCache.get(username)
    if value is not None and not isinstance(value, int):
        value = int(value)

    return value
