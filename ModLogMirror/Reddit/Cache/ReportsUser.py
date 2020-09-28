from Redis import Cache as RedisCache

keyPrefixReport = "rep-"
keyPrefixCount = "repCount-"

def Insert(redditId, recordId, totalReports):
    RedisCache.set(f"{keyPrefixReport}{redditId}", recordId, RedisCache.Expires['Reports'])
    RedisCache.set(f"{keyPrefixCount}{redditId}", totalReports, RedisCache.Expires['Reports'])
    print(f"Cached report thing: {redditId} ({keyPrefixReport}{redditId}: {recordId} | {keyPrefixCount}{totalReports}) ")

def Get(redditId):
    reportRecordId = RedisCache.get(f"{keyPrefixReport}{submissionRedditId}")
    reportReportCount = RedisCache.get(f"{keyPrefixCount}{submissionRedditId}")

    if not isinstance(reportRecordId, int) and reportRecordId is not None:
        reportRecordId = int(reportRecordId)

    if not isinstance(reportReportCount, int) and reportReportCount is not None:
        reportReportCount = int(reportReportCount)

    return {
        "recordId": reportRecordId,
        "reportCount": reportReportCount
    }