import discord
import random

my_bot = discord.Bot(command_prefix="!", intents=discord.Intents.all())


def ping():
    return (f"Pong!\n"
            f">>> {round(my_bot.latency * 1000)}ms")


def greetings():
    return random.choice(["Hello!", "Hi!", "Hey!", "Yo!", "Sup!"])


def command_list():
    commands = "\n".join([f"!{command}" for command in handlers.keys()])
    return (f"Available commands:\n"
            f">>> {commands}")


handlers = {
    "hello": greetings,
    "ping": ping,
    "help": command_list,
}

alias_groups = {
    "hello": ["hi", "hey", "yo", "sup"],
}

aliases = {alias: command for command, aliases in alias_groups.items() for alias in aliases}


async def handle_response(message, discord_bot: discord.bot) -> None:
    """
    Gives a response to a message using text commands
    :param message: message the bot received
    :param discord_bot: the discord bot object
    :return: None
    """
    formatted_message = message.content[1:].lower()
    canonical_command = aliases.get(formatted_message, formatted_message)
    response = handlers.get(canonical_command)
    global my_bot
    my_bot = discord_bot

    if response is None:
        return

    if callable(response):
        response = response()
    else:
        response = response

    await message.channel.send(response)
