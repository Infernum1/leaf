from bot import LeafBot
from utils.time import parse_duration
from utils.helpers import shorten_text
from discord.ext import commands
from discord import app_commands
import discord
import arrow
from discord.utils import format_dt

class RemindersCog(commands.GroupCog, name="Reminders", group_name="reminders"):
    def __init__(self, bot: LeafBot) -> None:
        self.bot = bot

    @app_commands.describe(
        reminder_text="What you need to be reminded of.",
        duration_str="When do you want to be reminded.",
        make_private="Keep the reminder private (you'll be notified through DMs)"
    )
    @app_commands.command(name="add", description="Add a reminder")
    async def add_reminder(self, interaction: discord.Interaction, reminder_text: str, duration_str: str, make_private: bool) -> None:
        duration = parse_duration(duration_str)
        embed = discord.Embed()

        if duration is None or duration.total_seconds() <= 0:
            embed.description = "You need to give me a valid time! For eg. `1y10M2d5m`."
            return await interaction.response.send_message(embed=embed)
    
        at = arrow.utcnow() + duration

        query = "INSERT INTO reminders (content, owner_id, remind_at, message_id, private) VALUES ($1, $2, $3, $4, $5)"
        await self.bot.database.execute(query, reminder_text, interaction.message.author.id, at.datetime, interaction.message.id, make_private)
        embed.description = f"Okay! I'll remind you {format_dt(at.datetime, style='R')}"

    @app_commands.describe(show_private="`True` if you want to see private reminders too, `False` by default")
    @app_commands.command(name="list", description="Take a look at all your active reminders")
    async def list_reminders(self, interaction: discord.Interaction, show_private: bool = False):
        query = "SELECT * FROM reminders WHERE owner_id = $1 AND private = $2"
        user_reminders = await self.bot.database.execute(query, interaction.message.author.id, show_private)
        embed = discord.Embed()
        embed.set_author(
            name=f"{interaction.message.author.display_name}'s reminders", icon_url=interaction.message.author.avatar.url
        )

        for reminder in user_reminders:
            unix_timestamp = format_dt(reminder["at"], style="R")
            reminder_text = shorten_text(reminder["reminder"], 75)
            embed.add_field(
                name=f"`#{reminder['id']}` - {unix_timestamp}",
                value=reminder_text,
                inline=False,
            )
        await interaction.response.send_message(embed=embed)

async def setup(bot: LeafBot) -> None:
    await bot.add_cog(RemindersCog(bot))