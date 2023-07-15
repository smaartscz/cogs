from .urltrigger import URLTrigger

async def setup(bot):
    await bot.add_cog(URLTrigger(bot=bot))
    