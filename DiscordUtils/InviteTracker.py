import discord
import asyncio
import sys

class Cache(object):
    def __init__(self):
        self.cache = {}
        self.size = 40
    def __iter__(self):
        return self.cache

class InviteTracker(object):
    def __init__(self, bot):
        self.bot = bot
        self.__cache = Cache()
        
    async def cache_invites(self):
        for guild in self.bot.guilds:
            self.__cache.cache[guild.id] = {}
            try:
                invs = await guild.invites()
                for invite in invs:
                    if invite.inviter not in self.__cache.cache[guild.id].keys():
                        self.__cache.cache[guild.id][invite.inviter] = []
                    self.__cache.cache[guild.id][invite.inviter].append(invite)
                self.__cache.size = sys.getsizeof(self.__cache.cache)
            except discord.errors.Forbidden:
                pass
        
    async def update_invite_cache(self, invite):
        try:
            if not invite.guild.id in self.__cache.cache.keys():
                self.__cache.cache[invite.guild.id] = {}
            if not invite.inviter in self.__cache.cache[invite.guild.id].keys():
                self.__cache.cache[invite.guild.id][invite.inviter] = []
            self.__cache.cache[invite.guild.id][invite.inviter].append(invite)
            self.__cache.size = sys.getsizeof(self.__cache.cache)
        except discord.errors.Forbidden:
            return
    
    async def remove_invite_cache(self, invite):
        for key in self.__cache.cache:
            for lists in self.__cache.cache[key]:
                user = self.__cache.cache[key][lists]
                if invite in user:
                    self.__cache.cache[key][lists].remove(invite)
                    self.__cache.size = sys.getsizeof(self.__cache.cache)
                    break
                    
    async def remove_guild_cache(self, guild):
        if guild.id in self.__cache.cache.keys():
            self.__cache.size = sys.getsizeof(self.__cache.cache)
            del self.__cache.cache[guild.id]
                
    async def update_guild_cache(self, guild):
        try:
            invs = await guild.invites()
            self.__cache.cache[guild.id] = {}
            for invite in invs:
                if not invite.inviter in self.__cache.cache[guild.id].keys():
                    self.__cache.cache[guild.id][invite.inviter] = []
                self.__cache.cache[guild.id][invite.inviter].append(invite)
            self.__cache.size = sys.getsizeof(self.__cache.cache)
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
            for cached_invite_key in self.__cache.cache[member.guild.id]:
                if new_invite_key == cached_invite_key:
                    new_invite_list = invs[new_invite_key]
                    cached_invite_list = self.__cache.cache[member.guild.id][cached_invite_key]
                    for new_invite in new_invite_list:
                        for old_invite in cached_invite_list:
                            if new_invite.code == old_invite.code and new_invite.uses-old_invite.uses >= 1:
                                cached_invite_list.remove(old_invite)
                                cached_invite_list.append(new_invite)
                                self.__cache.size = sys.getsizeof(self.__cache.cache)
                                return new_invite_key
                                break
        else:
            return None