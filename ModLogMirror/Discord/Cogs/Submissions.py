import logging
from discord.ext import tasks, commands
from discord import Embed
import Discord.Colors as CustomColors
import Discord.Channels as Channels
from time import sleep
from Reddit.Data import Submissions as RedditDataSubmissions, Subreddits
from Reddit.Utility import TextHelpers
import Config.Reddit as RedditConfig

class Submissions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger("discord")
        self.channel = "pso2-submissions"
        self.getSubmissions.start()
        print("TODO: Cache subreddit ID w/ Discord channel to reduce ID lookup on each getSubmissions() call")

    def cog_unload(self):
        self.getSubmissions.cancel()

    @tasks.loop(seconds=30)
    async def getSubmissions(self):
        try:
            for sub in RedditConfig.Subreddits["Regular"]:
                SubId = Subreddits.GetIdByName(sub)
                UnnotifiedSubmissions = RedditDataSubmissions.GetUnnotified(SubId)
        
                if len(UnnotifiedSubmissions) > 0:
                    for submission in UnnotifiedSubmissions:
                        EmbeddedMessage = self._createEmbeddedMessage(submission)
                        await Channels.Channels[self.channel][sub].send(embed=EmbeddedMessage)
                        sleep(1)

                    NotifiedIds = [result["id"] for result in UnnotifiedSubmissions]
                    if len(NotifiedIds) > 0:
                        RedditDataSubmissions.MarkNotified(NotifiedIds)
        except Exception as e:
            self.logger.exception(f"[Cog: Submissions][Task: getSubmissions] Unhandled exception: {str(e)}")

    @getSubmissions.before_loop
    async def before_getSubmissions(self):
        await self.bot.wait_until_ready()

    def _createEmbeddedMessage(self, submission):
        # Create embedded post
        # title contains the submission type
        # url contains the title and permalink
        EmbeddedMessage = Embed(
            color=CustomColors.PSO2Blue,
            title=TextHelpers.FormattedSubstring(submission["title"]),
            description=f"New {submission['submissionType']} post on /r/PSO2",
            url="https://reddit.com"+submission["permalink"]
        )

        # Post author
        EmbeddedMessage.add_field(
            name="Post Author",
            value="/u/"+submission["author"]
        )

        # Content Warnings
        TypeTags = []
        if submission["over_18"]:
            TypeTags.append("**NSFW**")
        if submission["spoiler"]:
            TypeTags.append("**Spoiler**")
        if len(TypeTags) == 0:
            TypeTags.append("None")

        EmbeddedMessage.add_field(
            name="Content Warnings",
            value=", ".join(TypeTags)
        )

        # Post contents preview
        EmbeddedMessage.add_field(
            name="Content Preview",
            value=f"```{submission['content']}```",
            inline=False
        )

        ## Moderation Status
        #if submission["mod"] != None:
        #    EmbeddedMessage.add_field(
        #        name="Moderation Status",
        #        value=f"Moderated by {submission['mod']}, status: {submission['status']}"
        #    )

        return EmbeddedMessage
