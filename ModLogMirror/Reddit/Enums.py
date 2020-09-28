# Notes and References
#   * Official Docs: Programmatic access to enum members and attributes: https://docs.python.org/3/library/enum.html#programmatic-access-to-enumeration-members-and-their-attributes

from enum import Enum

"""Reddit enums helper - Provides utility functions for Reddit enums. """
__TypeStrings = ["Comment", "Account", "Link", "Message", "Subreddit", "Award"]
__StatusStrings = ["Unmoderated", "Approved", "Removed", "Reported"]

# Private Methods
def _GetRawTypeFromIDString(IDString):
    if("_" in IDString):
        SplitResult = IDString.split("_")[0]
        try:
            return RawContentTypes[SplitResult]
        except:
            return None
    else:
        return None

def _GetRawIDFromIDString(IDString):
    if("_" in IDString):
        try:
            return IDString.split("_")[1]
        except:
            return None
    else:
        return None

# Public Methods
def GetStringForType(RedditEnum):
    try:
        return __TypeStrings[RedditEnum]
    except Exception as e:
        return None

# TODO: Review necessity. thing.id exists on PRAW objects. (Might be useful in "lookup from stored reddit_id" scenarios?)
def GetIDFromFullIDString(IDString): #Okay, not an enum... But it fits in here with the other, similar methods... for now?
    return _GetRawIDFromIDString(IDString)

def GetTypeEnumFromIDString(IDString):
    try:
        return _GetRawTypeFromIDString(IDString)
    except Exception as e:
        return None

def GetNamedTypeFromIDString(IDString):
    RawType = _GetRawTypeFromIDString(IDString)
    if(RawType is not IDString):
        return RawType
    else:
        return None

def GetSubmissionStatusFromInt(number):
    return SubmissionStatus[number]

def GetStatusFromSubmissionObject(Submission):
    Status = SubmissionStatus.Unmoderated
    if(Submission.removal_reason is not None):
        Status = SubmissionStatus.Removed
    elif(Submission.approved_by is not None and Submission.approved_at_utc is not None):
        Status = SubmissionStatus.Approved

    return Status

class NamedContentTypes(Enum):
    """Enums representing Reddit's content types"""
    Comment = 0
    Account = 1
    Link = 2
    Message = 3
    Subreddit = 4
    Award = 5

class RawContentTypes(Enum):
    """Enums representing Reddit's raw content types found in item ID strings."""
    #Source: https://www.reddit.com/dev/api/
    t1 = 0  #Comment
    t2 = 1  #Account
    t3 = 2  #Link
    t4 = 3  #Message
    t5 = 4  #Subreddit
    t6 = 5  #Award

class SubmissionStatus(Enum):
    """Enums representing submission status states"""
    Unmoderated = 0
    Approved = 1
    Removed = 2
    Reported = 3 #As in "Has Reports"