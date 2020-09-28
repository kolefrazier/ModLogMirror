from ..Data import Subreddits, Contributers, ModmailNew, ModmailNewMessage

def Get(subreddits):
    # New Modmail
    # New Modmail uses PRAW's ModmailConversation and ModmailMessage objects
    # Don't use ID length as an indicator for Old vs New Modmail.
    # Ref: https://www.reddit.com/r/redditdev/comments/gg705x/old_modmail_vs_new_modmail/

    for conversation in subreddits.modmail.conversations(limit=None, sort='unread'):
        if(conversation is None):
            break;

        firstMessageAuthor = conversation.messages[0].author.name
        contributerRecordId = Contributers.Insert(firstMessageAuthor)
        subredditId = Subreddits.Insert(conversation.owner.display_name, conversation.owner.id) # conversation.owner is the subreddit
        conversationId = ModmailNew.Insert(conversation, contributerRecordId, subredditId)

        # Insert messages from conversation. (Will skip if already in database.)
        for message in conversation.messages:
            ModmailNewMessage.Insert(message, conversationId, contributerRecordId)
        
        conversation.read()
