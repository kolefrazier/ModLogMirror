from ..Data import Subreddits, Contributers, ModmailOld

def Get(subreddits):
    # Old Modmail - Stream
    # Old Modmail uses PRAW's Message object
    # Ref: https://praw.readthedocs.io/en/latest/code_overview/other/subredditmoderationstream.html
    for mail in subreddits.mod.stream.unread(pause_after=1):
        if(mail is None):
            break

        subredditId = Subreddits.Insert(mail.subreddit.display_name, mail.subreddit.id)
        contributerId = Contributers.Insert(mail.author.name)
        ModmailOld.Insert(mail, subredditId, contributerId)
        mail.mark_read()
