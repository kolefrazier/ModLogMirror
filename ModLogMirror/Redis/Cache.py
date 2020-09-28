import redis
import Config.Redis as c

_redis = redis.Redis(host=c.Host, port=c.Port, password=c.Password, db=0)
_expire = 14400 # 14,400 seconds == 4 hours in seconds

# Debug Stats
_setOperations = 0
_getOperations = 0

def printStats():
    global _setOperations, _getOperations
    print(f"[Redis] Gets: {_getOperations}\tSets: {_setOperations}")

def resetStats():
    global _setOperations, _getOperations
    _setOperations = 0
    _getOperations = 0

def _secondsForHours(hours):
    return hours*3600

Expires = {
    "Default": _secondsForHours(4),
    "Mods": _secondsForHours(24),
    "Subreddits": _secondsForHours(24),
    "Reports": _secondsForHours(12)
}

# Redis.py documentation: https://redis-py.readthedocs.io/en/stable/
# Redis commands documentation: https://redis.io/commands

# Set `key` to hold the string `value`.
#   If the key already exists, it is overwritten, regardless of its type.
#   Any previous TTL for the key is discarded, too.
# Ref: https://redis-py.readthedocs.io/en/stable/#redis.Redis.set
# Ref: https://redis.io/commands/set
def set(key, value, expiration=Expires["Default"]):
    global _setOperations
    _redis.set(key, value, expiration)
    _setOperations += 1

# Get the value for the given key.
#   If key does not exist, None is returned.
# Ref: https://redis-py.readthedocs.io/en/stable/#redis.Redis.get
# Ref: https://redis.io/commands/get
def get(key, resetExpire = True):
    global _getOperations
    if resetExpire:
        _redis.expire(key, Expires["Default"])

    _getOperations += 1
    return _redis.get(key)

# Get a list of keys matching `pattern`
#   Default pattern is: u"*"
# Ref: https://redis-py.readthedocs.io/en/stable/#redis.Redis.keys
# Ref: https://redis.io/commands/keys
def keys(pattern=None):
    if (pattern is None):
        return _redis.keys()
    else:
        return _redis.keys(pattern)

# Remove existing timeout on key, turning the key from volatile to persistent.
# Ref: https://redis-py.readthedocs.io/en/stable/#redis.Redis.persist
# Ref: https://redis.io/commands/persist
def persist(key):
    _redis.persist(key)
