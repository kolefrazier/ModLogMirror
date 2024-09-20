import os

IMAGE_SAVE_LOCATION = None
IMAGE_MAGICK_PATH = None
WORD_BLACKLIST = []

def initialize(config, environment):
    global IMAGE_SAVE_LOCATION, IMAGE_MAGICK_PATH, WORD_BLACKLIST

    IMAGE_SAVE_LOCATION = config[environment]["imageSaveLocation"]
    IMAGE_MAGICK_PATH = config[environment]["imageMagickPath"]
    WORD_BLACKLIST = [word.lower() for word in config["wordBlacklist"]]

    _createSaveDirIfNotExists()

def _createSaveDirIfNotExists():
    os.makedirs(IMAGE_SAVE_LOCATION, exist_ok=True)
