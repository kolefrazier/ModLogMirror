from datetime import datetime
import Database.DatabaseDriver as DbDriver

def Insert(message, conversationRecordId, contributerId):
    existingMessage = __getExisting(message.id)

    if (existingMessage is None):
        existingMessage = __insert(
            message.id,
            conversationRecordId, 
            contributerId, 
            message.body_markdown, 
            datetime.fromisoformat(message.date)
    )

    return existingMessage[0] # [0] = id

def __getExisting(redditId):
    return DbDriver.ExecuteQuery(
               """SELECT id, reddit_id
                   FROM modmail_messages
                   WHERE reddit_id = %(reddit_id)s;
               """,
            {
                   'reddit_id': redditId
            }
           ).fetchone()

def __insert(messageRedditId, modmailConversationId, contributerId, bodyMarkdown, messageDate):
    return DbDriver.ExecuteQuery(
                """INSERT INTO modmail_messages (reddit_id, modmail_conversation_id, contributer_id, body_markdown, message_date)
                    VALUES (%(reddit_id)s, %(modmail_conversation_id)s, %(contributer_id)s, %(body_markdown)s, %(message_date)s)
                    RETURNING id;
                """,
                {
                    'reddit_id': messageRedditId,
                    'modmail_conversation_id': modmailConversationId,
                    'contributer_id': contributerId,
                    'body_markdown': bodyMarkdown,
                    'message_date': messageDate
                }
            ).fetchone()
