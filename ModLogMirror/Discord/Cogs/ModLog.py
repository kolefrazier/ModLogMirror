import logging
from discord.ext import tasks, commands
from discord import Embed
import Discord.Colors as CustomColors
import Discord.Channels as Channels
from Reddit.Data import Subreddits, ModLog as RedditModLog # Alias ModLog, otherwise it wants to use the class defined below.
from Reddit.Utility import TextHelpers, ModeratorActions #GetHumanReadableAction(key)
import Config.Reddit as RedditConfig

class ModLog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger("discord")
        self.getModLog.start()
        self.channel = "pso2-modlog"

    def cog_unload(self):
        self.getModLog.cancel()

    @tasks.loop(minutes=1.0)
    async def getModLog(self):
        try:
            for sub in RedditConfig.Subreddits["Moderated"]:
                SubId = Subreddits.GetIdByName(sub)
                UnnotifiedEntries = RedditModLog.GetUnnotified(SubId)

                # Check if the sub exists in the channels. If not, throw a helpful error.
                # (Based on an error that filled the logs silently for a solid month.)
                # Could probably refactor this logic into the config startup, to run checks and stuff.
                if(sub not in Channels.Channels[self.channel].keys()):
                    raise Exception(f"Hey dingus, you have a sub ({sub}) in the moderated list that doesn't have a matching entry for {self.channel}! Remove it or add a channel!")

                if len(UnnotifiedEntries) > 0:
                    EmbeddedMessage = self._createEmbeddedMessage(sub.upper(), UnnotifiedEntries)

                    await Channels.Channels[self.channel][sub].send(embed=EmbeddedMessage)

                    NotifiedIds = [m["id"] for m in UnnotifiedEntries]
                    RedditModLog.MarkNotified(NotifiedIds)
        except Exception as e:
            self.logger.info(f"[Cog: ModLog][Task: getModLog] Unhandled exception: {str(e)}")

    @getModLog.before_loop
    async def before_getModLog(self):
        await self.bot.wait_until_ready()

    def _createEmbeddedMessage(self, subredditName, modLogEntries):
        EmbeddedMessage = Embed(
            #description="", 
            color=CustomColors.ModGreen,
            url=f"https://www.reddit.com/r/{subredditName}/about/log/",
            title=f"/r/{subredditName} Mod Log",
            #icon=""
        )

        for entry in modLogEntries:
            # General outline for each message:
            #
            # Action | Mod
            # Permalink | Date
            # Target Author | Details (reddit-generated details)
            # Description (custom mod input values - eg automod config change notes)

            FormattedBody = []
            ModAction = ModeratorActions.GetHumanReadableAction(entry["action"])
            FieldTitle = f"{ModAction} | {entry['acting_mod']}"
            
            # The following may not have a value, so some None-checking is needed
            # Row: Permalink | Date
            if entry['target_permalink'] is not None:
                FormattedPermalink = self._formatPermalink(entry['target_permalink'])
                FormattedBody.append(f"[Permalink]({FormattedPermalink}) | {entry['created']}")
            else:
                FormattedBody.append(f"{entry['created']}")

            # Row: Target Author | Details
            AuthorDetailsRow = []
            if entry['target_author'] is not None and len(entry['target_author']) > 0:
                AuthorNameSanitized = TextHelpers.SanitizeUsername(entry['target_author'])
                AuthorDetailsRow.append(f"u/{AuthorNameSanitized}")

            if entry['details'] is not None:
                AuthorDetailsRow.append(f"{entry['details']}")

            FormattedBody.append(" | ".join(AuthorDetailsRow))

            # Row: Description
            if entry['description'] is not None and entry['description'] != "":
                FormattedBody.append(f"*({entry['description']})*")

            EmbeddedMessage.add_field(
                name=FieldTitle,
                value="\n".join(FormattedBody),
                inline=False
        )

        return EmbeddedMessage

    def _formatPermalink(self, permalink):
        return f"https://reddit.com{permalink}"