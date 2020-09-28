import yaml

_configs = {}
CONFIG_WIKI_PATH = "config/automoderator"

def GetConfig(subreddit):
    """ Retrieve the Automoderator config from the given subreddit. Requires wiki access. """

    if subreddit.display_name not in _configs:
        _retrieveConfig(subreddit)

    return _configs[subreddit.display_name]

def _retrieveConfig(subreddit):
    """ Private method - Wraps the actual retrieval of the Automod config page. """

    configMarkdown = subreddit.wiki[CONFIG_WIKI_PATH].content_md

    # The config *should* be validated by Reddit before saving. Thus, load() should be appropriate. (OG Automod used yaml.load()...)
    _configs[subreddit.display_name] = yaml.load(configMarkdown)

def GetRuleMatches(submission, subreddit):
    print('foo')
