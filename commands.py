"""
N-Word Counter - A simple-to-use Discord bot that counts how many times each user has said the N-word
Written in 2019 by NinjaSnail1080 (Discord user: @NinjaSnail1080#8581)

To the extent possible under law, the author has dedicated all copyright and related and neighboring rights to this software to the public domain worldwide. This software is distributed without any warranty.
You should have received a copy of the CC0 Public Domain Dedication along with this software. If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.
"""

from discord.ext import commands
import discord

import collections
import datetime
import time
import pprint
import sys


def find_color(ctx):
    """Find the bot's rendered color. If it's the default color or we're in a DM, return Discord's "greyple" color"""

    try:
        if ctx.guild.me.color == discord.Color.default():
            color = discord.Color.greyple()
        else:
            color = ctx.guild.me.color
    except AttributeError:  #* If it's a DM channel
        color = discord.Color.greyple()
    return color


class Commands(commands.Cog):
    """Commands for the N-Word Counter"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx):
        """Это команда помощи!"""

        cmds = sorted([c for c in self.bot.commands if not c.hidden], key=lambda c: c.name)

        embed = discord.Embed(
            title="Команда помощи",
            description="Я считаю каждый раз когда кто то говорит " + '"ладно"' + ". Я "
                        "довольно простой бот в использовании. Мой префикс это @упоминание, имеется ввиду что Вам нужно "
                        f"вставлять {self.bot.user.mention} перед каждой командой."
                        "\n\nВот короткий список моих команд:",
            color=find_color(ctx))
        embed.set_footer(
            text="Примечание: Нет, я не считаю слова перед тем как присоединился на сервер")
        for c in cmds:
            embed.add_field(name=c.name, value=c.help, inline=False)

        await ctx.send(embed=embed)

    @commands.command(aliases=["info"])
    async def about(self, ctx):
        """Немного базовой информации про меня"""

        embed = discord.Embed(
            title=str(self.bot.user), description=self.bot.app_info.description +
            f"\n\n**ID**: {self.bot.app_info.id}", color=find_color(ctx))

        embed.set_thumbnail(url=self.bot.app_info.icon_url)
        embed.add_field(name="Владелц", value=self.bot.app_info.owner)
        embed.add_field(name="Количество серверов", value=len(self.bot.guilds))
        embed.add_field(name="Количество пользователей", value=len(self.bot.users))
        embed.add_field(
            name="Язык програмирования",
            value=f"Python {sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]}")
        embed.add_field(
            name="Библиотека", value="[discord.py](https://github.com/Rapptz/discord.py)")
        embed.add_field(
            name="Лицензия",
            value="[CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/)")
        embed.add_field(
            name="Открытый код", value="https://github.com/PerchunPak/sunshinedsbot", inline=False)
        embed.set_footer(
            text="Примечание: Оригинальный автор не Perchun_Pak#9236, а NinjaSnail1080#8581")

        await ctx.send(embed=embed)

    @commands.command()
    async def count(self, ctx, user: discord.User=None):
        """Узнайте, сколько раз пользователь сказал "ладно"
        Формат: `count <@пинг пользователя>`
        Если вы не указываете пинг, я укажу **вашу** статистику
        """
        if user is None:
            user = ctx.author
        if user == self.bot.user:
            return await ctx.send(
            """@MATUKITE has said the N-word **1,070,855 times**,
__1,070,801 of which had a hard-R__

They've said the N-word __23,737 times__ since they were last investigated
            """)
        if user.bot:
            return await ctx.send(
                "Я не считаю " + '"ладно-слова"' + ", сказанные ботами. Представляете, насколько это было бы беспокойно?")

        try:
            count = self.bot.lwords[user.id]
        except:
            return await ctx.send(f"{user.mention} еще ни разу не говорил " + '"ладно"' + ". Странный чел")

        if count["total"]:
            msg = (f"{user.mention} сказал ладно **{count['total']:,} "
                   f"раз{'' if count['total'] == 1 else 'а'}**")
            if "last_time" in count:
                since_last = count["total"] - count["last_time"]
                if since_last:
                    msg += (f".\n\nТак же {user.mention} сказал ладно __{since_last:,} "
                            f"раз{'' if since_last == 1 else 'а'}__ с прошлой "
                            "проверки")
            await ctx.send(msg)
            self.bot.lwords[user.id]["last_time"] = self.bot.lwords[user.id]["total"]
        else:
            await ctx.send(f"{user.mention} еще ни разу не говорил " + '"ладно"' + ". Странный чел")

    @count.error
    async def count_error(self, ctx, exc):
        if isinstance(exc, commands.BadArgument):
            return await ctx.send(exc)

    @commands.command()
    async def invite(self, ctx):
        """Скидывает ссылку чтобы Вы могли пригласить бота на свой сервер"""

        await ctx.send("Это моя пригласительная ссылка чтобы Вы могли считать " + '"ладно"' + " тоже:\n"
                       f"https://discordapp.com/oauth2/authorize?client_id={self.bot.app_info.id}"
                       "&scope=bot&permissions=8")

    @commands.command()
    async def stats(self, ctx):
        """Показывает мою статистику"""

        await ctx.channel.trigger_typing()

        uptime = datetime.datetime.utcnow() - self.bot.started_at

        #* This code was copied from my other bot, MAT
        y = int(uptime.total_seconds()) // 31557600  #* Number of seconds in 356.25 days
        mo = int(uptime.total_seconds()) // 2592000 % 12  #* Number of seconds in 30 days
        d = int(uptime.total_seconds()) // 86400 % 30  #* Number of seconds in 1 day
        h = int(uptime.total_seconds()) // 3600 % 24  #* Number of seconds in 1 hour
        mi = int(uptime.total_seconds()) // 60 % 60  #* etc.
        se = int(uptime.total_seconds()) % 60

        frmtd_uptime = []
        if y != 0:
            frmtd_uptime.append(f"{y}г")
        if mo != 0:
            frmtd_uptime.append(f"{mo}мес")
        if d != 0:
            frmtd_uptime.append(f"{d}дн")
        if h != 0:
            frmtd_uptime.append(f"{h}ч")
        if mi != 0:
            frmtd_uptime.append(f"{mi}м")
        if se != 0:
            frmtd_uptime.append(f"{se}с")

        embed = discord.Embed(
            description=f"ID: {self.bot.user.id}",
            timestamp=datetime.datetime.utcnow(),
            color=find_color(ctx))
        embed.add_field(name="Количество серверов", value=f"{len(self.bot.guilds):,} серверов")
        embed.add_field(name="Количество пользовотелей", value=f"{len(self.bot.users):,} уникальных пользователей")
        embed.add_field(
            name="Количество каналов",
            value=f"{len(list(self.bot.get_all_channels()) + self.bot.private_channels):,} "
                  "каналов")
        embed.add_field(
            name="Использование памяти",
            value=f"{round(self.bot.process.memory_info().rss / 1000000, 2)} МБ")
        embed.add_field(name="Пинг", value=f"{round(self.bot.latency * 1000, 2)}мс")
        embed.add_field(name="Аптайм", value=" ".join(frmtd_uptime) + " после прошлого рестарта")
        embed.add_field(
            name="Количество пользователей кто произнес " + '"ладно"',
            value=f"{len(self.bot.lwords):,}",
            inline=False)
        embed.add_field(
            name="Всего слов насчитано",
            value=f"{self.bot.lwords[0]['total']:,} ",
            inline=False)
        embed.set_author(name="Статистика", icon_url=self.bot.user.avatar_url)
        embed.set_footer(text="Эти статистические данные верны на: 98%")

        await ctx.send(embed=embed)

    @commands.command(aliases=["leaderboard", "high"])
    @commands.guild_only()
    async def top(self, ctx, param: str=None):
        """Показывает таблицу лидеров по произношению слова "ладно" на этом сервере. Используйте `top global` чтобы посмотреть таблицу лидеров всех серверов
        Примечание: Если пользователь сказал "ладно" на другом сервере, на котором я тоже есть, они будут приняты во внимание.
        """
        await ctx.channel.trigger_typing()
        def create_leaderboard():
            leaderboard = {}
            if param == "global":
                for u, n in self.bot.lwords.items():
                    if self.bot.get_user(u):
                        leaderboard.update({self.bot.get_user(u): n["total"]})
                leaderboard = dict(collections.Counter(leaderboard).most_common(10))
            else:
                for m in ctx.guild.members:
                    if m.id in self.bot.lwords and not m.bot:
                        if self.bot.lwords[m.id]["total"]:
                            leaderboard.update({m: self.bot.lwords[m.id]["total"]})
                leaderboard = dict(collections.Counter(leaderboard).most_common(10))
            return leaderboard

        leaderboard = await self.bot.loop.run_in_executor(None, create_leaderboard)
        if not len(leaderboard):
            return await ctx.send("На этом сервере еще никто не сказал " + '"ладно"')

        description = "\n"
        counter = 1
        for m, c in leaderboard.items():
            description += (f"**{counter}.** {m if param == 'global' else m.mention} - __{c:,} "
                            f"раз{'' if c == 1 or c == 3 or c == 4 else ''}__\n")
            counter += 1

        description = description.replace("**1.**", ":first_place:").replace("**2.**", ":second_place:").replace("**3.**", ":third_place:")

        embed = discord.Embed(description=description, color=find_color(ctx),
                              timestamp=datetime.datetime.utcnow())
        if param == "global":
            embed.set_author(
                name=f"Топ за все время")
        else:
            embed.set_author(
                name=f"Топ сервера {ctx.guild.name}", icon_url=ctx.guild.icon_url)

        embed.set_footer(
            text="Эти списки верны на: 109%", icon_url=self.bot.user.avatar_url)

        await ctx.send(embed=embed)

    @top.error
    async def top_error(self, ctx, exc):
        if isinstance(exc, commands.NoPrivateMessage):
            return await ctx.send(exc)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def edit(self, ctx, user_id: int, total: int, last_time: int=None):
        """Edit a user's entry in the dict or add a new one"""

        if last_time:
            self.bot.lwords[user_id] = {"id": user_id, "total": total, "last_time": last_time}
        else:
            self.bot.lwords[user_id] = {"id": user_id, "total": total}
        await ctx.send("Done")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def pop(self, ctx, user_id: int):
        """Delete a user's entry from the dict"""

        try:
            self.bot.lwords.pop(user_id)
            await ctx.send("Done")
        except KeyError as e:
            await ctx.send(f"KeyError: ```{e}```")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def execute(self, ctx, *, query):
        """Execute a query in the database"""

        try:
            with ctx.channel.typing():
                async with self.bot.pool.acquire() as conn:
                    result = await conn.execute(query)
            await ctx.send(f"Query complete:```{result}```")
        except Exception as e:
            await ctx.send(f"Query failed:```{e}```")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def fetch(self, ctx, *, query):
        """Run a query in the database and fetch the result"""

        try:
            with ctx.channel.typing():
                async with self.bot.pool.acquire() as conn:
                    result = await conn.fetch(query)

            fmtd_result = pprint.pformat([dict(i) for i in result])
            await ctx.send(f"Query complete:```{fmtd_result}```")
        except Exception as e:
            await ctx.send(f"Query failed:```{e}```")

    @commands.command(aliases=["resetstatus"], hidden=True)
    @commands.is_owner()
    async def restartstatus(self, ctx):
        await self.bot.change_presence(status=discord.Status.dnd, activity=discord.Activity(
            name=f"for N-Words on {len(self.bot.guilds)} servers",
            type=discord.ActivityType.watching))

        await ctx.send("Reset playing status")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def setstatus(self, ctx, status):
        """Change the bot's presence"""

        if status.startswith("on"):
            await self.bot.change_presence(status=discord.Status.online)
        elif status.startswith("id"):
            await self.bot.change_presence(status=discord.Status.idle)
        elif status.startswith("d"):
            await self.bot.change_presence(status=discord.Status.dnd)
        elif status.startswith("off") or status.startswith("in"):
            await self.bot.change_presence(status=discord.Status.invisible)
        else:
            await ctx.send("Invalid status")

        await ctx.send("Set new status")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def updatedb(self, ctx):
        temp = await ctx.send("Manually updating... This may take a few minutes... Please wait...")
        with ctx.channel.typing():
            start = time.perf_counter()
            async with self.bot.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO lwords
                    (id)
                    VALUES {}
                    ON CONFLICT
                        DO NOTHING
                ;""".format(", ".join([f"({u})" for u in self.bot.lwords])))

                for data in self.bot.lwords.copy().values():
                    await conn.execute("""
                        UPDATE lwords
                        SET total = {}
                        WHERE id = {}
                    ;""".format(data["total"], data["id"]))

        delta = time.perf_counter() - start
        mi = int(delta) // 60
        sec = int(delta) % 60
        ms = round(delta * 1000 % 1000)
        await temp.delete()
        await ctx.send(f"Finished updating database ({mi}m {sec}s {ms}ms)")


def setup(bot):
    bot.add_cog(Commands(bot))
