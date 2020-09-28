Username = None
Password = None
ClientSecret = None
ClientId = None
UserAgent = None
AppScopes = None
Subreddits = None

def initialize(config):
    global Username, Password, ClientSecret, ClientId, UserAgent, AppScopes, Subreddits

    Username = config["username"]
    Password = config["password"]
    ClientSecret = config["clientSecret"]
    ClientId = config["clientId"]
    UserAgent = config["userAgent"]
    AppScopes = config["appScopes"]
    Subreddits = {
        "Regular": config["subreddits"]["regular"],
        "Moderated": config["subreddits"]["moderated"],
        "All": [],
        "ModLog": config["subreddits"]["modlog"]
    }

    Subreddits["All"] = list(set(Subreddits["Regular"] + Subreddits["Moderated"]))
