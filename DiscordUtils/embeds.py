import discord
from discord import embeds


class Embed(embeds.Embed):
    def __init__(self, **kwargs):
        if "colour" not in kwargs:
            kwargs["colour"] = discord.Color.random()

        super().__init__(**kwargs)


class ErrorEmbed(embeds.Embed):
    def __init__(self, **kwargs):
        if "colour" not in kwargs:
            kwargs["colour"] = discord.Color.red()

        super().__init__(**kwargs)


class SuccessEmbed(embeds.Embed):
    def __init__(self, **kwargs):
        if "colour" not in kwargs:
            kwargs["colour"] = discord.Color.green()

        super().__init__(**kwargs)


class StarboardEmbed(embeds.Embed):
    def __init__(self, **kwargs):
        if "colour" not in kwargs:
            kwargs["colour"] = discord.Color.yellow()

        super().__init__(**kwargs)
