import discord # for discord.Client & intents
from discord.ext import commands # for @bot.command()
from Config import Discord as DiscordConfig
from Discord import Channels
from Discord.Cogs import ModLog, Reports, ImageProcessing, Submissions # ReportAbuse, ModMailOld
import logging
import Reddit.Data.Submissions as RedditSubmissions
from time import sleep

logger = logging.getLogger("discord")
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="a")
handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
logger.addHandler(handler)

# Intents
# https://discordpy.readthedocs.io/en/stable/intents.html
intents = discord.Intents.default()
intents.message_content = True  # Needed for prefix-based commands (non-slash commands).

#client = discord.Client(command_prefix="!")
# Set up using commands.Bot, following the Discord.py Commands docs: https://discordpy.readthedocs.io/en/latest/ext/commands/commands.html
# (Because the "get started" and "minimal bot" use different things......)
bot = commands.Bot(command_prefix="!", intents=intents)

# Track channel initialization to prevent re-initializations on repeat on_ready events. (From reconnects, etc.)
ChannelsInitialized = False

def WaitForServices():
    StartupWaitCounter = 1
    while True:
        logger.info(f"[Startup] ({StartupWaitCounter}) Waiting for other services to start.")
        try:
            if RedditSubmissions.GetAny():
                break
        finally:
            sleep(5 * StartupWaitCounter)

class ModLogMirrorBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.command_prefix = "!"
        #self.intents = intents
        self.channels_initialized = False
    
    async def on_ready(self):
        if self.channels_initialized == False:
            Channels.InitializeChannels(self)
            self.channels_initialized = True

        print('Bot on_ready hit!')


    async def ping(self, ctx, message=None):
        try:
            logger.info(f"[Command: ping(message={message})] Invoked by: {ctx.author.display_name} (id: {ctx.author.id})")
            response = "Pong!" if message == None else message
            await ctx.send(response)
        except Exception as e:
            logger.exception(f"[Bot Root Level][Command: ping(message={message}] Unhandled exception: {str(e)}")

    async def setup_hook(self):
        # For Discord.py v2.0, loading cogs is async and requires awaiting each load.
        await self.add_cog(ModLog.ModLog(self))
        await self.add_cog(Reports.Reports(self))
        await self.add_cog(ImageProcessing.ImageProcessing(self))
        #await self.add_cog(Submissions.Submissions(self)) # TEMP DISABLE UNTIL I CAN FIX IT

        # Example error for Submissions cog above
        #2024-01-01 07:52:49,734:ERROR:discord: [Cog: Submissions][Task: getSubmissions] Unhandled exception: 400 Bad Request (error code: 50035): Invalid Form Body
        #In embeds.0.fields.2.value: Must be 1024 or fewer in length.
        #Traceback (most recent call last):
        #    File "/home/kole/git/ModLogMirror/ModLogMirror/Discord/Cogs/Submissions.py", line 32, in getSubmissions
        #    await Channels.Channels[self.channel][sub].send(embed=EmbeddedMessage)
        #    File "/home/kole/venv/modlogmirror/lib/python3.10/site-packages/discord/abc.py", line 1562, in send
        #    data = await state.http.send_message(channel.id, params=params)
        #    File "/home/kole/venv/modlogmirror/lib/python3.10/site-packages/discord/http.py", line 745, in request
        #    raise HTTPException(response, data)
        #discord.errors.HTTPException: 400 Bad Request (error code: 50035): Invalid Form Body
        #In embeds.0.fields.2.value: Must be 1024 or fewer in length.


        # Disabled Cogs
        # await bot.add_cog(ReportAbuse.ReportAbuse(bot))
        # await bot.add_cog(ModMailOld.ModMailOld(bot))

bot = ModLogMirrorBot(command_prefix="!", intents=intents)
bot.run(DiscordConfig.token, reconnect=True)
