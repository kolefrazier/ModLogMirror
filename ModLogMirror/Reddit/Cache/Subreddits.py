from Redis import Cache as RedisCache

keyPrefix = "r-"

def Insert(name, recordId):
    RedisCache.set(f"{keyPrefix}{name}", recordId)
    print(f"Cached mod: {name} ({keyPrefix}{name})")

def Get(name):
    value = RedisCache.get(f"{keyPrefix}{name}")
    if value is not None and not isinstance(value, int):
        value = int(value)

    return value
