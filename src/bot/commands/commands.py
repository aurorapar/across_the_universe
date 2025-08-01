import discord
from discord.ext.commands import Bot

from ..dtos import GuildState


async def set_bot_channel(interaction: discord.Interaction, bot: Bot):
    user = interaction.user
    if not user.guild_permissions.manage_roles:
        return

    guild = interaction.guild
    guild_state = GuildState(guild.id, guild.name)
    channel = interaction.channel
    guild_state.set_channel(channel.id)

    overwrite = discord.PermissionOverwrite()
    overwrite.send_messages = True
    overwrite.view_channel = True
    overwrite.use_application_commands = True
    await channel.set_permissions(user.guild.get_member(bot.user.id), overwrite=overwrite)
    await channel.send(f"I have been set to this channel by {user.mention}")
    await interaction.response.send_message(ephemeral=True, content=f"command successful")
    await bot.handle_subscriber(guild)



async def disable(interaction):
    return await interaction.response.send_message(ephemeral=True, content="This command has been disabled.")
