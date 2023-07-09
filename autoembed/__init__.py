from .autoembedmessage import AutoEmbedMessage

async def setup(bot):
    await bot.add_cog(AutoEmbedMessage(bot=bot))
    