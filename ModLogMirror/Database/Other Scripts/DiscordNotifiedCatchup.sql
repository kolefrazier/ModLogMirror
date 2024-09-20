-- Sets the "DiscordNotified" column on specific tables to true. Intended to help reduce notification spam in catch-up scenarios.

UPDATE submissions SET discord_notified = true;
UPDATE reports_user SET discord_notified = true;
UPDATE reports_moderator SET discord_notified = true;
UPDATE modmail_conversations SET discord_notified = true;
UPDATE modmail_messages SET discord_notified = true;
UPDATE modmail_old_messages SET discord_notified = true;
UPDATE comments SET discord_notified = true;
UPDATE mod_log SET discord_notified = true;
UPDATE image_processing SET discord_notified = true;
