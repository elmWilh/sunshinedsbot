# Sunshine Discord Bot

Our discord bot, fully translated to russian (without backend)

My first project, so it is can have many issues in code

## Installing

1. **Get Python 3.6 or higher**

This is required to run the bot

2. **Clone this repository**

3. **Set up a virtual environment**

Do `python3 -m venv <path to repository>`

4. **Once in the venv, install dependencies**

Run `python3 -m pip install -U -r REQUIREMENTS.txt`

5. **Create a database in PostGreSQL**

You will need version 9.5 or higher. The database will store the n-word count for each user. There's no centralized database.

6. **Setup configuration**

There's a file in the root directory called `config.py` which contains two variables that are needed in order to run the bot. One is `TOKEN`, which is a string containing the Discord bot token. The other variable is `POSTGRES`, which is a string containing the DSN for the Postgres database created in step 5.

> from https://github.com/NWordCounter/bot

#

**Important Note**: You need to turn on the `SERVER MEMBERS` privileged intent in order for the bot to work. [Follow these instructions to turn it on](https://discordpy.readthedocs.io/en/latest/intents.html#privileged-intents).

## Credits

"ладно" counter it is fork from https://github.com/NWordCounter/bot
