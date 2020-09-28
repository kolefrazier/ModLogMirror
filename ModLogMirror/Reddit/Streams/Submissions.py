from ..Data import Submissions, Contributers, Mods
from ..Data import Subreddits as DataSubreddits # For whatever reason, the Subreddits module was colliding and being overwritten by PRAW's Subreddits module.
from ImageProcessing import Utility as ImgUtil, Data as ImgData

def Get(Subreddits):
    for submission in Subreddits.stream.submissions(pause_after=1): #pause_after=1 => Number of requests with no results before the function yields None.
        if(submission is None):
            break

        contributerId = Contributers.Insert(submission.author.name)
        subredditId = DataSubreddits.Insert(submission.subreddit.display_name, submission.subreddit.id)
        actingMod = Mods.Insert(submission.approved_by) if submission.approved_by is not None else None
        submissionId = Submissions.Upsert(submission, contributerId, subredditId, actingMod)

        if ImgUtil.isImage(submission.domain, submission.url):
            fileName, fileNameInverted = ImgUtil.generateFileNames(submission.url, submissionId)
            try:
                # Try to get the image. If this fails, it will skip adding it to the database, hopefully skipping any data integrity problems for the parser.
                ImgUtil.getImage(submission.url, fileName, fileNameInverted)
                ImgData.Insert(submissionId, fileName)
            except Exception as e:
                print(str(e))
