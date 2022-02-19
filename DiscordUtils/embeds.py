from __future__ import annotations

import discord
from discord import embeds


class Embed(embeds.Embed):
    '''Embed which has whoose colors are randomly generated
    The `random` color are generated using :func:`discord.Color.random()`
    '''
    def __init__(self, **kwargs):
        if "colour" not in kwargs:
            kwargs["colour"] = discord.Color.random()

        super().__init__(**kwargs)


class ErrorEmbed(embeds.Embed):
    '''The Embed used to depict an :class:`Exception`
    The `red` color are generated using :func:`discord.Color.red()`
    '''
    def __init__(self, **kwargs):
        if "colour" not in kwargs:
            kwargs["colour"] = discord.Color.red()

        super().__init__(**kwargs)


class SuccessEmbed(embeds.Embed):
    '''The Embed used to depict any kind of `success`
    The `green` color are generated using :func:`discord.Color.green()`
    '''
    def __init__(self, **kwargs):
        if "colour" not in kwargs:
            kwargs["colour"] = discord.Color.green()

        super().__init__(**kwargs)


class StarboardEmbed(embeds.Embed):
    '''The Embed used to depict any kind of `warning` or `starboard` kind of :class:`~discord.Embed`
    The `green` color are generated using :func:`discord.Color.green()`
    '''
    def __init__(self, **kwargs):
        if "colour" not in kwargs:
            kwargs["colour"] = discord.Color.yellow()

        super().__init__(**kwargs)
