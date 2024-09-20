import discord
import Config.Discord

Channels = {}

def InitializeChannels(bot):
    global Channels

    for key in Config.Discord.channels:
        if type(Config.Discord.channels[key]) is dict:
            if Channels.get(key) is None:
                Channels[key] = {}

            for subkey in Config.Discord.channels[key].keys():
                Channels[key][subkey] = bot.get_channel(Config.Discord.channels[key][subkey])
        else:
            Channels[key] = bot.get_channel(Config.Discord.channels[key])

def Get(bot, key):
    global Channels

    if Channels[key] is None:
        Channels[key] = bot.get_channel(Config.Discord.channels[key])

    return Channels[key]
