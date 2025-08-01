import atexit
import os
from threading import Thread
import time
import traceback

from bot.settings import TESTING
from bot.bot import discord_bot


def main():
    try:
        bot_token = os.environ['ATR_TOKEN']
        discord_bot.run(bot_token)
    except Exception as e:
        print("bot was unable to connect to server.")
        print(e)
        print(traceback.format_exc())


def release_resources():
    discord_bot.read_messages.stop()
    for guild_id, subscriber in discord_bot.subscribers.items():
        subscriber.queue.delete(subscriber.server_name)
        print(f" [*] {subscriber.server_name} queue deleted")
    discord_bot.publisher.channel.close()
    print(" [*] All resources closed")
    exit()


def quitter():
    time.sleep(5)
    while True:
        x = input(" [*] Enter 'quit' to quit: ")
        if x.lower().startswith('q'):
            release_resources()
            exit()


atexit.register(release_resources)

if __name__ == "__main__":
    quit_thread = Thread(target=quitter)
    quit_thread.start()
    main()

