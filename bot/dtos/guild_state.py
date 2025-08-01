import json
import os


class GuildState:

    data_dir = "data"
    data_file = os.path.join(data_dir, "data.json")

    def __init__(self, guild_id, guild_name):
        self.data = {}
        self.guild_id = str(guild_id)
        self.channel_id = None
        self.subscriber = None

        if not os.path.exists(self.data_dir):
            os.mkdir(self.data_dir)
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                self.data = json.load(f)

        if self.guild_id not in self.data.keys():
            self.data[self.guild_id] = {
                "guild_name": guild_name,
                "channel": None
            }
        else:
            self.channel_id = self.data[self.guild_id]["channel"]

    def set_channel(self, channel_id):
        self.data[self.guild_id]["channel"] = channel_id
        self.channel_id = int(channel_id)
        self.save()

    def has_channel(self):
        if 'channel' not in self.data[self.guild_id].keys():
            return False
        if not self.data[self.guild_id]['channel']:
            return False
        return True

    def save(self):
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f)
