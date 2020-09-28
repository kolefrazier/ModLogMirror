CREATE TABLE IF NOT EXISTS Contributers (
  ContributerId INTEGER PRIMARY KEY,
  Username TEXT
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_contributers_username ON Contributers(Username);

CREATE TABLE IF NOT EXISTS Subreddits ( 
	SubredditId INTEGER PRIMARY KEY , 
	SubredditName TEXT,
	RedditId TEXT
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_subreddits_subredditname ON Subreddits(SubredditName);
CREATE UNIQUE INDEX IF NOT EXISTS idx_subreddits_redditId ON Subreddits(RedditId);

CREATE TABLE IF NOT EXISTS Submissions (
  SubmissionId INTEGER PRIMARY KEY,
  RedditId TEXT,
  RedditType TEXT,
  SubredditId INT,
  Title TEXT,
  ContributerId INT NOT NULL,
  SubmissionStatus INT,
  SubmissionDate DATETIME,
  LastUpdated DATETIME,
  LastUpdatedMod TEXT,

  FOREIGN KEY (ContributerId) 
    REFERENCES Contributers(ContributerId),

  FOREIGN KEY (SubredditId) 
    REFERENCES Subreddits(SubredditId)
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_submissions_redditid ON Submissions(RedditId);

CREATE TABLE IF NOT EXISTS DiscordSubmissionsQueue (
	DiscordSubmissionsQueueId INTEGER PRIMARY KEY,
	SubmissionId INT,
	Reported INT
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_discordsubmissionsqueue_submissionid ON DiscordSubmissionsQueue(SubmissionId);

CREATE TABLE IF NOT EXISTS Reports (
  ReportId INTEGER PRIMARY KEY,
  SubmissionId INT NOT NULL,
  ReportContent TEXT,

  FOREIGN KEY (SubmissionId) 
    REFERENCES Submissions(SubmissionId)
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_reports_submissionid ON Reports(SubmissionId);

CREATE TABLE IF NOT EXISTS ModReports (
  ModReportId INTEGER PRIMARY KEY,
  SubmissionId INT NOT NULL,
  ReportContent TEXT,

  FOREIGN KEY (SubmissionId) 
    REFERENCES Submissions(SubmissionId)
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_modreports_submissionid ON Reports(SubmissionId);

CREATE TABLE IF NOT EXISTS Modmails (
  ModmailId INTEGER PRIMARY KEY,
  ContributerId INT,
  Title TEXT,
  Body TEXT,

  FOREIGN KEY (ContributerId) 
    REFERENCES Contributers(ContributerId)
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_modmails_contributerid ON Modmails(ContributerId);

CREATE TABLE IF NOT EXISTS ExternalErrors (
	ExternalErrorId INTEGER PRIMARY KEY,
	ErrorDate DATETIME,
	ResponseCode INT NULL,
	ErrorMessage TEXT,
	ErrorBody TEXT
);

CREATE TABLE IF NOT EXISTS ProgramErrors (
	ProgramErrorId INTEGER PRIMARY KEY,
	ErrorDate DATETIME,
	Module TEXT,
	ErrorType TEXT,
	ErrorMessage TEXT,
	StackTrace TEXT
);

CREATE TABLE IF NOT EXISTS Comments (
	CommentId INTEGER PRIMARY KEY,
	ContributerId INT,
	SubredditId INT,
	Created DATETIME,
	ParentId TEXT,
	Body TEXT,

	FOREIGN KEY (ContributerId) 
		REFERENCES Contributers(ContributerId),
	FOREIGN KEY (SubredditId) 
		REFERENCES Subreddits(SubredditId)
);