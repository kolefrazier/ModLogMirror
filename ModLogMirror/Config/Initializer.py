import json
from Config import Reddit as RedditConfig, Redis as RedisConfig, Database as DbConfig #, Discord as DiscordConfig

""" Config initializer methods. Intended to be called from module __init__. """

def readConfig():
    config = None

    with open('config.json') as f:
        config = json.load(f)

    RedditConfig.initialize(config["reddit"])
    RedisConfig.initialize(config["redis"])
    DbConfig.initialize(config["postgres"])
    #DiscordConfig.initialize(config["discord"])
