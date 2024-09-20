CREATE TABLE contributers (
  id SERIAL PRIMARY KEY,
  username TEXT UNIQUE,
  last_seen TIMESTAMPTZ -- IMPORTANT: PG will store Timestamps WITH Timezone as UTC values. Thus, TIMESTAMPTZ is correct.
);

CREATE INDEX idx_contributers_username ON contributers(username);

CREATE TABLE moderators (
  id SERIAL PRIMARY KEY,
  username TEXT UNIQUE
);

CREATE INDEX idx_moderators_username ON moderators(username);

CREATE TABLE subreddits (
  id SERIAL PRIMARY KEY,
  subreddit_name TEXT UNIQUE,
  reddit_id TEXT UNIQUE
);

CREATE INDEX idx_subreddits_subreddit_name ON subreddits(subreddit_name);
CREATE INDEX idx_subreddits_reddit_id ON subreddits(reddit_id);

CREATE TABLE submissions (
  id SERIAL PRIMARY KEY,
  reddit_id TEXT UNIQUE,
  reddit_type INTEGER,
  subreddit_id INTEGER REFERENCES subreddits(id),
  title TEXT,
  content TEXT,
  domain TEXT,
  flair_text TEXT,
  contributer_id INTEGER REFERENCES contributers(id),
  submission_status INTEGER,
  submission_date TIMESTAMPTZ,
  last_updated TIMESTAMPTZ,
  approved_by INTEGER REFERENCES moderators(id),
  discord_notified BOOLEAN DEFAULT FALSE,
  over_18 BOOLEAN DEFAULT FALSE,
  spoiler BOOLEAN DEFAULT FALSE,
  permalink TEXT DEFAULT ''
);

CREATE INDEX idx_submissions_reddit_id ON submissions(reddit_id);

CREATE TABLE submission_stats (
  id SERIAL PRIMARY KEY,
  submission_id INTEGER REFERENCES submissions(id),
  last_updated TIMESTAMPTZ
);

CREATE INDEX idx_submission_stats_submission_id ON submission_stats(submission_id);

CREATE TABLE submission_stats_entries (
  submission_stats_id INTEGER REFERENCES submission_stats(id),
  stat_hour INTEGER,
  ups INTEGER,
  upvote_ratio DECIMAL,
  PRIMARY KEY(submission_stats_id, stat_hour)
);

CREATE TABLE reports_user (
  id SERIAL PRIMARY KEY,
  reddit_id TEXT UNIQUE,
  reddit_type INTEGER,
  subreddit_id INTEGER REFERENCES subreddits(id),
  report_content TEXT,
  total_reports INTEGER,
  created TIMESTAMPTZ,
  last_updated TIMESTAMPTZ,
  discord_notified BOOLEAN DEFAULT FALSE,
  first_notification BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_reports_submission_id ON reports_user(reddit_id);

CREATE TABLE reports_moderator (
  id SERIAL PRIMARY KEY,
  reddit_id TEXT UNIQUE,
  reddit_type INTEGER,
  subreddit_id INTEGER REFERENCES subreddits(id),
  report_content TEXT,
  total_reports INTEGER,
  created TIMESTAMPTZ,
  last_updated TIMESTAMPTZ,
  discord_notified BOOLEAN DEFAULT FALSE,
  spam_abuse_auto_approved BOOLEAN DEFAULT FALSE, -- For the Jan 2021 "This is spam" report abuse on image posts
  first_notification BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_modreports_submission_id ON reports_moderator(reddit_id);

CREATE TABLE modmail_conversations (
  id SERIAL PRIMARY KEY,
  author_id INTEGER REFERENCES contributers(id),
  reddit_id TEXT UNIQUE,
  subreddit_id INTEGER REFERENCES subreddits(id),
  subject TEXT,
  last_updated TIMESTAMPTZ,
  is_internal BOOLEAN,
  discord_notified BOOLEAN DEFAULT FALSE
);

create table modmail_messages (
  id SERIAL PRIMARY KEY,
  reddit_id TEXT UNIQUE,
  modmail_conversation_id INTEGER REFERENCES modmail_conversations(id),
  contributer_id INTEGER REFERENCES contributers(id),
  body_markdown TEXT,
  message_date TIMESTAMPTZ,
  discord_notified BOOLEAN DEFAULT FALSE
);

CREATE TABLE modmail_old_messages (
  id SERIAL PRIMARY KEY,
  reddit_id TEXT UNIQUE,
  contributer_id INTEGER REFERENCES contributers(id),
  subreddit_id INTEGER REFERENCES subreddits(id),
  subject TEXT,
  body TEXT,
  created TIMESTAMPTZ,
  parent_id TEXT,
  discord_notified BOOLEAN DEFAULT FALSE
);

CREATE TABLE external_errors (
  id SERIAL PRIMARY KEY,
  error_date TIMESTAMPTZ,
  response_code INTEGER NULL,
  error_message TEXT,
  error_body TEXT
);

CREATE TABLE program_errors (
  id SERIAL PRIMARY KEY,
  error_date TIMESTAMPTZ,
  module TEXT,
  error_type TEXT,
  error_message TEXT,
  stack_trace TEXT
);

CREATE TABLE comments (
  id SERIAL PRIMARY KEY,
  reddit_id TEXT,
  contributer_id INTEGER REFERENCES contributers(id),
  subreddit_id INTEGER REFERENCES subreddits(id),
  created TIMESTAMPTZ,
  last_updated TIMESTAMPTZ,
  parent_reddit_id TEXT,
  body TEXT,
  discord_notified BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_comment_reddit_id ON comments(reddit_id);

CREATE TABLE mod_log (
  id SERIAL PRIMARY KEY,
  reddit_id TEXT UNIQUE, -- "ModAction_GUID"
  subreddit_id INTEGER REFERENCES subreddits(id),
  mod_id INTEGER REFERENCES contributers(id),
  contributer_id INTEGER REFERENCES contributers(id),
  action TEXT,
  description TEXT,
  details TEXT,
  target_title TEXT,
  target_name TEXT,
  target_reddit_type INTEGER,
  target_permalink TEXT,
  created TIMESTAMPTZ,
  discord_notified BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_reddit_id ON mod_log(reddit_id);

CREATE TABLE image_processing (
	id SERIAL PRIMARY KEY,
	submission_id INTEGER REFERENCES submissions(id),
	url TEXT,
	file_name TEXT UNIQUE NULL,
	file_hash bytea NULL,
	parse_date TIMESTAMPTZ,
	tesseract_raw_output TEXT NULL,
	matched_text TEXT NULL,
	errors TEXT DEFAULT NULL,
	processing_attempted BOOLEAN DEFAULT FALSE,
	discord_notified BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_image_processing_submission_id ON image_processing(submission_id);
CREATE INDEX idx_image_processing_file_name ON image_processing(file_name);

CREATE TABLE automoderator_matches (
	id SERIAL PRIMARY KEY,
	submission_id INTEGER REFERENCES submissions(id),
	triggered_rule TEXT,
	matches TEXT,
	discord_notified BOOLEAN DEFAULT FALSE
);

CREATE TABLE config_word_blacklist (
	id SERIAL PRIMARY KEY,
	word TEXT UNIQUE,
	occurrences INTEGER DEFAULT 0
);
