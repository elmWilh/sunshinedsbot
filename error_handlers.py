"""
N-Word Counter - A simple-to-use Discord bot that counts how many times each user has said the N-word
Written in 2019 by NinjaSnail1080 (Discord user: @NinjaSnail1080#8581)

To the extent possible under law, the author has dedicated all copyright and related and neighboring rights to this software to the public domain worldwide. This software is distributed without any warranty.
You should have received a copy of the CC0 Public Domain Dedication along with this software. If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.
"""

from discord.ext import commands
import discord


class Error_Handlers(commands.Cog):
    """Error Handlers for commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, exception):
        exc = exception
        if isinstance(exc, commands.NotOwner):
            return await ctx.send(f"Только мой Владелец, {self.bot.app_info.owner}, может использовать эту команду")

        elif isinstance(exc, commands.NoPrivateMessage):
            return

        elif isinstance(exc, commands.BadArgument):
            return

        elif isinstance(exc, discord.Forbidden):
            return

        elif isinstance(exc, discord.NotFound):
            return

        elif "Missing Permissions" in str(exc):
            return await ctx.send("У меня нет необходимых прав для выполнения этой команды. "
                                  "Предоставление мне разрешения администратора должно решить эту проблему")

        else:
            return await ctx.send(
                f"```Команда: {ctx.command.qualified_name}\n{exc}```Неизвестная ошибка "
                "произошла и я не смог выполнить эту команду. Простите!")


def setup(bot):
    bot.add_cog(Error_Handlers(bot))
