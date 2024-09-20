from datetime import datetime
import json
import Reddit.Enums as RedditEnums
import Database.DatabaseDriver as DbDriver
from ..Cache import ReportsUser as ReportsCache
from praw.models import Submission, Comment

def Upsert(report, subredditId):
    existingReport = __getExisting(report.id)

    # Reports are lists-of-lists - a list of reports (['reason', int_count])
    # Use a list comprehension to extract all of the count values, then sum them.
    totalReports = sum([user_report[1] for user_report in report.user_reports])
    mappedReports = [{"reason": report[0], "count": report[1]} for report in report.user_reports]

    if (existingReport is None):
        redditType = None # For future protection or something. This way unknown types (or, more likely, incorrectly handled types) can be handled later.

        # TODO: Investigate weirdness around this. Some items are stored with the wrong type.
        #   eg, as comments when the reddit_id is for a submission.
        #   (See Reports Discord cog to see where it's affecting things.)
        if isinstance(report, Submission):
            redditType = RedditEnums.NamedContentTypes.Link.value
        elif isinstance(report, Comment):
            redditType = RedditEnums.NamedContentTypes.Comment.value

        createdTimestamp = datetime.utcfromtimestamp(report.created_utc)

        recordId = __insert(report.id, redditType, subredditId, mappedReports, totalReports, createdTimestamp)
        ReportsCache.Insert(report.id, recordId, totalReports)
    elif totalReports > existingReport["total_reports"]:
        # I believe reports are additive (only appends to list, does not clear list). So just updating the record values should do the trick.
        __update(existingReport["id"], mappedReports, totalReports)
        ReportsCache.Insert(report.id, existingReport["id"], totalReports)

def GetUnnotified(subredditId):
    QueryResults = DbDriver.ExecuteQuery(
        """SELECT id, reddit_id, reddit_type, report_content, total_reports, first_notification
            FROM reports_user
            WHERE subreddit_id = %(subredditId)s
            AND discord_notified = false;
        """,
        {
            "subredditId": subredditId
        }
    ).fetchall()

    ReportEntries = []
    for entry in QueryResults:
        ReportEntries.append({
            "id": entry[0],
            "reddit_id": entry[1],
            "reddit_type": entry[2],
            "report_content": entry[3],
            "total_reports": entry[4],
            "first_notification": entry[5]
        })

    return ReportEntries

def MarkNotified(reportIds):
    DbDriver.ExecuteQuery(
        """UPDATE reports_user
           SET discord_notified = true, first_notification = true
           WHERE id IN %(ids)s;
        """,
        {
            "ids": tuple(reportIds)
        }
    )

def GetCommentReportsAndAuthor(reddit_id, days_ago):
    # IMPORTANT: Keep this query in sync with GetSubmissionReportsAndAuthor below
    query = f""" SELECT cr.username, SUM(r.total_reports), COUNT(*)
                 FROM reports_user r
                 JOIN comments cmt ON cmt.reddit_id = r.reddit_id
                 JOIN contributers cr ON cr.id = cmt.contributer_id
                 WHERE cmt.reddit_id = %(reddit_id)s
                 AND cmt.created >= (CURRENT_DATE - '{days_ago} days'::interval)
                 AND r.created >= (CURRENT_DATE - '{days_ago} days'::interval)
                 GROUP BY r.reddit_id, cr.username"""

    result = DbDriver.ExecuteQuery(
        query,
        {
            "reddit_id": reddit_id
        },
        "ReportsUser"
    ).fetchone()

    if result == None:
        return None
    else:
        return {
            "username": result[0],
            "total_reports": result[1],
            "reported_items": result[2]
        }

def GetSubmissionReportsAndAuthor(reddit_id, days_ago):
    # IMPORTANT: Keep this query in sync with GetCommentReportsAndAuthor above
    query = f""" SELECT cr.username, SUM(r.total_reports), COUNT(*)
                 FROM reports_user r
                 JOIN submissions s ON s.reddit_id = r.reddit_id
                 JOIN contributers cr ON cr.id = s.contributer_id
                 WHERE s.reddit_id = %(reddit_id)s
                 AND s.submission_date >= (CURRENT_DATE - '{days_ago} days'::interval)
                 AND r.created >= (CURRENT_DATE - '{days_ago} days'::interval)
                 GROUP BY r.reddit_id, cr.username"""

    result = DbDriver.ExecuteQuery(
        query,
        {
            "reddit_id": reddit_id,
            "interval": days_ago
        },
        "ReportsUser"
    ).fetchone()
    
    if result == None:
        return None
    else:
        return {
            "username": result[0],
            "total_reports": result[1],
            "reported_items": result[2]
        }

def All(columns="*"):
    query = f"SELECT {','.join(columns)} FROM reports_user"

    return DbDriver.ExecuteQuery(query,{},"ReportsUser").fetchall()

def __getExisting(reportRedditId):
    record = DbDriver.ExecuteQuery(
                """SELECT id, total_reports
                    FROM reports_user
                    WHERE reddit_id = %(reddit_id)s;
                """,
                {
                    'reddit_id': reportRedditId
                },
                "ReportsUser"
            ).fetchone()

    if record is None:
        return None
    else:
        return {
            "id": record[0],
            "total_reports": record[1]
        }

def __insert(reportRedditId, redditType, subredditId, reportContentJson, totalReports, created):
    return DbDriver.ExecuteQuery(
                """INSERT INTO reports_user (reddit_id, reddit_type, subreddit_id, report_content, total_reports, created, last_updated)
                    VALUES (%(reddit_id)s, %(reddit_type)s, %(subreddit_id)s, %(report_content)s, %(total_reports)s, %(created)s, %(last_updated)s)
                    RETURNING id;
                """,
                {
                    'reddit_id': reportRedditId,
                    'reddit_type': str(redditType),
                    'subreddit_id': subredditId,
                    'report_content': json.dumps(reportContentJson),
                    'total_reports': totalReports,
                    'created': str(created),
                    'last_updated': str(created)
                },
                "ReportsUser"
            ).fetchone()[0]

def __update(reportRecordId, reportContentJson, totalReports, lastUpdated=str(datetime.utcnow())):
    DbDriver.ExecuteQuery(
                """UPDATE reports_user
                    SET report_content = %(report_content)s,
                        total_reports = %(total_reports)s,
                        last_updated = %(last_updated)s,
                        discord_notified = FALSE
                    WHERE id = %(existing_id)s;
                """,
                {
                    'existing_id': reportRecordId,
                    'last_updated': str(datetime.utcnow()),
                    'report_content': json.dumps(reportContentJson),
                    'total_reports': totalReports,
                },
                "ReportsUser"
            )
