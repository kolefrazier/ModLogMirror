from datetime import datetime
import Reddit.Enums as RedditEnums
import Database.DatabaseDriver as DbDriver
from ..Cache import ReportsUser as ReportsCache
from praw.models import Submission, Comment

def Upsert(report, subredditId):
    existingReport = __getExisting(report.id)

    # Reports are lists-of-lists - a list of reports (['reason', int_count])
    # Use a list comprehension to extract all of the count values, then sum them.
    totalReports = sum([user_report[1] for user_report in report.user_reports])

    if (existingReport is None):
        redditType = None # For future protection or something. This way unknown types (or, more likely, incorrectly handled types) can be handled later.

        if isinstance(report, Submission):
            redditType = RedditEnums.NamedContentTypes.Link.value
        elif isinstance(report, Comment):
            redditType = RedditEnums.NamedContentTypes.Comment.value

        createdTimestamp = datetime.utcfromtimestamp(report.created_utc)

        recordId = __insert(report.id, redditType, subredditId, report.user_reports, totalReports, createdTimestamp)
        ReportsCache.Insert(report.id, recordId, totalReports)
    elif totalReports > existingReport["total_reports"]:
        # I believe reports are additive (only appends to list, does not clear list). So just updating the record values should do the trick.
        __update(existingReport["id"], report.user_reports, totalReports)
        ReportsCache.Insert(existingReport["id"], recordId, totalReports)

def __getExisting(reportRedditId):
    record = DbDriver.ExecuteQuery(
                """SELECT id, total_reports
                    FROM reports_user
                    WHERE reddit_id = %(reddit_id)s;
                """,
                {
                    'reddit_id': reportRedditId
                }
            ).fetchone()

    if record is None:
        return None
    else:
        return {
            "id": record[0],
            "total_reports": record[1]
        }

def __insert(reportRedditId, redditType, subredditId, reportContent, totalReports, created):
    return DbDriver.ExecuteQuery(
                """INSERT INTO reports_user (reddit_id, reddit_type, subreddit_id, report_content, total_reports, created, last_updated)
                    VALUES (%(reddit_id)s, %(reddit_type)s, %(subreddit_id)s, %(report_content)s, %(total_reports)s, %(created)s, %(last_updated)s)
                    RETURNING id;
                """,
                {
                    'reddit_id': reportRedditId,
                    'reddit_type': str(redditType),
                    'subreddit_id': subredditId,
                    'report_content': str(reportContent),
                    'total_reports': totalReports,
                    'created': str(created),
                    'last_updated': str(created)
                }
            ).fetchone()[0]

def __update(reportRecordId, reportContent, totalReports, lastUpdated=str(datetime.utcnow())):
    DbDriver.ExecuteQuery(
                """UPDATE reports_user
                    SET report_content = %(report_content)s,
                        total_reports = %(total_reports)s,
                        last_updated = %(last_updated)s,
                        discord_notified = FALSE
                    WHERE id = %(existing_id)s;
                """,
                {
                    'existing_id': existing[0],
                    'last_updated': str(datetime.utcnow()),
                    'report_content': str(updated.user_reports),
                    'total_reports': totalReports,
                }
            ).fetchone()
