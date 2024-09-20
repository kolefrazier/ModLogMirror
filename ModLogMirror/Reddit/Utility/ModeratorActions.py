# Provides translations from Reddit's action strings.
#   Aims to translate action strings into easily read strings,
#   while standardizing "alloneword" and "some_action_word" into the
#   same format.
#
# See GET [/r/subreddit]/about/log endpoint notes for up to date list
#   Link: https://www.reddit.com/dev/api/#GET_about_log

# These actions are in no particular order. Just copied from the above-linked API doc.
_actions = {
    "banuser": "Ban User",
    "unbanuser": "Unban User",
    "spamlink": "Spam Link",
    "removelink": "Remove Link",
    "approvelink": "Approve Link",
    "spamcomment": "Spam Comment",
    "removecomment": "Remove Comment",
    "approvecomment": "Approve Comment",
    "addmoderator": "Add Moderator",
    "showcomment": "Show Comment",
    "invitemoderator": "Invite Moderator",
    "uninvitemoderator": "Uninvite Moderator",
    "acceptmoderatorinvite": "Accept Moderator Invite",
    "removemoderator": "Remove Moderator",
    "addcontributor": "Add Contributor",
    "removecontributor": "Remove Contributor",
    "editsettings": "Edit Settings",
    "editflair": "Edit Flair",
    "distinguish": "Distinguish",
    "marknsfw": "Mark NSFW",
    "wikibanned": "Wiki Banned",
    "wikicontributor": "Wiki Contributor",
    "wikiunbanned": "Wiki Unbanned",
    "wikipagelisted": "Wiki Page Listed",
    "removewikicontributor": "Remove Wiki Contributor",
    "wikirevise": "Wiki Revise",
    "wikipermlevel": "Wiki Perm Level",
    "ignorereports": "Ignore Reports",
    "unignorereports": "Unignore Reports",
    "setpermissions": "Set Permissions",
    "setsuggestedsort": "Set Suggested Sort",
    "sticky": "Sticky",
    "unsticky": "Unsticky",
    "setcontestmode": "Set Contest Mode",
    "unsetcontestmode": "Unset Contest Mode",
    "lock": "Lock",
    "unlock": "Unlock",
    "muteuser": "Mute User",
    "unmuteuser": "Unmute User",
    "createrule": "Create Rule",
    "editrule": "Edit Rule",
    "reorderrules": "Reorder Rules",
    "deleterule": "Delete Rule",
    "spoiler": "Spoiler",
    "unspoiler": "Unspoiler",
    "modmail_enrollment": "Modmail Enrollment",
    "community_styling": "Community Styling",
    "community_widgets": "Community Widgets",
    "markoriginalcontent": "Mark Original Content",
    "collections": "Collections",
    "events": "Events",
    "hidden_award": "Hidden Award",
    "add_community_topics": "Add Community Topics",
    "remove_community_topics": "Remove Community Topics",
    "create_scheduled_post": "Create Scheduled Post",
    "edit_scheduled_post": "Edit Scheduled Post",
    "delete_scheduled_post": "Delete Scheduled Post",
    "submit_scheduled_post": "Submit Scheduled Post",
    "edit_post_requirements": "Edit Post Requirements",
    "invitesubscriber": "Invite Subscriber",
    "submit_content_rating_survey": "Submit Content Rating Survey",
    "adjust_post_crowd_control_level": "Adjust Post Crowd Control Level",
    "deleteoverriddenclassification": "Delete Overridden Classification",
    "overrideclassification": "Override Classification",
    "snoozereports": "Snooze Reports",
    "addnote": "Add Note",
    "deletenote": "Delete Note",
    "disable_post_crowd_control_filter": "Disable Post Crowd Control Filter",
    "enable_post_crowd_control_filter": "Enable Post Crowd Control Filter",
    "reordermoderators": "Reorder Moderators",
    "unsnoozereports": "Unsnooze Reports",
}

def GetHumanReadableAction(key):
    global _actions

    if key in _actions.keys():
        return _actions[key]
    else:
        print(f"[Reddit.ModeratorActions.GetHumanReadableAction] Unknown key: {key}")
        return key