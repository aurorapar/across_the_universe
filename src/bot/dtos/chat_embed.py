from time import strftime, localtime

from discord import Embed
from ..settings import DATE_FORMAT


class ChatEmbed(Embed):

    def __init__(self, message):

        super().__init__(
            title=f'{message["user_account"]}/{message["user_name"]}',
            description=message["message"]
        )
        self.add_field(name="Home Server", value=message["source_server"])
        self.add_field(name="Time", value=strftime(DATE_FORMAT, localtime(message["time"])))
