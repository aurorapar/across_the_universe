import json
import sys
from typing import Any

import discord
from discord.ext import tasks
from discord.ext.commands import Bot

from .commands import set_bot_channel
from .dtos import ChatEmbed, GuildState
from .queue_handlers.publisher import Publisher
from .queue_handlers.subscriber import Subscriber
from .handlers import handle_typed_message
from .settings import BOT_USERNAME, SYNC_ON_MESSAGE, RESYNC_ALLOWED


class DiscordBot(Bot):

    def __init__(self, *, command_prefix: str, intents: discord.Intents):
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.synced = False
        self.publisher = Publisher()
        self.subscribers = {}

    async def on_error(self, event_method: str, /, *args: Any, **kwargs: Any) -> None:
        error = sys.exc_info()
        error_message = error[1]
        # trace = error[2]
        print(error_message)

    async def on_message(self, discord_message):
        await handle_typed_message(self, discord_message)
        master_user = int(discord_message.author.id) == 266328806011174912
        if discord_message.content.lower() == 'resync':
            if len([role for role in discord_message.author.roles if role.permissions.administrator]) or master_user:
                # await discord_message.channel.delete_messages(messages=[discord_message])
                if not RESYNC_ALLOWED and not master_user:
                    await discord_message.author.send(content='Resyncing has been disabled.')
                    return
                if self.synced:
                    await discord_message.author.send(content='The bot has already synced.')
                    return
                print('Resyncing....')
                await discord_message.author.send(content='Resyncing....')
                await self.tree.sync()
                await self.tree.sync(guild=discord.Object(discord_message.guild.id))
                print('Resynced')
                await discord_message.author.send(content='Resynced!')
                self.synced = True
        if not self.synced and SYNC_ON_MESSAGE:
            await self.tree.sync()
            print(f"Tree synced!")
            self.synced = True

    async def on_ready(self):
        await self.user.edit(username=BOT_USERNAME)
        for guild in self.guilds:
            await self.handle_subscriber(guild)
        self.read_messages.start()

    async def get_self_member(self, guild: discord.Guild):
        member = await guild.query_members(user_ids=[self.user.id])
        if not member:
            return None
        return member[0]

    async def handle_subscriber(self, guild):
        guild_state = GuildState(guild.id, guild.name)
        guild_name = guild_state.data[guild_state.guild_id]["guild_name"]
        subscriber = None

        if guild_name not in self.subscribers.keys():
            self.subscribers[guild_name] = Subscriber(self, guild_name, guild_state.guild_id)
            print(f" [*] Created new subscriber {guild_name}")

        subscriber = self.subscribers[guild_name]
        print(" [*] Waiting to consume messages")

    @tasks.loop(seconds=.5)
    async def read_messages(self):
        for guild_name, subscriber in self.subscribers.items():
            while not subscriber.message_queue.empty():
                print(f" [*] {subscriber.server_name} has messages!")
                message = subscriber.message_queue.get()
                subscriber.message_queue.task_done()
                message = json.loads(message)
                for guild in self.guilds:
                    if guild.name == message["source_server"]:
                        continue
                    channel = guild.get_channel(GuildState(subscriber.discord_server_id, guild.name).channel_id)
                    if not channel:
                        print(f" [***] Could not get channel for guild {guild.name}")
                        continue
                    await channel.send(embed=ChatEmbed(message))

    async def publish_message(self, message):
        self.publisher.send_message(message.data)


bot_intents = discord.Intents.default()
bot_intents.messages = True
bot_intents.guilds = True
bot_intents.members = True
bot_intents.message_content = True
discord_bot = DiscordBot(command_prefix=".", intents=bot_intents)


@discord_bot.tree.command(name="setchannel", description="Sets the channel for the bot", guilds=())
async def set_channel(interaction: discord.Interaction):
    await set_bot_channel(interaction, discord_bot)
