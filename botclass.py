import discord
from discord.ext import commands
import importlib
import random
import string
import re
import sys
import asyncio
import os

__all__ = ['WightBot', ]


class Prefix:

    def __init__(self, prefix):
        self.prefix = prefix
        self.pattern = re.compile(re.escape(prefix) + r'(\s+)')

    async def __call__(self, bot, message):
        match = self.pattern.search(message.content)
        if match:
            prefix = self.prefix + match.group(1)
        else:
            prefix = self.prefix
            while prefix in message.content:
                prefix = ''.join(random.sample(string.ascii_letters + string.digits, k=10))
        return prefix


class WightBot(commands.Bot):

    def __init__(self, loop=None, **options):
        options["intents"] = discord.Intents.all()
        super().__init__(loop=loop, command_prefix=Prefix('!k'), **options)
        self.remove_command('help')

    async def setup_hook(self):
        path = os.path.join(os.path.dirname(__file__), '..')
        sys.path.append(path)
        names = ('main',)
        for name in names:
            if __package__:
                libname = f'{__package__}.{name}'
            else:
                libname = f'{name}'
            lib = importlib.import_module(libname)
            await lib.setup(self)
        sys.path.remove(path)

    async def close(self):
        futs = self.extra_events.get('on_close', [])
        if futs:
            await asyncio.wait([f() for f in futs])
        await super().close()
