def TrimContent(content, sliceLength=10):
    CleanSplit = content.replace("\n", " ").split(" ")

    # Then use slice notation ([:stop]) to get the first 10 words. 
    # (Does not error if less than N elements in list.)
    Output = " ".join(CleanSplit[:sliceLength])
    
    if len(CleanSplit) > sliceLength:
        Output += "..."
    
    return Output

def FormattedSubstring(content, characterLength=250, ellipses=True):
    trimmed = content[0:characterLength]
    if len(content) > characterLength and ellipses:
        trimmed += "..."
    return trimmed

def IdListToSQLValueString(messageIds):
    if type(messageIds) is not list:
        raise "[Reddit.Data.ModmailOld.MarkNotifed()] Parameter messageIds must a list."

    # Using a list comprehension, cast the id to a string (.join() only takes in strings),
    #   format the id in parenthesis (for SQL syntax), then join them all into one string.
    # Example:
    #   Input: [1,2,3]
    #   Output: '(1),(2),(3)'
    return ",".join([f"({str(id)})" for id in messageIds])

def SanitizeUsername(name):
    return name.replace("_", "\_") # Underscore pairs result in italicized text.
