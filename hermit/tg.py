import asyncio
import functools
import os
import signal
import traceback

from telethon import TelegramClient, events, sync
from subprocess import Popen, PIPE

from .bot import HermitBot
from .cli import data_dir


class ShellObject:
    """A Bourne Shell object handler for RiveScript."""
    _objects = {}

    def load(self, name, code):
        source = "\n".join(code)
        self._objects[name] = source

    def call(self, rs, name, user, fields):
        if not name in self._objects:
            return "[ERR: Object Not Found]"
        script = f'#!/usr/bin/env sh\n'.encode('utf-8')
        vars = rs.get_uservars(user)
        for key, value in vars.items():
            if type(value) != str:
                continue
            script += f'{key}="{value}"\n'.encode('utf-8')
        script += self._objects[name].encode('utf-8')

        proc = Popen(["sh"], stdin=PIPE, stdout=PIPE)
        proc.stdin.write(script)
        proc.stdin.close()
        result = proc.stdout.read().decode('utf-8')
        return result


APP_TOKEN = os.environ['TELEGRAM_APP_TOKEN']
BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
BOT_OWNER = os.environ['TELEGRAM_BOT_OWNER']
BOT_OWNER_ID = int(os.environ['TELEGRAM_BOT_OWNER_ID'])
BOT_NAME = os.environ['TELEGRAM_BOT_NAME']
api_id, api_hash = APP_TOKEN.split(':')
api_id = int(api_id)

loop = asyncio.get_event_loop()

client = TelegramClient(BOT_NAME, api_id, api_hash)

hermit = HermitBot(data_dir, debug=False)


def exit_on_signal(signal_name):
    client.send_message(BOT_OWNER, 'I am going offline.')
    client.disconnect()
    loop.stop()


def stop_on_error(func):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            await client.send_message(BOT_OWNER, 'Encountered error, shutting down. ```%s```' % traceback.format_exc())
            client.disconnect()
            loop.stop()

    return wrapper


@client.on(events.NewMessage(pattern='reload'))
@stop_on_error
async def reload_handler(event):
    if event.from_id != BOT_OWNER_ID:
        print(f"Ignoring chat from {event.from_id}.")
        return
    hermit.reload()
    await event.respond('Reloaded.')


@client.on(events.NewMessage())
@stop_on_error
async def handler(event):
    if event.from_id != BOT_OWNER_ID:
        print(f"Ignoring chat from {event.from_id}.")
        return
    elif event.raw_text == 'reload':
        return
    reply = hermit.reply(event.raw_text)
    if reply:
        await event.respond(reply)
    else:
        await event.respond('Received empty response.')


def main():
    try:
        for signame in ('SIGINT', 'SIGTERM'):
            loop.add_signal_handler(getattr(signal, signame),
                                    functools.partial(exit_on_signal, signame))
        client.connect()
        if not client.is_user_authorized():
            client.sign_in(bot_token=BOT_TOKEN)

        client.send_message(BOT_OWNER, 'I am online.')

        loop.run_forever()
    except KeyboardInterrupt:
        client.send_message(BOT_OWNER, 'I am going offline.')
    except Exception as e:
        client.send_message(BOT_OWNER, 'Encountered error, shutting down. ```%s```' % traceback.format_exc())
    finally:
        client.disconnect()
        loop.stop()
