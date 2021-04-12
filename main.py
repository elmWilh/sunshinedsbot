"""
N-Word Counter - A simple-to-use Discord bot that counts how many times each user has said the N-word
Written in 2019 by NinjaSnail1080 (Discord user: @NinjaSnail1080#8581)

To the extent possible under law, the author has dedicated all copyright and related and neighboring rights to this software to the public domain worldwide. This software is distributed without any warranty.
You should have received a copy of the CC0 Public Domain Dedication along with this software. If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.
"""

from discord.ext import commands, tasks
import discord
import asyncpg
import psutil

import datetime
import re
import os

import config #! You'll need to define your own credentials in config.py

bot_intents = discord.Intents.default()
bot_intents.members = True

bot = commands.Bot(
    command_prefix=commands.when_mentioned,
    description="ладно-Word Counter",
    case_insensitive=True,
    help_command=None,
    status=discord.Status.invisible,
    intents=bot_intents,
    fetch_offline_members=True
)

bot.process = psutil.Process(os.getpid())
bot.ready_for_commands = False
bot.load_extension("commands")
bot.load_extension("error_handlers")


async def create_pool():
    """Create table in postgres database if it doesn't already exist. Otherwise, get the n-word data"""

    bot.pool = await asyncpg.create_pool(config.POSTGRES)
    async with bot.pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS lwords (
                id BIGINT PRIMARY KEY,
                total BIGINT NOT NULL DEFAULT 0
            )
        ;""")

        await conn.execute("""
                INSERT INTO lwords
                (id)
                VALUES (0)
                ON CONFLICT (id)
                    DO NOTHING
            ;""")

        query = await conn.fetch("SELECT * FROM lwords;")

    bot.lwords = {}
    for i in query:
        bot.lwords.update({i.get("id"): dict(i)})


@bot.event
async def on_connect():
    print("\nУстановлено соеденение с дискордом")


@bot.event
async def on_ready():
    await create_pool()

    print("\nЗашел как:")
    print(bot.user)
    print(bot.user.id)
    print("-----------------")
    print(datetime.datetime.now().strftime("%m/%d/%Y %X"))
    print("-----------------")
    print("Shards: " + str(bot.shard_count))
    print("Серверов: " + str(len(bot.guilds)))
    print("Пользователей: " + str(len(bot.users)))
    print("-----------------\n")

    update_db.start()
    bot.ready_for_commands = True
    bot.started_at = datetime.datetime.utcnow()
    bot.app_info = await bot.application_info()

    await bot.change_presence(status=discord.Status.online, activity=discord.Activity(
        name=f'кто сколько раз сказал "ладно"', type=discord.ActivityType.competing))


@bot.event
async def on_message(message):
    if not bot.ready_for_commands or message.author.bot:
        return

    if message.guild is not None:
        for m in re.finditer(r"\b(ладно)(s\b|\b)", message.content, re.IGNORECASE):
            if message.author.id not in bot.lwords:
                bot.lwords.update(
                    {message.author.id: {"total": 0, "id": message.author.id}})
            bot.lwords[message.author.id]["total"] += 1
            bot.lwords[0]["total"] += 1

    ctx = await bot.get_context(message)
    if ctx.valid:
        await bot.invoke(ctx)
    else:
        if bot.user in message.mentions and len(message.mentions) == 2:
            await message.channel.send(f"Вам нужно написать `@{bot.user} count <user>` чтобы "
                                       f"получить статистику другого пользователя.\nИспользуйте"
                                       "`@{bot.user} help` для помощи с другими командами")
        elif bot.user in message.mentions:
            await message.channel.send(f"Используйте `@{bot.user} help` для списка моих команд")


@tasks.loop(minutes=5, loop=bot.loop)
async def update_db():
    """Update the SQL database every 5 minutes"""

    async with bot.pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO lwords
            (id)
            VALUES {}
            ON CONFLICT
                DO NOTHING
        ;""".format(", ".join([f"({u})" for u in bot.lwords])))

        for data in bot.lwords.copy().values():
            await conn.execute("""
                UPDATE lwords
                SET total = {}
                WHERE id = {}
            ;""".format(data["total"], data["id"]))


@bot.command(hidden=True)
@commands.is_owner()
async def reload(ctx):
    """Reload the bot's cogs"""

    bot.reload_extension("commands")
    bot.reload_extension("error_handlers")
    await ctx.send("Reloaded extensions")


@bot.command(hidden=True)
@commands.is_owner()
async def restartdb(ctx):
    await create_pool()
    await ctx.send("Restarted database")


@bot.command(hidden=True)
@commands.is_owner()
async def restartudb(ctx):
    update_db.cancel()
    update_db.start()
    await ctx.send("Cancelled and restarted `update_db()`")


try:
    bot.loop.run_until_complete(bot.start(config.TOKEN))
except KeyboardInterrupt:
    print("\nЗакрытие")
    bot.loop.run_until_complete(bot.change_presence(status=discord.Status.invisible))
    for e in bot.extensions.copy():
        bot.unload_extension(e)
    print("Выходим")
    bot.loop.run_until_complete(bot.logout())
finally:
    update_db.cancel()
    bot.loop.run_until_complete(bot.pool.close())
    print("Закрыто")
