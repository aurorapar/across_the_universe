import time

from discord import Message
from discord.ext.commands import Bot

from ..dtos import GuildState
from ..dtos import RabbitMessage


async def handle_typed_message(bot: Bot, discord_message: Message):
    guild_state = GuildState(discord_message.guild.id, discord_message.guild.name)
    if not guild_state.has_channel():
        print("not doing anything because guild didn't have channel set")
        return

    user = discord_message.author
    if user == bot.user:
        print("not doing anything because bot sent message")
        return

    user_account = user.name
    user_name = user.display_name
    server = discord_message.guild.name
    channel = discord_message.channel.name
    now = int(time.time())
    message = RabbitMessage(user_account, user_name, server, channel, discord_message.content, now)

    await bot.publish_message(message)

