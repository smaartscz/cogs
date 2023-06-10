import discord
from redbot.core import commands, Config

class AutoReply(commands.Cog):
    """My custom cog"""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=7735229659)
        default_guild_settings = {
            "autoreply_settings": {}
        }
        self.config.register_guild(**default_guild_settings)

    @commands.group(aliases=["ar"])
    async def autoreply(self, ctx):
        """Manage autoreply settings"""
        pass

    @autoreply.command(name="add")
    async def autoreply_add(self, ctx, users_word: str, bots_reply: str):
        """Add a word and bot reply to autoreply settings"""
        settings = await self.config.guild(ctx.guild).autoreply_settings()
        settings[users_word.lower()] = bots_reply
        await self.config.guild(ctx.guild).autoreply_settings.set(settings)
        await ctx.send(f"Added autoreply: {users_word} - {bots_reply}")

    @autoreply.command(name="remove")
    async def autoreply_remove(self, ctx, users_word: str):
        """Remove a word from autoreply settings"""
        settings = await self.config.guild(ctx.guild).autoreply_settings()
        if users_word.lower() in settings:
            del settings[users_word.lower()]
            await self.config.guild(ctx.guild).autoreply_settings.set(settings)
            await ctx.send(f"Removed autoreply for: {users_word}")
        else:
            await ctx.send(f"No autoreply found for: {users_word}")

    @autoreply.command(name="list")
    async def autoreply_list(self, ctx):
        """List all autoreply settings"""
        settings = await self.config.guild(ctx.guild).autoreply_settings()
        if settings:
            reply_list = "\n".join(f"{user_word} - {bot_reply}" for user_word, bot_reply in settings.items())
            await ctx.send(f"Autoreply List:\n{reply_list}")
        else:
            await ctx.send("No autoreply settings found.")

    @autoreply.command(name="purge")
    async def autoreply_purge(self, ctx):
        """Remove all autoreply settings"""
        await self.config.guild(ctx.guild).autoreply_settings.clear()
        await ctx.send("Cleared all autoreply settings.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        content = message.content.lower()
        settings = await self.config.guild(message.guild).autoreply_settings()

        for users_word, bots_reply in settings.items():
            if users_word in content:
                bots_reply = bots_reply.replace("{user}", message.author.mention)
                await message.channel.send(bots_reply)
                break
