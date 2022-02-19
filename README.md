# DiscordUtils
A very useful library made to be used in with [discord.py](https://pypi.org/project/discord.py/)

# Note
This is my version of DiscordUtils, as the original is no longer maintained. [[See Here](https://github.com/toxicrecker/DiscordUtils#readme)]

I have started to maintain this lib for my own bot which is [Minato Namikaze](https://minato-namikaze.readthedocs.io/).
I don't know if this works with `pycord` or not since I don't use pycord personally for my any of the projects. So please do not dm me about this, if this lib supports `pycord` or not.

I use [StockerMC discord.py](https://github.com/StockerMC/discord.py) and it works very well with that lib.
But if you want to use my fork of `DiscordUtils` then you can use it as I have removed the `discord.py` as a `required` dependency.

```note
This lib would work with any discord.py fork, as long as that fork provides the functions, classes and namespace that the original discord.py used to provide
```

# Installation
For access to many utily classes:
```
pip install git+https://github.com/The-4th-Hokage/DiscordUtils.git@master
```

instead use the following for access to Music functions aswell
```
pip install git+https://github.com/The-4th-Hokage/DiscordUtils.git@master
pip install .[voice]
```
Requires discord.py[voice] so make sure you have all dependencies of it installed.

also use the following for access to Paginator classes aswell
```
pip install git+https://github.com/The-4th-Hokage/DiscordUtils.git@master
pip install git+https://github.com/Rapptz/discord-ext-menus.git@master
```

# Example code

### DiscordUtils.InviteTracker
```python
import discord
from discord.ext import commands
import DiscordUtils

intents = discord.intents.default()
intents.members = True
bot = commands.AutoShardedBot(command_prefix=">", intents=intents)
tracker = DiscordUtils.InviteTracker(bot)

@bot.event
async def on_member_join(member):
    inviter = await tracker.fetch_inviter(member) # inviter is the member who invited
```

### DiscordUtils.Music
```python
import discord
from discord.ext import commands
import DiscordUtils

bot = commands.AutoShardedBot(command_prefix=">")
music = DiscordUtils.Music()

@bot.command()
async def join(ctx):
    await ctx.author.voice.channel.connect() #Joins author's voice channel
    
@bot.command()
async def leave(ctx):
    await ctx.voice_client.disconnect()
    
@bot.command()
async def play(ctx, *, url):
    player = music.get_player(guild_id=ctx.guild.id)
    if not player:
        player = music.create_player(ctx, ffmpeg_error_betterfix=True)
    if not ctx.voice_client.is_playing():
        await player.queue(url, search=True)
        song = await player.play()
        await ctx.send(f"Playing {song.name}")
    else:
        song = await player.queue(url, search=True)
        await ctx.send(f"Queued {song.name}")
        
@bot.command()
async def pause(ctx):
    player = music.get_player(guild_id=ctx.guild.id)
    song = await player.pause()
    await ctx.send(f"Paused {song.name}")
    
@bot.command()
async def resume(ctx):
    player = music.get_player(guild_id=ctx.guild.id)
    song = await player.resume()
    await ctx.send(f"Resumed {song.name}")
    
@bot.command()
async def stop(ctx):
    player = music.get_player(guild_id=ctx.guild.id)
    await player.stop()
    await ctx.send("Stopped")
    
@bot.command()
async def loop(ctx):
    player = music.get_player(guild_id=ctx.guild.id)
    song = await player.toggle_song_loop()
    if song.is_looping:
        await ctx.send(f"Enabled loop for {song.name}")
    else:
        await ctx.send(f"Disabled loop for {song.name}")
    
@bot.command()
async def queue(ctx):
    player = music.get_player(guild_id=ctx.guild.id)
    await ctx.send(f"{', '.join([song.name for song in player.current_queue()])}")
    
@bot.command()
async def np(ctx):
    player = music.get_player(guild_id=ctx.guild.id)
    song = player.now_playing()
    await ctx.send(song.name)
    
@bot.command()
async def skip(ctx):
    player = music.get_player(guild_id=ctx.guild.id)
    data = await player.skip(force=True)
    if len(data) == 2:
        await ctx.send(f"Skipped from {data[0].name} to {data[1].name}")
    else:
        await ctx.send(f"Skipped {data[0].name}")

@bot.command()
async def volume(ctx, vol):
    player = music.get_player(guild_id=ctx.guild.id)
    song, volume = await player.change_volume(float(vol) / 100) # volume should be a float between 0 to 1
    await ctx.send(f"Changed volume for {song.name} to {volume*100}%")
    
@bot.command()
async def remove(ctx, index):
    player = music.get_player(guild_id=ctx.guild.id)
    song = await player.remove_from_queue(int(index))
    await ctx.send(f"Removed {song.name} from queue")
```

### DiscordUtils.embeds
```python
import discord
from discord.ext import commands
import DiscordUtils import Embed, ErrorEmbed, SuccessEmbed, StarboardEmbed

bot = commands.AutoShardedBot(command_prefix=">")

@bot.command()
async def embed(ctx):
    await ctx.send(embed=Embed(title="Embed",description="A embed with random colors"))

@bot.command()
async def error_emebed(ctx):
    await ctx.send(embed=ErrorEmbed(title="Embed",description="Oh no an error happened"))

@bot.command()
async def success(ctx):
    await ctx.send(embed=SuccessEmbed(title="Embed",description="Yaay! task executed successfully"))

@bot.command()
async def starboard(ctx):
    await ctx.send(embed=StarboardEmbed(title="Embed",description="Warning given/ starboard embed"))
```

For further information please read the docs

# Links
**[Documentation](https://docs.discordutils.gq)**

**[Github](https://github.com/The-4th-Hokage/DiscordUtils)**

# Support
**__Please make sure that you are on the latest version of [DiscordUtils](https://github.com/The-4th-Hokage/DiscordUtils) and [youtube_dl](https://pypi.org/project/youtube_dl) before contacting for support__**

DM/PM `HATSUNE MIKU#9955` on Discord for support
