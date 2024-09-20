from ..Data import Submissions, Contributers, Mods
from ..Data import Subreddits as DataSubreddits # For whatever reason, the Subreddits module was colliding and being overwritten by PRAW's Subreddits module.
from ImageProcessing import Utility as ImgUtil, Data as ImgData

def Get(Subreddits):
    # pause_after=1 => Number of requests with no results before the function yields None.
    for submission in Subreddits.stream.submissions(pause_after=1): 
        if(submission is None):
            break

        # If an author deletes their post before the bot gets to it, the post still comes through (for some reason) but with a bunch of None values.
        if (submission.author is None):
            continue

        contributerId = Contributers.Insert(submission.author.name)
        subredditId = DataSubreddits.Insert(submission.subreddit.display_name, submission.subreddit.id)
        actingMod = Mods.Insert(submission.approved_by) if submission.approved_by is not None else None
        submissionId, newSubmission = Submissions.Upsert(submission, contributerId, subredditId, actingMod)

        if newSubmission and ImgUtil.IsImage(submission.domain, submission.url):
            # Insert a record for processing. 
            # Set a default file name here as well, because it's easy enough to generate.
            fileNames = ImgUtil.GenerateFileNames(submission.url, submissionId)
            ImgData.Insert(submissionId, submission.url, fileNames[0])
