# DiscordUtils
A very useful library made to be used with [discord.py](https://pypi.org/project/discord.py/)

# Installation
`pip install DiscordUtils`

# Example code

### DiscordUtils.Pagination.AutoEmbedPaginator
```python
@bot.command()
async def paginate(ctx):
    embed1 = discord.Embed(color=ctx.author.color).add_field(name="Example", value="Page 1")
    embed2 = discord.Embed(color=ctx.author.color).add_field(name="Example", value="Page 2")
    embed3 = discord.Embed(color=ctx.author.color).add_field(name="Example", value="Page 3")
    paginator = DiscordUtils.Pagination.AutoEmbedPaginator(ctx)
    embeds = [embed1, embed2, embed3]
    await paginator.run(embeds)
```

### DiscordUtils.Pagination.CustomEmbedPaginator
```python
@bot.command()
async def paginate(ctx):
    embed1 = discord.Embed(color=ctx.author.color).add_field(name="Example", value="Page 1")
    embed2 = discord.Embed(color=ctx.author.color).add_field(name="Example", value="Page 2")
    embed3 = discord.Embed(color=ctx.author.color).add_field(name="Example", value="Page 3")
    paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx)
    paginator.add_reaction('⏮️', "first")
    paginator.add_reaction('⏪', "back")
    paginator.add_reaction('🔐', "lock")
    paginator.add_reaction('⏩', "next")
    paginator.add_reaction('⏭️', "last")
    embeds = [embed1, embed2, embed3]
    await paginator.run(embeds)
```

### DiscordUtils.InviteTracker
```python
import discord
from discord.ext import commands
import DiscordUtils

bot = commands.AutoShardedBot(command_prefix=">")
tracker = DiscordUtils.InviteTracker(bot)

@bot.event
async def on_ready():
    await tracker.cache_invites()
	
@bot.event
async def on_invite_create(invite):
    await tracker.update_invite_cache(invite)

@bot.event
async def on_guild_join(guild):
    await tracker.update_guild_cache(guild)
	
@bot.event
async def on_invite_delete(invite):
    await tracker.remove_invite_cache(invite)
	
@bot.event
async def on_guild_remove(guild):
    await tracker.remove_guild_cache(guild)
	
@bot.event
async def on_member_join(member):
    inviter = await tracker.fetch_inviter(member) # inviter is the member who invited
```

**___For further information please read the docs___**

# Links
**[Documentation](https://docs.discordutils.gq)**

**[PyPi](https://pypi.discordutils.gq)**

# Support
DM/PM `toxic_recker#6764` on Discord
