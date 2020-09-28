Username = None
Password = None

def initialize(config):
    global Username, Password

    Username = config["username"]
    Password = config["password"]
