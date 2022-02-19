from asyncio import sleep
from typing import Optional, Union

import discord
from discord import AuditLogAction
from discord.errors import Forbidden
from discord.ext import commands


class InviteTracker:
    """A usefull class to track invites of member whenever a user is invited to a guild.

    :param bot:
    :type bot: Union[~discord.Client, ~discord.AutoShardedClient, ~discord.ext.commands.Bot, ~discord.ext.commands.AutoSharededBot]
    
    :attributes: 
        - bot: The default bot class.
        - _cache: :class:`dict`
            A `dict` to cache :class:`~discord.Guild` instances :class:`~discord.Invite`
    """ 
    __slots__ = ['bot', '_cache']
    def __init__(self, bot: Union[discord.Client, discord.AutoShardedClient, commands.Bot, commands.AutoShardedBot]):       
        self.bot = bot
        self._cache = {}
        self.add_listeners()

    def add_listeners(self) -> None:
        """It adds the following listeners to the :class:`~discord.ext.commands.Bot` instance.

        :Mapping:
            +-----------------------------+-----------------------------------+
            | Function                    | Discord Function                  |
            +-----------------------------+-----------------------------------+
            | :func:`cache_invites`       | :func:`~discord.on_ready`         |
            +-----------------------------+-----------------------------------+
            | :func:`update_invite_cache` | :func:`~discord.on_invite_create` |
            +-----------------------------+-----------------------------------+
            | :func:`remove_invite_cache` | :func:`~discord.on_invite_delete` |
            +-----------------------------+-----------------------------------+
            | :func:`add_guild_cache`     | :func:`~discord.on_guild_join`    |
            +-----------------------------+-----------------------------------+
            | :func:`remove_guild_cache`  | :func:`~discord.on_guild_remove`  |
            +-----------------------------+-----------------------------------+
        """        
        self.bot.add_listener(self.cache_invites, "on_ready")
        self.bot.add_listener(self.update_invite_cache, "on_invite_create")
        self.bot.add_listener(self.remove_invite_cache, "on_invite_delete")
        self.bot.add_listener(self.add_guild_cache, "on_guild_join")
        self.bot.add_listener(self.remove_guild_cache, "on_guild_remove")

    async def cache_invites(self) -> None:
        '''It cache the guild invites `automatically` whenever the :func:`~discord.on_ready` event is fired'''
        for guild in self.bot.guilds:
            try:
                self._cache[guild.id] = {}
                for invite in await guild.invites():
                    self._cache[guild.id][invite.code] = invite
            except Forbidden:
                continue

    async def update_invite_cache(self, invite: discord.Invite) -> None:
        '''It updates the invite cache `automatically` whenever the :func:`~discord.on_invite_create` event is fired'''
        if invite.guild.id not in self._cache:
            self._cache[invite.guild.id] = {}
        self._cache[invite.guild.id][invite.code] = invite

    async def remove_invite_cache(self, invite: discord.Invite):
        '''It removes the invite cache of the deleted invite `automatically` whenever the :func:`~discord.on_invite_delete` event is fired'''
        if invite.guild.id not in self._cache:
            return
        ref_invite = self._cache[invite.guild.id][invite.code]
        if ((ref_invite.created_at.timestamp() + ref_invite.max_age > discord.utils.utcnow().timestamp() or ref_invite.max_age == 0)
                and ref_invite.max_uses > 0
                and ref_invite.uses == ref_invite.max_uses - 1):
            try:
                async for entry in invite.guild.audit_logs(limit=1, action=AuditLogAction.invite_delete):
                    if entry.target.code != invite.code:
                        self._cache[invite.guild.id][
                            ref_invite.code].revoked = True
                        return
                else:
                    self._cache[invite.guild.id][ref_invite.code].revoked = True
                    return
            except Forbidden:
                self._cache[invite.guild.id][ref_invite.code].revoked = True
                return
        else:
            self._cache[invite.guild.id].pop(invite.code)

    async def add_guild_cache(self, guild: discord.Guild) -> None:
        '''It adds the guild to cache `automatically` whenever the :func:`~discord.on_guild_join` event is fired'''
        self._cache[guild.id] = {}
        for invite in await guild.invites():
            self._cache[guild.id][invite.code] = invite

    async def remove_guild_cache(self, guild: discord.Guild) -> None:
        '''It removes the guild from cache `automatically` whenever the :func:`~discord.on_guild_remove` event is fired'''
        try:
            self._cache.pop(guild.id)
        except KeyError:
            return

    async def fetch_inviter(self, member: discord.Member) -> Optional[discord.Invite]:
        """This utility function returns the :class:`~discord.Invite` class which was used when the member joined the guild.

        :param member: The member which joined the guild. (The :class:`~discord.Member` recieved during :func:`~discord.on_member_join` event)
        :type member: discord.Member
        :return: If the member was bot i.e. invited via integration then it would return :class:`None`
        :rtype: Optional[discord.Invite]
        """        
        await sleep(self.bot.latency)
        async for new_invite in member.guild.invites():
            for cached_invite in self._cache[member.guild.id].values():
                if (new_invite.code == cached_invite.code
                        and new_invite.uses - cached_invite.uses == 1
                        or cached_invite.revoked):
                    if cached_invite.revoked:
                        self._cache[member.guild.id].pop(cached_invite.code)
                    elif new_invite.inviter == cached_invite.inviter:
                        self._cache[member.guild.id][cached_invite.code] = new_invite
                    else:
                        self._cache[member.guild.id][cached_invite.code].uses += 1
                    return cached_invite
