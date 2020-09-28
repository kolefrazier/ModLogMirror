from datetime import datetime
import Reddit.Enums as RedditEnums
import Database.DatabaseDriver as DbDriver
from Reddit.Data import Contributers, Subreddits
from ..Cache import ModmailNew as ModmailNewCache

def Insert(conversation, contributerId, subredditId):
    # Use cached, if available
    CachedId = ModmailNewCache.Get(conversation.id)
    
    if(CachedId is not None):
        return CachedId

    modmailConv = __getExisting(conversation.id)

    if (modmailConv is None):
        modmailConv = __insert(conversation.id, subredditId, contributerId, conversation.subject, conversation.is_internal, conversation.last_updated)

    ModmailNewCache.Insert(conversation.id, modmailConv[0])
    return modmailConv[0] # [0] = id

def __getExisting(conversationRedditId):
    return DbDriver.ExecuteQuery(
               """SELECT id, reddit_id
                   FROM modmail_conversations
                   WHERE reddit_id = %(reddit_id)s;
               """,
               {
                   'reddit_id': conversationRedditId
               }
           ).fetchone()

def __insert(conversationRedditId, subredditId, authorId, subject, is_internal, last_updated):
    return DbDriver.ExecuteQuery(
               """INSERT INTO modmail_conversations (reddit_id, subreddit_id, author_id, subject, is_internal, last_updated)
                   VALUES (%(reddit_id)s, %(subreddit_id)s, %(author_id)s, %(subject)s, %(is_internal)s, %(last_updated)s)
                   RETURNING id;
               """,
               {
                   'reddit_id': conversationRedditId,
                   'subreddit_id': subredditId,
                   'author_id': authorId,
                   'subject': subject,
                   'is_internal': is_internal,
                   'last_updated': last_updated
               }
           ).fetchone()
    

## ModmailConversation has zero-to-many ModmailMessages
#def UpsertModmailConversation(conversation, contributerId, subredditId):

#    if (Existing is None):
#        SubredditId = Subreddits.InsertSubreddit(conversation.owner.display_name, conversation.owner.id)['Id']

#        Existing = DbDriver.ExecuteQuery(
#            """INSERT INTO modmail_conversations (reddit_id, subreddit_id, author_id, subject, is_internal, last_updated)
#                VALUES (%(reddit_id)s, %(subreddit_id)s, %(author_id)s, %(subject)s, %(is_internal)s, %(last_updated)s)
#                RETURNING id;
#            """,
#            {
#                'reddit_id': conversation.id,
#                'subreddit_id': SubredditId,
#                'author_id': AuthorId,
#                'subject': conversation.subject,
#                'is_internal': conversation.is_internal,
#                'last_updated': conversation.last_updated
#            }
#        ).fetchone()
#    else:
#        # Update the last_updated value, as I believe this will indicate last activity on the conversation
#        DbDriver.ExecuteQuery(
#            """UPDATE modmail_conversations
#                SET last_updated = %(last_updated)s
#                WHERE id = %(existing_id)s;
#            """,
#            {
#                'existing_id': Existing[0],
#                'last_updated': conversation.last_updated
#            }
#        )

#    # Return the ID of the conversation
#    return Existing[0]

#def InsertModmailMessage(conversationId, message):
#    # ModmailConversations have zero-to-many ModmailMessages

#    AuthorId = Contributers.InsertContributer(message.author.name)['Id']

#    Existing = DbDriver.ExecuteQuery(
#        """SELECT id, reddit_id
#            FROM modmail_messages
#            WHERE reddit_id = %(reddit_id)s;""",
#        {
#            'reddit_id': message.id
#        }
#    ).fetchone()

#    # If it already exists, skip it. Conversations messages can't be udpated.
#    if (Existing is None):
#        AuthorId = InsertContributer(message.author.name)['Id']

#        DbDriver.ExecuteQuery(
#            """INSERT INTO modmail_messages (reddit_id, modmail_conversation_id, author_id, body_markdown, message_date)
#                VALUES (%(reddit_id)s, %(modmail_conversation_id)s, %(author_id)s, %(body_markdown)s, %(message_date)s)
#            """,
#            {
#                'reddit_id': message.id,
#                'modmail_conversation_id': conversationId,
#                'author_id': AuthorId,
#                'body_markdown': message.body_markdown,
#                'message_date': message.date
#            }
#        )

