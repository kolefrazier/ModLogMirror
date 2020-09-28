from Redis import Cache as RedisCache

keyPrefix = "mmc-" #mmc = Modmail Conversation

def Insert(conversationId, recordId):
    RedisCache.set(f"{keyPrefix}{conversationId}", recordId)

def Get(conversationId):
    value = RedisCache.get(f"{keyPrefix}{conversationId}")
    if not isinstance(value, int) and value is not None:
        value = int(value)

    return value
