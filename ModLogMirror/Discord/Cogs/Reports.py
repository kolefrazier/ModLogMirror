import json
import logging
from discord.ext import tasks, commands
from discord import Embed
import Discord.Colors as CustomColors
import Discord.Channels as Channels
from Reddit.Data import ReportsMod, ReportsUser, Subreddits, Comments, Submissions
from Reddit.Utility import TextHelpers
from Reddit.Cache import ReportsUser as ReportsCache
from Reddit.Enums import NamedContentTypes
import Config.Reddit as RedditConfig

class Reports(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger("discord")
        self.channel = "pso2-reports"
        self.getUserReports.start()

    def cog_unload(self):
        self.getUserReports.cancel()

    @tasks.loop(minutes=1.0)
    async def getUserReports(self):
        try:
            for sub in RedditConfig.Subreddits["Moderated"]:
                SubId = Subreddits.GetIdByName(sub)
                #ModReports = ReportsMod.GetUnnotified(SubId)
                UserReports = ReportsUser.GetUnnotified(SubId)

                # TODO: Generate messages for batches of up to ~10 reports
                if len(UserReports) > 0:
                    EmbeddedMessage = self._createEmbeddedMessage(sub.upper(), UserReports)
                    await Channels.Channels[self.channel][sub].send(embed=EmbeddedMessage)

                    NotifiedIds = [r["id"] for r in UserReports]
                    ReportsUser.MarkNotified(NotifiedIds)
        except Exception as e:
            self.logger.exception(f"[Cog: Reports][Task: getUserReports] Unhandled exception: {str(e)}")

    @getUserReports.before_loop
    async def before_getUserReports(self):
        await self.bot.wait_until_ready()

    def _createEmbeddedMessage(self, subredditName, reports):
        EmbeddedMessage = Embed(
            description="New reports!",
            color=CustomColors.ModGreen,
            url=f"https://www.reddit.com/r/{subredditName}/about/modqueue/",
            title=f"/r/{subredditName} Reports",
            #icon=""
        )

        HistoryRangeDays = 90

        for report in reports:
            # General outline for each report:
            #
            # New Reported Type / Additional Reports on Type
            # Reddit ID | total reports
            # * Count: Reason (repeating row)

            FieldBody = []
            TypeName = NamedContentTypes(report['reddit_type']).name

            # Report summary - contains username and report history (for use further down)
            ReportSummary = self._getContentReportSummary(report, TypeName, HistoryRangeDays)

            # TODO: Investigate this issue and figure out what's going on.
            #   Might need to pull reports twice for each sub, using the `only:<'comments'/'submissions'>` arg and enforce type.
            if ReportSummary == None:
                self.logger.warning(f"Reports cog: No report summary returned from query. Reddit_Id: {report['reddit_id']}, Reddit Type: {TypeName}")
                
                # Flip type
                OtherType = "Link" if TypeName == "Comment" else "Comment"

                # Try again
                ReportSummary = self._getContentReportSummary(report, OtherType, HistoryRangeDays)

                # Log
                if ReportSummary == None:
                    self.logger.info(f"Reports cog: Changed type to {OtherType} and still did not find any history. Reddit_Id: {report['reddit_id']}")
                else:
                    self.logger.info(f"Reports cog: Found summary after type change to {Othertype}. Reddit_Id: {report['reddit_id']}")

            # Field summary row
            if ReportSummary == None:
                FieldBody.append(f"Total reports: {report['total_reports']}")
            else:
                FieldBody.append(f"u/{ReportSummary['username']} | Total reports: {report['total_reports']}")


            # Title row: New/Updated, Type, ID
            if report["first_notification"] == False:
                FieldTitle = f"**New Reported {TypeName}**"
            else:
                FieldTitle = f"**Additional Reports on {TypeName}**"

            # List each report reason and quantity
            ReportContent = json.loads(report["report_content"])
            for content in ReportContent:
                FieldBody.append(f"\t\u2022 {content['count']}:\t{content['reason']}")
            
            # Reported summary
            if ReportSummary == None:
                FieldBody.append(f"*ID: {report['reddit_id']}*")
            elif(ReportSummary['total_reports'] > 1 and ReportSummary['reported_items'] > 1): # Don't show history unless it goes beyond the current report
                FieldBody.append(f"*90-Day History: {ReportSummary['total_reports']} reports across {ReportSummary['reported_items']} items. | ID: {report['reddit_id']}*")

            EmbeddedMessage.add_field(
                name=FieldTitle,
                value="\n".join(FieldBody),
                inline=False
            )
        return EmbeddedMessage

    #def _getAuthorInfo(self, report, typeName):
    #    if(typeName == "Comment"):
    #        return Comments.GetWithAuthorInfo(report["reddit_id"])
    #    elif(typeName == "Link"):
    #        return Submissions.GetSubmissionReportsAndAuthor(report["reddit_id"])

    def _getContentReportSummary(self, report, typeName, daysAgo):
        # If the time range is changed here, update it in the message content above.
        if(typeName == "Comment"):
            return ReportsUser.GetCommentReportsAndAuthor(report["reddit_id"], daysAgo) # 90 days ago
        elif(typeName == "Link"):
            return ReportsUser.GetSubmissionReportsAndAuthor(report["reddit_id"], daysAgo)
