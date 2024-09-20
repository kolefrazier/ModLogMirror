import json
from datetime import datetime
import Database.DatabaseDriver as DbDriver

""" Data-layer wrapper class for Subreddits """

def Insert(submissionId, url, fileName):
    """ Inserts the given submission and its data into the image_processing table. """
    imageProc = __getExisting(submissionId)

    if (imageProc is None):
        inserted = __insert(submissionId, url, fileName)
        return inserted[0] # [0] = id
    else:
        return imageProc[0]

def GetAny():
    """ Get the very first record. Used to check if the table is empty or not. """
    return DbDriver.ExecuteQuery(
        """ SELECT id
            FROM image_processing
            ORDER BY id ASC LIMIT 1
        """
    ).fetchall()

def GetUnprocessed():
    """ Get all records that have not been processed. If it has been processed or attempted to be processed, it will not be returned. """
    return DbDriver.ExecuteQuery(
        """ SELECT id, submission_id, url, file_name
            FROM image_processing
            WHERE parse_date IS NULL
            AND processing_attempted = false
            AND file_name IS NOT NULL;
        """
    ).fetchall()

def GetResults(submissionId):
    """ Get raw and match results for the given submission ID. (Reddit ID, not row ID.) """
    Results = DbDriver.ExecuteQuery(
        """ SELECT s.title, s.content, ip.file_name, ip.file_hash, ip.parse_date, ip.tesseract_raw_output, ip.matched_text, ip.errors
            FROM image_processing ip
            JOIN submissions s ON ip.submission_id = s.id
            WHERE s.reddit_id = %(submission_id)s
            AND ip.processing_attempted = true;
        """,
        {
            "submission_id": submissionId
        }
    ).fetchall()

    # Early return None when no results
    if len(Results) == 0:
        return None

    Image = Results[0]
    return {
        "submission_title": Image[0],
        "submission_content": Image[1],
        "image_file_name": Image[2],
        "image_hash": Image[3],
        "image_parse_date": Image[4],
        "image_tesseract_raw": json.loads(Image[5]),
        "image_tesseract_match": json.loads(Image[6]),
        "image_errors": Image[7]
    }

def MarkNotified(ids):
    """ Set discord_notified to true for all given IDs. """
    DbDriver.ExecuteQuery(
        """ UPDATE image_processing
            SET discord_notified = true
            WHERE id IN %(ids)s
            OR (
              matched_text = null
              AND processing_attempted = true
              AND discord_notified = false
            );
        """,
        {
            "ids": tuple(ids)
        }
    )

def GetUnnotified(subId):
    """ Get all records that have false for discord_notified. """
    QueryResults = DbDriver.ExecuteQuery(
        """ SELECT ip.id, ip.url, ip.matched_text, s.reddit_id
            FROM image_processing ip
            JOIN submissions s ON ip.submission_id = s.id
            WHERE ip.discord_notified = false
            AND s.subreddit_id = %(subreddit_id)s
            AND ip.processing_attempted = true;
        """,
        {
            "subreddit_id": str(subId)
        }
    ).fetchall()

    Processed = []
    for result in QueryResults:
        MatchedText = None
        if result[2] != None:
            MatchedText = json.loads(result[2])

        Processed.append({
            "id": result[0],
            "url": result[1],
            "matched_text": MatchedText,
            "reddit_id": result[3]
        })

    return Processed

def UpdateResults(id, matchedTextJson, tesseractRawOutput, fileHash):
    """ Update the given record, updating tesseract results and other file data. """
    if matchedTextJson != None:
        matchedTextJson = json.dumps(matchedTextJson)

    return DbDriver.ExecuteQuery(
        """ UPDATE image_processing
            SET parse_date = %(parse_date)s, tesseract_raw_output = %(tesseract_raw_output)s, matched_text = %(matched_text)s, file_hash = %(file_hash)s, processing_attempted = true
            WHERE id = %(id)s;
        """,
        {
            "parse_date": str(datetime.utcnow()),
            "tesseract_raw_output": json.dumps(tesseractRawOutput),
            "matched_text": matchedTextJson,
            "file_hash": fileHash,
            "id": str(id)
        }
    )

def UpdateError(id, error):
    """ Update the given record with error text from processing errors. """
    return DbDriver.ExecuteQuery(
        """ UPDATE image_processing
            SET parse_date = %(parse_date)s, errors = %(errors)s, processing_attempted = true
            WHERE id = %(id)s;
        """,
        {
            "parse_date": str(datetime.utcnow()),
            "errors": str(error),
            "id": str(id)
        }
    )

def GetPrePurgeInfo(redditId):
    """ Purges certain information from the record. Intended for sanitization purposes. """
    Result = DbDriver.ExecuteQuery(
        """ SELECT ip.id, ip.file_name
            FROM image_processing ip
            JOIN submissions s ON ip.submission_id = s.id
            WHERE s.reddit_id = %(reddit_id)s
            AND ip.matched_text != 'PURGED';
        """,
        {
            "reddit_id": redditId
        }
    ).fetchone()

    Processed = None
    if len(Result) > 0:
        Processed = {
            "id": Result[0],
            "file_name": Result[1]
        }
    return Processed

def PurgeRecord(redditId):
    """ Purges certain information from the record. Intended for sanitization purposes. """
    DbDriver.ExecuteQuery(
        """ UPDATE image_processing AS ip
            SET ip.url = NULL, ip.tesseract_raw_output = NULL, ip.matched_text = 'PURGED', ip.errors = 'PURGED', ip.processing_attempted = true, ip.parse_date = %(purgeDate)s, s.content = ''
            FROM submissions AS s
            WHERE ip.submission_id = s.id
            AND s.reddit_id = %(reddit_id)s;
        """,
        {
            "reddit_id": redditId,
            "purgeDate": str(datetime.utcnow())
        }
    )

def __getExisting(submissionId):
    """ Private, get a record by its submission ID. """
    return DbDriver.ExecuteQuery(
        """ SELECT id, submission_id, file_name, parse_date, tesseract_raw_output, matched_text
            FROM image_processing
            WHERE submission_id = %(submissionId)s;
        """,
        {
            "submissionId": str(submissionId)
        },
        "ImageProcessing"
    ).fetchone()

def __insert(submissionId, url, fileName):
    """ Insert a new record into image_processing. """
    return DbDriver.ExecuteQuery(
        """ INSERT INTO image_processing(submission_id, url, file_name)
            VALUES(%(submission_id)s, %(url)s, %(file_name)s)
            RETURNING id;
        """,
        {
            "submission_id": submissionId,
            "url": url,
            "file_name": fileName
        },
        "ImageProcessing"
    ).fetchone()
