from discord.ext import tasks, commands
from Reddit import Data as rd

class ReportAbuse(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.getUserReports.start()

    def cog_unload(self):
        self.getUserReports.cancel()

    @tasks.loop(minutes=1.0)
    async def getReports(self):
        print ("ReportAbuse: Looped")

    @getReports.before_loop
    async def before_getUserReports(self):
        await self.bot.wait_until_ready()
