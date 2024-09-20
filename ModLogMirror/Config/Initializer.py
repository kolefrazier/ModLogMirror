import json
from Config import Reddit as RedditConfig, Redis as RedisConfig, Database as DbConfig, Discord as DiscordConfig, Environment as EnvironmentConfig, ImageProcessing as ImageProcessingConfig

""" Config initializer methods. Intended to be called from module __init__. """

def initializeAllConfigs():
    config = None

    with open('config.json') as f:
        config = json.load(f)

    EnvironmentConfig.initialize(config["activeEnvironment"])
    ImageProcessingConfig.initialize(config["imageProcessing"], EnvironmentConfig.Environment)
    RedditConfig.initialize(config["reddit"])
    RedditConfig.initialize(config["reddit"])
    RedisConfig.initialize(config["redis"])
    DbConfig.initialize(config["postgres"])
    DiscordConfig.initialize(config["discord"], EnvironmentConfig.Environment)