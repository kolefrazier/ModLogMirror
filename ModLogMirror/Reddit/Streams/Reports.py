from ..Data import Subreddits, Contributers, Thing, ReportsUser, ReportsMod, Mods

def Get(subreddits):
    for report in subreddits.mod.stream.reports(pause_after=1):
        if (report is None):
            break

        subredditId = Subreddits.Insert(report.subreddit.display_name, report.subreddit.id)
        contributerId = Contributers.Insert(report.author.name)
        actingMod = Mods.Insert(report.approved_by) if report.approved_by is not None else None
        Thing.UpsertForType(report, contributerId, subredditId, actingMod)

        if (len(report.user_reports) > 0):
            ReportsUser.Upsert(report, subredditId)

        if (len(report.mod_reports) > 0):
            ReportsMod.Upsert(report, subredditId)
