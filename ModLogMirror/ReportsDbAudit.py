import copy
import csv

import Config.Environment as Conf
from Reddit import Enums as RedditEnums
from Reddit.Data import ReportsUser, Submissions, Comments

AllReports = ReportsUser.All(["id", "reddit_id", "reddit_type"])
print(f"Retrieved {len(AllReports)} reports")

OutputRows = []

# Process all records
for report in AllReports:
    Mapped = {
        "id": report[0],
        "reddit_id": report[1],
        "reddit_type": report[2]
    }

    # Output record
    # Default values are set here to reduce repeated, conditional assignments below.
    Output = copy.deepcopy(Mapped)
    Output["type_match"] = True
    Output["same_type_id"] = None
    Output["opposite_type_match"] = False
    Output["opposite_type_id"] = None
    Output["has_history"] = False

    TypeName = RedditEnums.NamedContentTypes(Mapped['reddit_type']).name

    if(TypeName == "Comment"):
        Record = Comments.Get(Mapped["reddit_id"])
    elif(TypeName == "Link"):
        Record = Submissions.Get(Mapped["reddit_id"])

    Output["same_type_id"] = Record[0]

    # Get report history (using AuthorHistory method)
    # then update Output["has_history"]
    # If no history, get opposite type (below), then check its history again.

    # If no record exists that matches, try retrieving the opposite.
    if Record == None:
        Output["type_match"] = False

        if(TypeName == "Comment"):
            Opposite = Submissions.Get(Mapped["reddit_id"])
        elif(TypeName == "Link"):
            Opposite = Comments.Get(Mapped["reddit_id"])

        Output["opposite_type_match"] = True if Opposite != None else False
        Output["opposite_type_id"] = Opposite[0]
    

    # Try retrieving from Reddit
    # TODO ...

    # Add to output
    OutputRows.append(Output)

# Save output to CSV
Keys = OutputRows[0].keys()
with open("report_mismatches.csv", "w", newline="") as OutputFile:
    writer = csv.DictWriter(OutputFile, fieldnames=Keys)
    writer.writeheader()
    writer.writerows(OutputRows)
