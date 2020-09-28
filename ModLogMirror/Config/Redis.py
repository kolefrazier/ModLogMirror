Host = None
Port = None
Password = None
Db = None

def initialize(config):
    global Host, Port, Password, Db

    Host = config["host"]
    Port = config["port"]
    Password = config["password"]
    Db = config["db"]
