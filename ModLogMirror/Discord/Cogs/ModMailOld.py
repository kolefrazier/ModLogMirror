import logging
from discord.ext import tasks, commands
from discord import Embed
import Discord.Colors as CustomColors
import Discord.Channels as Channels
from Reddit.Data import ModmailOld, Subreddits
from Reddit.Utility import TextHelpers

# --- IMPORTANT ---
# This class is tightly coupled to the database table modmail_old_messages!
class ModMailOld(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger("discord")
        self.getModMailOld.start()
        self.channel = "pso2-modmail"

    def cog_unload(self):
        self.getModMailOld.cancel()

    @tasks.loop(minutes=1.0)
    async def getModMailOld(self):
        try:
            SubId = Subreddits.GetIdByName('PSO2')
            UnnotifiedMail = ModmailOld.GetUnnotified(SubId)

            if len(UnnotifiedMail) > 0:
                EmbeddedMessage = self._createEmbeddedMessage(UnnotifiedMail)
                await Channels.Channels[self.channel].send(embed=EmbeddedMessage)

                NotifiedIds = [m['id'] for m in UnnotifiedMail]
                ModmailOld.MarkNotified(NotifiedIds)
        except Exception as e:
            self.logger.exception(f"[Cog: ModMailOld][Task: getModMailOld] Unhandled exception: {str(e)}")

    @getModMailOld.before_loop
    async def before_getModMailOld(self):
        await self.bot.wait_until_ready()

    def _createEmbeddedMessage(self, mailBag):
        EmbeddedMessage = Embed(
            description="New messages from the mail bag!", 
            color=CustomColors.ModGreen,
            url="https://www.reddit.com/r/PSO2/about/message/inbox/",
            title="/r/PSO2 Modmail",
            #icon=""
        )

        for index, message in enumerate(mailBag):
            TrimmedBody = TextHelpers.TrimContent(message['body'], 25)

            MessageName = f"{index+1}. {message['subject']}\nFrom: {message['author']}"
            if message['parent_id'] is not None:
                ParentMention = f"*(Response to parent: [{message['parent_id']}](https://www.reddit.com/message/messages/{message['parent_id']}))*\n"
                TrimmedBody = ParentMention + TrimmedBody

            EmbeddedMessage.add_field(
                name=MessageName,
                value=f"{TrimmedBody}",
                inline=False
        )

        return EmbeddedMessage
