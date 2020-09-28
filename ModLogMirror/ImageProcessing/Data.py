import Database.DatabaseDriver as DbDriver

""" Data-layer wrapper class for Subreddits """

def Insert(submissionId, fileName):

    imageProc = __getExisting(submissionId)

    if (imageProc is None):
        inserted = __insert(submissionId, fileName)
        return inserted[0] # [0] = id
    else:
        return imageProc[0]

def getUnprocessed():
    return DbDriver.ExecuteQuery(
        """ SELECT id, file_name
            FROM image_processing
            WHERE parse_date IS NULL;
        """,
        {}
    ).fetchall()

def __getExisting(submissionId):
    return DbDriver.ExecuteQuery(
        """ SELECT id, submission_id, file_name, parse_date, parsed_text_raw, matched_text
            FROM image_processing
            WHERE submission_id = %(submissionId)s;
        """,
        {
            'submissionId': str(submissionId)
        }
    ).fetchone()

def __insert(submissionId, fileName):
    return DbDriver.ExecuteQuery(
        """ INSERT INTO image_processing(submission_id, file_name)
            VALUES(%(submission_id)s, %(file_name)s)
            RETURNING id;
        """,
        {
            'submission_id': submissionId,
            'file_name': fileName
        }
    ).fetchone()
