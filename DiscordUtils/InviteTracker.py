from discord.errors import Forbidden
from discord import AuditLogAction
from datetime import datetime

class InviteTracker():
	def __init__(self, bot):
		self.bot = bot
		self._cache = {}
		self.add_listeners()
	
	def add_listeners(self):
		self.bot.add_listener(self.cache_invites, "on_ready")
		self.bot.add_listener(self.update_invite_cache, "on_invite_create")
		self.bot.add_listener(self.remove_invite_cache, "on_invite_delete")
		self.bot.add_listener(self.add_guild_cache, "on_guild_join")
		self.bot.add_listener(self.remove_guild_cache, "on_guild_remove")
		async def member_join(member):
			return await self.add_guild_cache(member.guild)
		self.bot.add_listener(member_join, "on_member_join")
	
	async def cache_invites(self):
		for guild in self.bot.guilds:
			try:
				self._cache[guild.id] = await guild.invites()
			except Forbidden:
				continue
	
	async def update_invite_cache(self, invite):
		if invite.guild.id not in self._cache.keys():
			self._cache[invite.guild.id] = []
		self._cache[invite.guild.id].append(invite)
	
	async def remove_invite_cache(self, invite):
		if invite.guild.id not in self._cache.keys():
			return
		ref_invite = None
		ref_invite_index = 0
		for i, inv in enumerate(self._cache[invite.guild.id]):
			if inv.code == invite.code:
				ref_invite = self._cache[invite.guild.id][i]
				ref_invite_index = i
				break
		if ref_invite.max_uses > 0 and ref_invite.created_at.timestamp()+ref_invite.max_age > datetime.utcnow().timestamp() and ref_invite.uses == ref_invite.max_uses-1:
				try:
					async for entry in invite.guild.audit_logs(limit=1, action=AuditLogAction.invite_delete):
						if entry.target.code != invite.code:
							self._cache[invite.guild.id][ref_invite_index].revoked = True
							return
				except Forbidden:
					self._cache[invite.guild.id][ref_invite_index].revoked = True
					return
		for i, inv in enumerate(self._cache[invite.guild.id]):
			if inv.code == invite.code:
				self._cache[invite.guild.id].pop(i)
				return
	
	async def add_guild_cache(self, guild):
		self._cache[guild.id] = await guild.invites()
	
	async def remove_guild_cache(self, guild):
		try:
			self._cache.pop(guild.id)
		except KeyError:
			return
	
	async def fetch_inviter(self, member):
		invites = await member.guild.invites()
		cached_invites = self._cache[member.guild.id]
		for new_invite in invites:
			for cached_invite in cached_invites:
				if new_invite.code == cached_invite.code and new_invite.uses - cached_invite.uses >= 1 or cached_invite.revoked:
					return new_invite.inviter