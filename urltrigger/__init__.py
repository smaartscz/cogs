from .urltrigger import urltrigger

async def setup(bot):
    await bot.add_cog(urltrigger(bot=bot))
    