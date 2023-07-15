from redbot.core import commands, Config
import discord
import httpx

class URLTrigger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=2468476484)  # Change identifier if needed
        self.config.register_guild(urls={}, mod_roles=[])

    async def get_mod_roles(self, guild):
        mod_role_ids = await self.config.guild(guild).mod_roles()
        return [guild.get_role(role_id) for role_id in mod_role_ids]

    def is_mod(self, author, mod_roles):
        return any(role in author.roles for role in mod_roles)

    @commands.Cog.listener()
    async def on_message(self, message):
        async with self.config.guild(message.guild).urls() as urls:
            for trigger, url in urls.items():
                if message.content == trigger:
                    try:
                        full_url = url.replace("{userid}", str(message.author.id))
                        async with httpx.AsyncClient() as client:
                            response = await client.get(full_url)
                            if response.status_code == 200:
                                embed = discord.Embed(title="Success!", color=discord.Color.green())
                                await message.channel.send(embed=embed)
                            else:
                                error_message = f"Error Sending GET Request\nStatus Code: {response.status_code}\nError: {response.reason}\nURL: {full_url}"
                                embed = discord.Embed(title="Something went wrong!", description=error_message, color=discord.Color.red())
                                await message.channel.send(embed=embed)
                    except Exception as e:
                        error_message = f"Error Sending GET Request\nError: {str(e)}\nURL: {full_url}"
                        embed = discord.Embed(title="Something went wrong!", description=error_message, color=discord.Color.red())
                        await message.channel.send(embed=embed)

    @commands.group(aliases=["ut"])
    async def urltrigger(self, ctx):
        """URL Trigger Commands"""
        pass

    @urltrigger.command(name="add")
    async def urltrigger_add(self, ctx, trigger: str, url: str):
        """Add a URL Trigger"""
        mod_roles = await self.get_mod_roles(ctx.guild)
        if self.is_mod(ctx.author, mod_roles):
            async with self.config.guild(ctx.guild).urls() as urls:
                urls[trigger] = url
            embed = discord.Embed(title="Success!", color=discord.Color.green())
            embed.add_field(name=trigger, value=url, inline=False)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="Something went wrong!", description="You don't have permission to use this command.", color=discord.Color.red())
            await ctx.send(embed=embed)

    @urltrigger.command(name="remove")
    async def urltrigger_remove(self, ctx, trigger: str):
        """Remove a URL Trigger"""
        mod_roles = await self.get_mod_roles(ctx.guild)
        if self.is_mod(ctx.author, mod_roles):
            async with self.config.guild(ctx.guild).urls() as urls:
                if trigger in urls:
                    del urls[trigger]
                    embed = discord.Embed(title="Success!", color=discord.Color.green())
                    embed.add_field(name=trigger, value="Trigger was removed!", inline=False)
                    await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(title="Something went wrong!", description="Trigger couldn't be removed! Does it exist?", color=discord.Color.red())
                    await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="Something went wrong!", description="You don't have permission to use this command.", color=discord.Color.red())
            await ctx.send(embed=embed)

    @urltrigger.command(name="list")
    async def urltrigger_list(self, ctx):
        """List all URL Triggers"""
        try:
            triggers = await self.config.guild(ctx.guild).urls()
            if triggers:
                embed = discord.Embed(title="URL Triggers", color=discord.Color.blue())
                for trigger, url in triggers.items():
                    embed.add_field(name=trigger, value=url, inline=False)
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(title="URL Triggers", description="No URL Triggers found.", color=discord.Color.blue())
                await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(title="Error", description=f"An error occurred while executing the command: {str(e)}", color=discord.Color.red())
            await ctx.send(embed=embed)

    @urltrigger.group(name="modrole")
    async def urltrigger_modrole(self, ctx):
        """Mod Role Commands"""
        pass

    @urltrigger_modrole.command(name="set")
    async def urltrigger_modrole_set(self, ctx, *roles: discord.Role):
        """Set mod roles for URL Trigger commands"""
        mod_roles = [role.id for role in roles]
        await self.config.guild(ctx.guild).mod_roles.set(mod_roles)
        role_mentions = ", ".join(role.mention for role in roles)
        embed = discord.Embed(title="Success!", description=f"Mod roles set to: {role_mentions}", color=discord.Color.green())
        await ctx.send(embed=embed)

    @urltrigger_modrole.command(name="remove")
    async def urltrigger_modrole_remove(self, ctx, *roles: discord.Role):
        """Remove mod roles from URL Trigger commands"""
        mod_roles = await self.config.guild(ctx.guild).mod_roles()
        for role in roles:
            if role.id in mod_roles:
                mod_roles.remove(role.id)
        await self.config.guild(ctx.guild).mod_roles.set(mod_roles)
        role_mentions = ", ".join(role.mention for role in roles)
        embed = discord.Embed(title="Success!", description=f"Mod roles removed: {role_mentions}", color=discord.Color.green())
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(URLTrigger(bot))
