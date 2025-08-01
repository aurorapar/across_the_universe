
class RabbitMessage:

    def __init__(self, user_account, user_name, source_server, source_channel, message, time):
        super().__init__()
        self.data = {
            'user_account': user_account,
            'user_name': user_name,
            'source_server': source_server,
            'source_channel': source_channel,
            'message': message,
            'time': time
        }

        self.user_account = self.data['user_account']
        self.user_name = self.data['user_name']
        self.source_server = self.data['source_server']
        self.source_channel = self.data['source_channel']
        self.message = self.data['message']
        self.time = self.data['time']
