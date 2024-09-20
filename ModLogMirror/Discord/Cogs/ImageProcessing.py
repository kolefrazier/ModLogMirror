import logging
from discord.ext import tasks, commands
from discord import Embed
import Discord.Colors as CustomColors
import Discord.Channels as Channels
from Reddit.Data import Subreddits
from ImageProcessing import Data as ImageProcessingData, Utility as ImageUtility

class ImageProcessing(commands.Cog, name="Image Processing"):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger("discord")
        self.channel = "pso2-imageprocessing"
        self.getImageProcessingResults.start()
        

    def cog_unload(self):
        self.getImageProcessingResults.cancel()

    @tasks.loop(minutes=1.0)
    async def getImageProcessingResults(self):
        try:
            SubId = Subreddits.GetIdByName("PSO2")
            ImageProcessingResults = ImageProcessingData.GetUnnotified(SubId)

            if len(ImageProcessingResults) > 0:
                EmbeddedMessage = self._createEmbeddedMessage(ImageProcessingResults)

                # Only send a message if there's something to report
                if len(EmbeddedMessage.fields) > 0:
                    await Channels.Channels[self.channel].send(embed=EmbeddedMessage)

            NotifiedIds = [result["id"] for result in ImageProcessingResults]
            if len(NotifiedIds) > 0:
                ImageProcessingData.MarkNotified(NotifiedIds)
        except Exception as e:
            self.logger.exception(f"[Cog: ImageProcessing][Task: getImageProcessingResults] Unhandled exception: {str(e)}")

    @getImageProcessingResults.before_loop
    async def before_getImageProcessingResults(self):
        await self.bot.wait_until_ready()

    # --- getResults Command and Helpers ---
    @commands.command(name="results", help="Retrieve image OCR results. Arguments: redditId (ab1cd2)")
    async def getResults(self, ctx, redditId):
        try:
            self.logger.info(f"[Cog: ImageProcessing][Command: getResults({redditId})] Invoked by: {ctx.author.display_name} (id: {ctx.author.id})")
            Result = ImageProcessingData.GetResults(redditId)

            if Result == None:
                await ctx.send(f"No record found for '{redditId}'")
            else:
                EmbeddedMessage = self._getResultsEmbeddedMessage(Result, redditId)
                await ctx.send(embed=EmbeddedMessage)
        except Exception as e:
            self.logger.exception(f"[Cog: ImageProcessing][Command: getResults({redditId})] An error occurred: {str(e)}")

    @getResults.error
    async def getResultsError(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(str(error))

    # Commented out - Not sure if this is needed since the change to delete-after-processing.
    ## --- purgeImage Command and Helpers ---
    #@commands.command(name="purge", help="Immediately purge a cached image. Arguments: redditId (ab1cd2)")
    #async def purgeImage(self, ctx, redditId):
    #    self.logger.info(f"[{redditId}] Command purgeImage invoked by {ctx.author.display_name} (discord id: {ctx.author.id}).")
    #    RecordInfo = ImageProcessingData.GetPrePurgeInfo(redditId)
    #    if RecordInfo == None:
    #        self.logger.info(f"[{redditId}] No record found.")
    #        await ctx.send(f"No record found for Reddit ID of {redditId}. Data retrieval may not have processed that post, yet.")
    #    else:
    #        try:
    #            self.logger.info(f"[{redditId}] Record found, beginning purge.")
    #            ImageUtility.PurgeImage(redditId, RecordInfo["file_name"])
    #            self.logger.info(f"[{redditId}] Files perged.")
    #            ImageProcessingData.PurgeRecord(redditId)
    #            self.logger.info(f"[{redditId}] Database record sanitized.")
    #            await ctx.send(f"Image has been purged from cache, database record sanitized.")
    #        except Exception as e:
    #            self.logger.error(f"[{redditId}] Error while purging image: {str(e)}")
    #            await ctx.send(f"An error occurred while purging image. Double check your ID and try again. Otherwise, ping Telchii to check the logs.")
    #
    #@purgeImage.error
    #async def purgeImageError(self, ctx, error):
    #    if isinstance(error, commands.MissingRequiredArgument):
    #        await ctx.send(str(error))

    # --- Private Methods ---
    def _getResultsEmbeddedMessage(self, result, redditId):
        EmbeddedMessage = Embed(
            color=CustomColors.ModGreen,
            title=f"Image Processing Results for {redditId}",
            #icon=""
        )

        # Post Information
        # On link posts (includes image posts), submission_content is the link.
        title = result['submission_title']
        url = f"[{title}](https://redd.it/{redditId})"
        EmbeddedMessage.add_field(
            name="--- Post ---",
            value=f"{url}\nContent URL: `{result['submission_content']}`", 
            inline=False
        )

        # Image Processing Results
        FieldBody = []
        #FieldBody.append(f"Hash: {result['image_hash']}") TODO: Need to convert the bin to hex-str! (str() casting doesn't seem to work...)
        FieldBody.append(f"Hash: (to be implemented)")
        FieldBody.append(f"Parse Date (UTC): {result['image_parse_date']}")

        FieldBody.append(f"--Matched Text--")
        MappedResults = self._mapResults(result['image_tesseract_match'])

        # If needed, set default values. Otherwise, six backticks (`) get smooshed together, which borks output formatting.
        if MappedResults['Method 1'] == "" or MappedResults['Method 1'] == None:
            MappedResults['Method 1'] = "No results"
        if MappedResults['Method 2'] == "" or MappedResults['Method 2'] == None:
            MappedResults['Method 2'] = "No results"
        FieldBody.append(f"Method 1:\n```{MappedResults['Method 1']}```")
        FieldBody.append(f"Method 2:\n```{MappedResults['Method 2']}```")
        
        FieldBody.append(f"--Raw Parse Results---")
        MappedResults = self._mapResults(result['image_tesseract_raw'])

        # If needed, set default values. Otherwise, six backticks (`) get smooshed together, which borks output formatting.
        if MappedResults['Method 1'] == "" or MappedResults['Method 1'] == None:
            MappedResults['Method 1'] = "No results"
        if MappedResults['Method 2'] == "" or MappedResults['Method 2'] == None:
            MappedResults['Method 2'] = "No results"
        FieldBody.append(f"Method 1:\n```{MappedResults['Method 1']}```")
        FieldBody.append(f"Method 2:\n```{MappedResults['Method 2']}```")


        if result['image_errors'] != None:
            FieldBody.append(f"\nErrors:\n```{result['image_errors']}```")

        EmbeddedMessage.add_field(
            name="--- Image Processing ---",
            value="\n".join(FieldBody),
            inline=False
        )

        return EmbeddedMessage


    def _createEmbeddedMessage(self, processingResults):
        EmbeddedMessage = Embed(
            color=CustomColors.ModGreen,
            title="Image Processing Results",
            #icon=""
        )

        for result in processingResults:
            if result["matched_text"] == None:
                continue

            FieldBody = []
            FieldBody.append(f"URL: `{result['url']}`\n")
            #FieldBody.append(f"Results:\n```{result['matched_text']}```")
            MappedResults = self._mapResults(result['matched_text'])

            # If needed, set default values. Otherwise, six backticks (`) get smooshed together, which borks output formatting.
            if MappedResults['Method 1'] == "" or MappedResults['Method 1'] == None:
                MappedResults['Method 1'] = "No results"
            if MappedResults['Method 2'] == "" or MappedResults['Method 2'] == None:
                MappedResults['Method 2'] = "No results"
            FieldBody.append(f"Method 1:\n```{MappedResults['Method 1']}```")
            FieldBody.append(f"Method 2:\n```{MappedResults['Method 2']}```")

            EmbeddedMessage.add_field(
                name=f"Text found in image! | Record ID: {result['id']} | Reddit ID: {result['reddit_id']}",
                value="\n".join(FieldBody),
                inline=False
            )

        return EmbeddedMessage

    def _mapResults(self, raw_results):
        return {
            "Method 1": raw_results['normal'],
            "Method 2": raw_results['inverted']
        }
