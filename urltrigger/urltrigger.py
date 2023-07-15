from redbot.core import commands, Config
import discord

class urltrigger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=2468476484)  # Change identifier if needed
        self.config.register_guild(urls={})

    @commands.Cog.listener()
    async def on_message(self, message):
        async with self.config.guild(message.guild).urls() as urls:
            for trigger, url in urls.items():
                if message.content == trigger:
                    try:
                        full_url = url.replace("{userid}", str(message.author.id))
                        response = await self.bot.http.request(discord.http.Route("GET", full_url))
                        if response.status == 200:
                            embed = discord.Embed(title="GET Request Sent", color=discord.Color.green())
                            await message.channel.send(embed=embed)
                        else:
                            error_message = f"Error Sending GET Request\nStatus Code: {response.status}\nError: {response.reason}\nURL: {full_url}"
                            embed = discord.Embed(title="Error Sending GET Request", description=error_message, color=discord.Color.red())
                            await message.channel.send(embed=embed)
                    except Exception as e:
                        error_message = f"Error Sending GET Request\nError: {str(e)}\nURL: {full_url}"
                        embed = discord.Embed(title="Error Sending GET Request", description=error_message, color=discord.Color.red())
                        await message.channel.send(embed=embed)

    @commands.group(aliases=["ut"])
    async def urltrigger(self, ctx):
        """URL Trigger Commands"""
        pass

    @urltrigger.command(name="add")
    async def urltrigger_add(self, ctx, trigger: str, url: str):
        """Add a URL Trigger"""
        async with self.config.guild(ctx.guild).urls() as urls:
            urls[trigger] = url
        embed = discord.Embed(title="Success", color=discord.Color.green())
        embed.add_field(name=url, value="Trigger was added!", inline=False)
        await ctx.send(embed=embed)

    @urltrigger.command(name="remove")
    async def urltrigger_remove(self, ctx, trigger: str):
        """Remove a URL Trigger"""
        async with self.config.guild(ctx.guild).urls() as urls:
            if trigger in urls:
                del urls[trigger]                
                embed = discord.Embed(title="Success", color=discord.Color.green())
                embed.add_field(name="", value="Trigger was removed!", inline=False)
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(title="Something went wrong", color=discord.Color.red())
                embed.add_field(name="", value="Trigger couldn't be removed! Does it exist?", inline=False)
                await ctx.send(embed=embed)
    @urltrigger.command(name="list")
    async def urltrigger_list(self, ctx):
        """List all URL Triggers"""
        triggers = await self.config.guild(ctx.guild).urls()
        if triggers:
            embed = discord.Embed(title="URL Triggers", color=discord.Color.blue())
            for trigger, url in triggers.items():
                embed.add_field(name=trigger, value=url, inline=False)
            await ctx.send(embed=embed)
        else:
            await ctx.send("No URL Triggers found.")

def setup(bot):
    bot.add_cog(URLTrigger(bot))
