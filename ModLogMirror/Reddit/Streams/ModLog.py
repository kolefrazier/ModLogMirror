from ..Data import Subreddits, Contributers, Mods, ModLog

def Get(subreddits):
    # I might want to look into caching the log entries (redis or even a local of the last 200?) to prevent rechecking the same 25+ entries each pull
    for entry in subreddits.mod.stream.log(pause_after=1):
        if (entry is None):
            break

        subredditId = Subreddits.Insert(entry.subreddit, entry.sr_id36)
        contributerId = Contributers.Insert(entry.target_author)
        modId = Mods.Insert(entry.mod.name)
        ModLog.Insert(entry, subredditId, modId, contributerId)
