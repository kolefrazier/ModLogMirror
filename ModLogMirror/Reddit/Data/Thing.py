from praw.models import Submission, Comment
from Reddit.Data import Submissions, Comments

def UpsertForType(thing, contributerId, subredditId, actingMod):
    """ Upsert router for generic type 'Thing', where the given something is a 'thing' (submissions, comments) """

    if isinstance(thing, Submission):
        Submissions.Upsert(thing, contributerId, subredditId, actingMod)
    elif isinstance(thing, Comment):
        Comments.Upsert(thing, contributerId, subredditId)
