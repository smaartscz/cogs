import discord
from discord import Embed
from redbot.core import commands, Config
import asyncio

class AutoReply(commands.Cog):
    """AutoReply cog"""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=7735229659)
        default_guild_settings = {
            "autoreply_settings": {},
            "autoreply_settings_role": None
        }
        self.config.register_guild(**default_guild_settings)

    async def has_modrole(self, ctx):
        modrole_id = await self.config.guild(ctx.guild).autoreply_settings_role()
        modrole = discord.utils.get(ctx.guild.roles, id=modrole_id)
        if not modrole:
            return True  # No modrole set, allow any user to modify settings
        if modrole not in ctx.author.roles:
            embed = Embed(
                title="Error",
                description="You do not have the required role to modify autoreply settings.",
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed)
            return False
        return True

    @commands.group(aliases=["ar"])
    async def autoreply(self, ctx):
        """Manage autoreply settings"""
        pass

    @autoreply.command(name="add")
    async def autoreply_add(self, ctx, users_word: str, bots_reply: str, exact_match: bool = True, delete_after: int = 0):
        """Add a word and bot reply to autoreply settings"""
        if not await self.has_modrole(ctx):
            return

        settings = await self.config.guild(ctx.guild).autoreply_settings()
        settings[users_word.lower()] = {"reply": bots_reply, "exact_match": exact_match}
        await self.config.guild(ctx.guild).autoreply_settings.set(settings)

        embed = Embed(title="Autoreply Added", color=discord.Color.green())
        embed.add_field(name="Word", value=users_word, inline=False)
        embed.add_field(name="Bot Reply", value=bots_reply, inline=False)
        embed.add_field(name="Exact Match", value=str(exact_match), inline=False)

        message = await ctx.send(embed=embed)

        if delete_after > 0:
            await asyncio.sleep(delete_after)
            await message.delete()


    @autoreply.command(name="remove")
    async def autoreply_remove(self, ctx, users_word: str):
        """Remove a word from autoreply settings"""
        if not await self.has_modrole(ctx):
            return

        settings = await self.config.guild(ctx.guild).autoreply_settings()
        if users_word.lower() in settings:
            del settings[users_word.lower()]
            await self.config.guild(ctx.guild).autoreply_settings.set(settings)
            embed = Embed(title="Autoreply Removed", description=f"Removed autoreply for: {users_word}", color=discord.Color.green())
            await ctx.send(embed=embed)
        else:
            embed = Embed(title="Error", description=f"No autoreply found for: {users_word}", color=discord.Color.red())
            await ctx.send(embed=embed)


    @autoreply.command(name="list")
    async def autoreply_list(self, ctx):
        """List all autoreply settings"""
        if not await self.has_modrole(ctx):
            return

        settings = await self.config.guild(ctx.guild).autoreply_settings()
        if settings:
            reply_list = []

            for user_word, bot_reply in settings.items():
                reply_text = f"{user_word} - {bot_reply['reply']} (Exact Match: {bot_reply['exact_match']})"
                reply_list.append(reply_text)

            # Check if the total reply_list length exceeds 4000 characters
            if sum(len(reply) for reply in reply_list) > 4000:
                embeds = []
                current_embed = Embed(title="Autoreply List", color=discord.Color.blue())
                character_count = 0

                for reply in reply_list:
                    if character_count + len(reply) > 4000:
                        embeds.append(current_embed)
                        current_embed = Embed(title="Autoreply List (Continued)", color=discord.Color.blue())
                        character_count = 0

                    current_embed.add_field(name="Autoreply", value=reply, inline=False)
                    character_count += len(reply)

                embeds.append(current_embed)

                for embed in embeds:
                    await ctx.send(embed=embed)
            else:
                embed = Embed(title="Autoreply List", color=discord.Color.blue())

                for reply in reply_list:
                    embed.add_field(name="Autoreply", value=reply, inline=False)

                await ctx.send(embed=embed)
        else:
            embed = Embed(title="Autoreply List", description="No autoreply settings found.", color=discord.Color.blue())
            await ctx.send(embed=embed)


    @autoreply.command(name="purge")
    async def autoreply_purge(self, ctx):
        """Remove all autoreply settings"""
        if not await self.has_modrole(ctx):
            return

        await self.config.guild(ctx.guild).autoreply_settings.clear()
        embed = Embed(title="Autoreply Purged", description="Cleared all autoreply settings.", color=discord.Color.green())
        await ctx.send(embed=embed)


    @autoreply.command(name="modrole")
    async def autoreply_modrole(self, ctx, modrole: discord.Role):
        """Set the modrole for autoreply settings"""
        if not await self.has_modrole(ctx):
            return        
        await self.config.guild(ctx.guild).autoreply_settings_role.set(modrole.id)
        embed = Embed(title="Modrole Set", description=f"The modrole for autoreply settings is now set to: {modrole.mention}", color=discord.Color.green())
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        content = message.content.lower()
        settings = await self.config.guild(message.guild).autoreply_settings()

        for users_word, bot_reply in settings.items():
            if bot_reply['exact_match'] and users_word == content:
                reply = bot_reply['reply'].replace("{user}", message.author.mention)
                await message.channel.send(reply)
                return
            elif not bot_reply['exact_match'] and users_word in content:
                reply = bot_reply['reply'].replace("{user}", message.author.mention)
                await message.channel.send(reply)
                return
