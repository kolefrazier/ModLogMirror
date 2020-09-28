Host = None
Port = None
Database = None
User = None
Password = None

def initialize(config):
    global Host, Port, Database, User, Password

    Host = config["host"]
    Port = config["port"]
    Database = config["database"]
    Password = config["password"]
    User = config["user"]
