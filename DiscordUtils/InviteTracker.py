from discord.errors import Forbidden
from discord import AuditLogAction
from datetime import datetime
from asyncio import sleep

class InviteTracker():
    def __init__(self, bot):
        """
        Create a new instance of the InviteTracker

        params:
            bot: The bot object
            type: discord.Client

        returns:
            NoneType: None
        """
        self.bot = bot
        self._cache = {}
        self.add_listeners()

    def add_listeners(self):
        self.bot.add_listener(self.cache_invites, "on_ready")
        self.bot.add_listener(self.update_invite_cache, "on_invite_create")
        self.bot.add_listener(self.remove_invite_cache, "on_invite_delete")
        self.bot.add_listener(self.add_guild_cache, "on_guild_join")
        self.bot.add_listener(self.remove_guild_cache, "on_guild_remove")

    async def cache_invites(self):
        """
        Cache the invites for all the guilds.

        returns:
            NoneType: None
        """
        for guild in self.bot.guilds:
            try:
                self._cache[guild.id] = {}
                for invite in await guild.invites():
                    self._cache[guild.id][invite.code] = invite
            except Forbidden:
                continue

    async def update_invite_cache(self, invite):
        """
        Cache an invite.
        params:
            invite: The invite object
            type: discord.Invite
        returns:
            NoneType; None
        """
        if invite.guild.id not in self._cache.keys():
            self._cache[invite.guild.id] = {}
        self._cache[invite.guild.id][invite.code] = invite

    async def remove_invite_cache(self, invite):
        """
        Removr the cache for an invite
        params:
            invite: The invite to remove the cache of
            type: discord.Invite
        returns:
            NoneType: None
        """
        if invite.guild.id not in self._cache.keys():
            return
        ref_invite = self._cache[invite.guild.id][invite.code]
        if (ref_invite.created_at.timestamp()+ref_invite.max_age > datetime.utcnow().timestamp() or ref_invite.max_age == 0) and ref_invite.max_uses > 0 and ref_invite.uses == ref_invite.max_uses-1:
            try:
                async for entry in invite.guild.audit_logs(limit=1, action=AuditLogAction.invite_delete):
                    if entry.target.code != invite.code:
                        self._cache[invite.guild.id][ref_invite.code].revoked = True
                        return
                else:
                    self._cache[invite.guild.id][ref_invite.code].revoked = True
                    return
            except Forbidden:
                self._cache[invite.guild.id][ref_invite.code].revoked = True
                return
        else:
            self._cache[invite.guild.id].pop(invite.code)

    async def add_guild_cache(self, guild):
        """
        Cache the invites for a guild
        params:
            guild: The guild to cache the invites for
            type: discord.Guild
        returns:
            NoneType: None
        """
        self._cache[guild.id] = {}
        for invite in await guild.invites():
            self._cache[guild.id][invite.code] = invite

    async def remove_guild_cache(self, guild):
        """
        Clear the invite cache for a guild
        params:
            guild: The guild to clear the invite cache for
            type: discord.Guild
        returns:
            NoneType: None
        """
        try:
            self._cache.pop(guild.id)
        except KeyError:
            return

    async def fetch_inviter(self, member):
        """
        Fetch the inviter for a member, Note: The invite must be in bot's cache
        params:
            member: The member to fetch the inviter for
            type: discord.Member
        returns:
            Union[discord.Member, NoneType]: Returns the member who invited the user, returns NoneType instead if it could not find it our
        """
        await sleep(self.bot.latency)
        for new_invite in await member.guild.invites():
            for cached_invite in self._cache[member.guild.id].values():
                if new_invite.code == cached_invite.code and new_invite.uses - cached_invite.uses == 1 or cached_invite.revoked:
                    if cached_invite.revoked:
                        self._cache[member.guild.id].pop(cached_invite.code)
                    elif new_invite.inviter == cached_invite.inviter:
                        self._cache[member.guild.id][cached_invite.code] = new_invite
                    else:
                        self._cache[member.guild.id][cached_invite.code].uses += 1
                    return cached_invite.inviter
