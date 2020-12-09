import discord
import asyncio

class InviteTracker(object):
    def __init__(self, bot):
        self.bot = bot
        self._cache = {}
        
    async def cache_invites(self):
        for guild in self.bot.guilds:
            self._cache[guild.id] = {}
            try:
                invs = await guild.invites()
                for invite in invs:
                    if invite.inviter not in self._cache[guild.id].keys():
                        self._cache[guild.id][invite.inviter] = []
                    self._cache[guild.id][invite.inviter].append(invite)
            except discord.errors.Forbidden:
                pass
        
    async def update_invite_cache(self, invite):
        try:
            if not invite.guild.id in self._cache.keys():
                self._cache[invite.guild.id] = {}
            if not invite.inviter in self._cache[invite.guild.id].keys():
                self._cache[invite.guild.id][invite.inviter] = []
            self._cache[invite.guild.id][invite.inviter].append(invite)
        except discord.errors.Forbidden:
            return
    
    async def remove_invite_cache(self, invite):
        for key in self._cache:
            for lists in self._cache[key]:
                user = self._cache[key][lists]
                if invite in user:
                    self._cache[key][lists].remove(invite)
                    break
                    
    async def remove_guild_cache(self, guild):
        if guild.id in self._cache.keys():
            del self._cache[guild.id]
                
    async def update_guild_cache(self, guild):
        try:
            invs = await guild.invites()
            self._cache[guild.id] = {}
            for invite in invs:
                if not invite.inviter in self._cache[guild.id].keys():
                    self._cache[guild.id][invite.inviter] = []
                self._cache[guild.id][invite.inviter].append(invite)
        except discord.errors.Forbidden:
            return
        
    async def fetch_inviter(self, member):
        invited_by = None
        invs = {}
        try:
            new_invites = await member.guild.invites()
        except discord.errors.Forbidden:
            return
        for invite in new_invites:
            if not invite.inviter in invs.keys():
                invs[invite.inviter] = []
            invs[invite.inviter].append(invite)
        for new_invite_key in invs:
            for cached_invite_key in self._cache[member.guild.id]:
                if new_invite_key == cached_invite_key:
                    new_invite_list = invs[new_invite_key]
                    cached_invite_list = self._cache[member.guild.id][cached_invite_key]
                    for new_invite in new_invite_list:
                        for old_invite in cached_invite_list:
                            if new_invite.code == old_invite.code and new_invite.uses-old_invite.uses >= 1:
                                cached_invite_list.remove(old_invite)
                                cached_invite_list.append(new_invite)
                                return new_invite_key
                                break
        else:
            return None