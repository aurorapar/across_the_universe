# Across The Universe
# Discord Bot

Allows Linking Multiple Discord Server Channels For Full-Duplex Communication

* Invite to your server using [This Link](https://discord.com/oauth2/authorize?client_id=1400556907864784926)
* Give the bot permission (Use Application Command) to the channel you want to use it in
* Use the `/setchannel` command to link the desired channel

Any server which has done the same will be able to receive and send messages from these channels.

![example server message](https://spawningpool.net/images/atu_example.PNG)

Current limitations:
* All severs connected will broadcast to all others. This functions as every server publishes to the same RabbitMQ 
exchange. This could be expanded in the future.
* There is no authentication for servers joining. Any server that wishes to do so may.

## Developer Notes

Set bot token as an environment variable, `ATR_TOKEN`

Create a fanout exchange in RabbitMQ.

Use the fanout name in `src/bot/queue_handlers/` for `publisher.py` and `subscriber.py`, and set the following as well:
```
USERNAME = os.environ['RABBITMQ_USER']
PASSWORD = os.environ['RABBITMQ_PASSWORD']
HOST = ''
EXCHANGE = ''
```

Quit by entering `quit` on the command line when started. This has the added benefit of deconstructing all various
server queues bound to the exchange.

All servers at this time listen on the same exchange, and there is no authentication for joining the exchange. 