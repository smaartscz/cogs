from redbot.core import commands, Config
import discord
import httpx

class URLTrigger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=2468476484)  # Change identifier if needed
        self.config.register_guild(urls={}, mod_roles=[])

    async def get_mod_role(self, guild):
        mod_role_id = await self.config.guild(guild).mod_role()
        return guild.get_role(mod_role_id) if mod_role_id else None

    def is_mod(self, author, mod_roles):
        return any(role in author.roles for role in mod_roles)

    @commands.Cog.listener()
    async def on_message(self, message):
        async with self.config.guild(message.guild).urls() as urls:
            for trigger, (url, method, key, value) in urls.items():
                if message.content == trigger:
                    try:
                        full_url = url.replace("{userid}", str(message.author.id))
                        async with httpx.AsyncClient() as client:
                            if method.upper() == "POST":
                                data = {key: value.replace("{userid}", str(message.author.id))}
                                response = await client.post(full_url, data=data)
                            else:
                                response = await client.get(full_url)
                    except Exception as e:
                        error_message = f"Error Sending {method} Request\nError: {str(e)}\nURL: {full_url}"
                        embed = discord.Embed(title="Something went wrong!", description=error_message, color=discord.Color.red())
                        await message.channel.send(embed=embed)

    @commands.group(aliases=["ut"])
    async def urltrigger(self, ctx):
        """URL Trigger Commands"""
        pass

    @urltrigger.command(name="add")
    async def urltrigger_add(self, ctx, trigger: str, url: str, method: str = "GET", key: str = None, value: str = None):
        """Add a URL Trigger"""
        mod_roles = await self.get_mod_role(ctx.guild)
        if self.is_mod(ctx.author, mod_roles):
            if method.upper() not in ["GET", "POST"]:
                embed = discord.Embed(title="Something went wrong!", description="Invalid method. Please use 'GET' or 'POST'.", color=discord.Color.red())
                await ctx.send(embed=embed)
                return
            if method.upper() == "POST" and (key is None or value is None):
                embed = discord.Embed(title="Something went wrong!", description="For POST requests, key and value must be specified.", color=discord.Color.red())
                await ctx.send(embed=embed)
                return
            async with self.config.guild(ctx.guild).urls() as urls:
                urls[trigger] = (url, method.upper(), key, value)
            embed = discord.Embed(title="Success!", color=discord.Color.green())
            embed.add_field(name=trigger, value=f"{url} ({method.upper()})", inline=False)
            if method.upper() == "POST":
                embed.add_field(name="POST Data", value=f"{key}: {value}", inline=False)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="Something went wrong!", description="You don't have permission to use this command.", color=discord.Color.red())
            await ctx.send(embed=embed)

    @urltrigger.command(name="remove")
    async def urltrigger_remove(self, ctx, trigger: str):
        """Remove a URL Trigger"""
        mod_roles = await self.get_mod_role(ctx.guild)
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
                for trigger, (url, method, key, value) in triggers.items():
                    embed.add_field(name=trigger, value=f"{url} ({method})", inline=False)
                    if method == "POST":
                        embed.add_field(name="POST Data", value=f"{key}: {value}", inline=False)
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
    @commands.has_permissions(administrator=True)
    async def urltrigger_modrole_set(self, ctx, role: discord.Role):
        """Set the mod role for URL Trigger commands"""
        existing_mod_role = await self.get_mod_role(ctx.guild)
        if existing_mod_role:
            embed = discord.Embed(title="Something went wrong!", description="Mod role has already been set. Only administrators can modify the mod role.", color=discord.Color.red())
            await ctx.send(embed=embed)
        else:
            await self.config.guild(ctx.guild).mod_role.set(role.id)
            embed = discord.Embed(title="Success!", description=f"Mod role set to: {role.mention}", color=discord.Color.green())
            await ctx.send(embed=embed)

    @urltrigger_modrole.command(name="remove")
    @commands.has_permissions(administrator=True)
    async def urltrigger_modrole_remove(self, ctx):
        """Remove the mod role from URL Trigger commands"""
        existing_mod_role = await self.get_mod_role(ctx.guild)
        if existing_mod_role:
            await self.config.guild(ctx.guild).mod_role.set(None)
            embed = discord.Embed(title="Success!", description="Mod role removed.", color=discord.Color.green())
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="Something went wrong!", description="No mod role has been set yet. Use the `modrole set` command to set the mod role.", color=discord.Color.red())
            await ctx.send(embed=embed)
