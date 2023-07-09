import discord
from discord import Embed
from redbot.core import commands, Config
import asyncio

class AutoEmbedMessage(commands.Cog):
    """AutoEmbedMessage cog will automatically embed discord message links  """
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild:
            return

        embed_fields = []

        for word in message.content.split():
            if word.startswith("https://discord.com/channels/") or word.startswith("https://discordapp.com/channels/"):
                message_link = discord.utils.escape_markdown(word)
                message_id = word.split("/")[-1]
                channel_id = word.split("/")[-2]
                channel = self.bot.get_channel(int(channel_id))
                if channel:
                    try:
                        fetched_message = await channel.fetch_message(int(message_id))
                        if fetched_message.attachments and fetched_message.attachments[0].content_type.startswith("image/"):
                            embed_fields.append((fetched_message.author.name, fetched_message.attachments[0].url))
                        else:
                            embed_fields.append((fetched_message.author.name, fetched_message.content))
                    except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                        continue

        if embed_fields:
            embed = discord.Embed(
                color=discord.Color.blue()
            )

            for username, content in embed_fields:
                if content.startswith("https://"):
                    if content.endswith((".png", ".jpg", ".jpeg", ".gif")):
                        embed.add_field(name=username, value="", inline=False)
                        embed.set_image(url=content)
                else:
                    embed.add_field(name=username, value=content, inline=False)


            message_link = f"[Link to message](https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id})"
            embed.add_field(name="", value=message_link, inline=False)

            await message.channel.send(embed=embed)
    @commands.command()
    async def autoembed(self, ctx):
        """Displays help information about the AutoEmbed cog."""
        help_message = (
            "AutoEmbed cog automatically embeds Discord message links.\n\n"
            "To use AutoEmbed, simply post a message that contains a Discord message link "
            "The cog will then embed the referenced message in the channel where the original "
            "message was sent. If the referenced message contains image, "
            "they will be embedded as well.\n\n"
            "Please note that the bot needs proper permissions to fetch and embed messages.\n\n"
        )
        await ctx.send(help_message)

def setup(bot):
    bot.add_cog(AutoEmbedMessageLinks(bot))
    