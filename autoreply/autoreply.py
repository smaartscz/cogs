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
    async def autoreply_add(self, ctx, users_word: str, bots_reply: str, exact_match: bool = True, delete_after: int = 0):
        """Add a word and bot reply to autoreply settings"""
        settings = await self.config.guild(ctx.guild).autoreply_settings()
        settings[users_word.lower()] = {"reply": bots_reply, "exact_match": exact_match, "delete_after": delete_after}
        await self.config.guild(ctx.guild).autoreply_settings.set(settings)
        await ctx.send(f"Added autoreply: {users_word} - {bots_reply} (Exact Match: {exact_match}, Delete After: {delete_after}s)")

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
            reply_list = "\n".join(f"{user_word} - {bot_reply['reply']} (Exact Match: {bot_reply['exact_match']}, Delete After: {bot_reply['delete_after']}s)" for user_word, bot_reply in settings.items())
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

        for users_word, bot_reply in settings.items():
            if bot_reply['exact_match'] and users_word == content:
                reply = bot_reply['reply'].replace("{user}", message.author.mention)
                sent_message = await message.channel.send(reply)
                if 'delete_after' in bot_reply and bot_reply['delete_after'] > 0:
                    await sent_message.delete(delay=bot_reply['delete_after'])
                return
            elif not bot_reply['exact_match'] and users_word in content:
                reply = bot_reply['reply'].replace("{user}", message.author.mention)
                sent_message = await message.channel.send(reply)
                if 'delete_after' in bot_reply and bot_reply['delete_after'] > 0:
                    await sent_message.delete(delay=bot_reply['delete_after'])
                return

        # If no autoreply is triggered, delete the message after 0 seconds (default: no deletion)
        sent_message = await message.channel.send(message.content)
        await sent_message.delete(delay=0)
