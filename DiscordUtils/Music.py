import asyncio
from typing import Callable, Iterable, Optional, Tuple, Union

import aiohttp
from discord.ext import commands

try:
    import discord
    import youtube_dl

    has_voice = True
except ImportError:
    has_voice = False

if has_voice:
    youtube_dl.utils.bug_reports_message = lambda: ""
    ydl = youtube_dl.YoutubeDL({
        "format": "bestaudio/best",
        "restrictfilenames": True,
        "noplaylist": True,
        "nocheckcertificate": True,
        "ignoreerrors": True,
        "logtostderr": False,
        "quiet": True,
        "no_warnings": True,
        "source_address": "0.0.0.0",
    })


class EmptyQueue(Exception):
    """Cannot skip because queue is empty"""


class NotConnectedToVoice(Exception):
    """Cannot create the player because bot is not connected to voice"""


class NotPlaying(Exception):
    """Cannot <do something> because nothing is being played"""


async def ytbettersearch(query) -> str:
    '''Formats the search string for the YouTube music search'''
    url = f"https://www.youtube.com/results?search_query={query}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            html = await resp.text()
    index = html.find("watch?v")
    url = ""
    while True:
        char = html[index]
        if char == '"':
            break
        url += char
        index += 1
    url = f"https://www.youtube.com/{url}"
    return url


class Song: 
    """The requested song data
    """    
    __slots__ = [
        'source',
        'url',
        'title',
        'description',
        'views',
        'duration',
        'thumbnail',
        'channel',
        'channel_url',
        'loop'
    ]
    def __init__(
        self,
        source: str,
        url: str,
        title: str,
        description: str,
        views: int,
        duration: Union[str,int],
        thumbnail: str,
        channel: str,
        channel_url: str,
        loop: bool,
    ):
        self.source = source
        self.url = url
        self.title = title
        self.description = description
        self.views = views
        self.name = title
        self.duration = duration
        self.thumbnail = thumbnail
        self.channel = channel
        self.channel_url = channel_url
        self.is_looping = loop



async def get_video_data(url, search: bool, bettersearch:bool, loop: Optional[asyncio.AbstractEventLoop]) -> Song:
    """It returns required video data after searching `YouTube`

    :raises RuntimeError: Is raised when the package is install without the .[voice] parameters
    :return: The song data in a formatted way
    :rtype: :class:`Song`
    """    
    if not has_voice:
        raise RuntimeError("DiscordUtils[voice] install needed in order to use voice")

    if not search and not bettersearch:
        data = await loop.run_in_executor(
            None, lambda: ydl.extract_info(url, download=False))
        source = data.get("url")
        url = "https://www.youtube.com/watch?v=" + data.get("id")
        title = data.get("title")
        description = data.get("description")
        views = data.get("view_count")
        duration = data.get("duration")
        thumbnail = data.get("thumbnail")
        channel = data.get("uploader")
        channel_url = data.get("uploader_url")
        return Song(
            source,
            url,
            title,
            description,
            views,
            duration,
            thumbnail,
            channel,
            channel_url,
            False,
        )
    if bettersearch:
        url = await ytbettersearch(url)
        data = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=False))
        source = data.get("url")
        url = "https://www.youtube.com/watch?v=" + data.get("id")
        title = data.get("title")
        description = data.get("description")
        views = data.get("view_count")
        duration = data.get("duration")
        thumbnail = data.get("thumbnail")
        channel = data.get("uploader")
        channel_url = data.get("uploader_url")
        return Song(
            source,
            url,
            title,
            description,
            views,
            duration,
            thumbnail,
            channel,
            channel_url,
            False,
        )
    ytdl = youtube_dl.YoutubeDL({
        "format": "bestaudio/best",
        "restrictfilenames": True,
        "noplaylist": True,
        "nocheckcertificate": True,
        "ignoreerrors": True,
        "logtostderr": False,
        "quiet": True,
        "no_warnings": True,
        "default_search": "auto",
        "source_address": "0.0.0.0",
    })
    data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
    try:
        data = data["entries"][0]
    except (KeyError, TypeError):
        pass
    source = data.get("url")
    url = "https://www.youtube.com/watch?v=" + data.get("id")
    title = data.get("title")
    description = data.get("description")
    views = data.get("view_count")
    duration = data.get("duration")
    thumbnail = data.get("thumbnail")
    channel = data.get("uploader")
    channel_url = data.get("uploader_url")
    return Song(
        source,
        url,
        title,
        description,
        views,
        duration,
        thumbnail,
        channel,
        channel_url,
        False,
    )


def check_queue(ctx: commands.Context, opts: dict, music: 'Music', after: Callable, on_play: Callable, loop: Optional[asyncio.AbstractEventLoop]) -> None:
    """It checks the music queue

    :param ctx: The commands `context`
    :type ctx: commands.Context
    :param opts: A set options for `ffmpeg`
    :type opts: dict
    :param music: The master class where the all the players data is stored
    :type music: Music
    :param after: The :func:`check_queue` which would be called afterwards
    :type after: Callable
    :param on_play: :func:`MusicPlayer.on_play` function
    :type on_play: MusicPlayer.on_play
    :param loop: The event loop in which the :class:`~discord.ext.commands.Bot` is running
    :type loop: Optional[asyncio.AbstractEventLoop]
    :raises RuntimeError: Is raised when the package is install without the .[voice] parameters
    """    
    if not has_voice:
        raise RuntimeError("DiscordUtils[voice] install needed in order to use voice")

    try:
        song = music.queue[ctx.guild.id][0]
    except IndexError:
        return
    if not song.is_looping:
        try:
            music.queue[ctx.guild.id].pop(0)
        except IndexError:
            return
        if len(music.queue[ctx.guild.id]) > 0:
            source = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio(music.queue[ctx.guild.id][0].source,
                                       **opts))
            ctx.voice_client.play(
                source,
                after=lambda error: after(ctx, opts, music, after, on_play,loop),
            )
            song = music.queue[ctx.guild.id][0]
            if on_play:
                loop.create_task(on_play(ctx, song))
    else:
        source = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(music.queue[ctx.guild.id][0].source,**opts))
        ctx.voice_client.play(
            source,
            after=lambda error: after(ctx, opts, music, after, on_play, loop))
        song = music.queue[ctx.guild.id][0]
        if on_play:
            loop.create_task(on_play(ctx, song))


class MusicPlayer:
    """The class which acts a music controller/player

    :raises RuntimeError: Is raised when the package is install without the .[voice] parameters
    :raises NotPlaying: See :func:`skip`, :func:`stop`, :func:`resume`, :func:`pause`, :func:`toggle_song_loop`, :func:`change_volume`, :func:`remove_from_queue`
    :raises EmptyQueue: See :func:`skip`, :func:`current_queue`
    """    
    __slots__ = [
        'ctx', 
        'voice', 
        'loop',
        'music',
        'after_func',
        'on_play_func',
        'on_queue_func',
        'on_skip_func',
        'on_stop_func',
        'on_pause_func',
        'on_resume_func',
        'on_loop_toggle_func',
        'on_volume_change_func',
        'on_remove_from_queue_func',
        'ffmpeg_opts'
    ]
    def __init__(self, ctx:commands.Context , music: 'Music', **kwargs):
        if not has_voice:
            raise RuntimeError("DiscordUtils[voice] install needed in order to use voice")

        self.ctx = ctx
        self.voice: Optional[discord.VoiceProtocol] = ctx.voice_client
        self.loop: Optional[asyncio.AbstractEventLoop] = ctx.bot.loop
        self.music = music
        if self.ctx.guild.id not in self.music.queue:
            self.music.queue[self.ctx.guild.id] = []
        
        self.after_func: Callable = check_queue
        self.on_play_func: Optional[Callable] = None
        self.on_queue_func:  Optional[Callable] = None
        self.on_skip_func:  Optional[Callable] = None
        self.on_stop_func:  Optional[Callable] = None
        self.on_pause_func:  Optional[Callable] = None
        self.on_resume_func:  Optional[Callable] = None
        self.on_loop_toggle_func: Optional[Callable] = None
        self.on_volume_change_func: Optional[Callable] = None
        self.on_remove_from_queue_func: Optional[Callable] = None

        ffmpeg_error = kwargs.get("ffmpeg_error_betterfix", kwargs.get("ffmpeg_error_fix"))

        if ffmpeg_error and "ffmpeg_error_betterfix" in kwargs:
            self.ffmpeg_opts: dict = {
                "options":
                "-vn -loglevel quiet -hide_banner -nostats",
                "before_options":
                "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 0 -nostdin",
            }
        elif ffmpeg_error:
            self.ffmpeg_opts: dict = {
                "options":
                "-vn",
                "before_options":
                "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 0 -nostdin",
            }
        else:
            self.ffmpeg_opts: dict = {"options": "-vn", "before_options": "-nostdin"}

    def disable(self):
        '''It disables the `Music Player`'''
        self.music.players.remove(self)

    def on_queue(self, func: Callable) -> None:
        """The event when the song is `queued`

        :param func:
        :type func: Callable
        """
        self.on_queue_func = func

    def on_play(self, func: Callable) -> None:
        """The event when the song is `played`

        :param func:
        :type func: Callable
        """
        self.on_play_func = func

    def on_skip(self, func: Callable) -> None:
        """The event when the song is `skipped`

        :param func:
        :type func: Callable
        """
        self.on_skip_func = func

    def on_stop(self, func: Callable) -> None:
        """The event when the player is `stopped`

        :param func:
        :type func: Callable
        """
        self.on_stop_func = func

    def on_pause(self, func: Callable) -> None:
        """The event when the song is `paused`

        :param func:
        :type func: Callable
        """
        self.on_pause_func = func

    def on_resume(self, func: Callable) -> None:
        """The event when the song is `resumed`

        :param func:
        :type func: Callable
        """
        self.on_resume_func = func

    def on_loop_toggle(self, func: Callable) -> None:
        """The event when the `looping` is `enabled`

        :param func:
        :type func: Callable
        """
        self.on_loop_toggle_func = func

    def on_volume_change(self, func: Callable) -> None:
        """The event when the `volume` is `changed`

        :param func:
        :type func: Callable
        """
        self.on_volume_change_func = func

    def on_remove_from_queue(self, func: Callable) -> None:
        """The event when the song is `removed from the queue`

        :param func:
        :type func: Callable
        """
        self.on_remove_from_queue_func = func

    async def queue(self, url: str, search: bool = False, bettersearch: bool = False) -> Song:
        """The song to queue

        :param url: The `url` of the song provider
        :type url: str
        :param search: Song Name, defaults to False
        :type search: bool, optional
        :param bettersearch: Search betterly or not, defaults to False
        :type bettersearch: bool, optional
        :return: The song with the minimum required data
        :rtype: Song
        """        
        song = await get_video_data(url, search, bettersearch, self.loop)
        self.music.queue[self.ctx.guild.id].append(song)
        if self.on_queue_func:
            await self.on_queue_func(self.ctx, song)
        return song

    async def play(self) -> Song:
        """Determines which song to play from the queue

        :return: See above
        :rtype: Song
        """        
        source = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(self.music.queue[self.ctx.guild.id][0].source,**self.ffmpeg_opts)
        )
        self.voice.play(
            source,
            after=lambda error: self.after_func(
                self.ctx,
                self.ffmpeg_opts,
                self.music,
                self.after_func,
                self.on_play_func,
                self.loop,
            ),
        )
        song = self.music.queue[self.ctx.guild.id][0]
        if self.on_play_func:
            await self.on_play_func(self.ctx, song)
        return song

    async def skip(self, force: bool = False) -> Union[Tuple[Song, Song], Song]:
        """Skips the current song which is being played

        :param force: Force skip or not, defaults to False
        :type force: bool, optional
        :raises NotPlaying: When there is no song played then this error is raised
        :raises EmptyQueue: When the queue is empty
        :return: It returns (old song, new song) or just (song) depending on the situtation
        :rtype: Union[Tuple[Song, Song], Song]
        """        
        if len(self.music.queue[self.ctx.guild.id]) == 0:
            raise NotPlaying("Cannot loop because nothing is being played")
        elif not len(self.music.queue[self.ctx.guild.id]) > 1 and not force:
            raise EmptyQueue("Cannot skip because queue is empty")
        old = self.music.queue[self.ctx.guild.id][0]
        old.is_looping = False if old.is_looping else False
        self.voice.stop()
        try:
            new = self.music.queue[self.ctx.guild.id][0]
            if self.on_skip_func:
                await self.on_skip_func(self.ctx, old, new)
            return (old, new)
        except IndexError:
            if self.on_skip_func:
                await self.on_skip_func(self.ctx, old)
            return old

    async def stop(self) -> None:
        """Stops the player

        :raises NotPlaying: When nothing is played
        """        
        try:
            self.music.queue[self.ctx.guild.id] = []
            self.voice.stop()
            self.music.players.remove(self)
        except:
            raise NotPlaying("Cannot loop because nothing is being played")
        if self.on_stop_func:
            await self.on_stop_func(self.ctx)

    async def pause(self) -> Song:
        """Pauses the player

        :raises NotPlaying: When nothing is played
        :return: The song on which the pause was initiated
        :rtype: Song
        """        
        try:
            self.voice.pause()
            song = self.music.queue[self.ctx.guild.id][0]
        except:
            raise NotPlaying("Cannot pause because nothing is being played")
        if self.on_pause_func:
            await self.on_pause_func(self.ctx, song)
        return song

    async def resume(self) -> Song:
        """Resumes the player

        :raises NotPlaying: When nothing was played by the player previously
        :return: The song which will be played
        :rtype: Song
        """        
        try:
            self.voice.resume()
            song = self.music.queue[self.ctx.guild.id][0]
        except:
            raise NotPlaying("Cannot resume because nothing is being played")
        if self.on_resume_func:
            await self.on_resume_func(self.ctx, song)
        return song

    def current_queue(self) -> Union[Iterable, Song]:
        """Gives the current queue of songs which is there in the player

        :raises EmptyQueue: When the song queue is empty
        :return: _description_
        :rtype: Union[Iterable, Song]
        """        
        try:
            return self.music.queue[self.ctx.guild.id]
        except KeyError:
            raise EmptyQueue("Queue is empty")

    def now_playing(self) -> Optional[Union[Iterable, Song]]:
        """Returns the :class:`Song` which is currently being played

        :return: See above
        :rtype: Optional[Union[Iterable, Song]]
        """        
        try:
            return self.music.queue[self.ctx.guild.id][0]
        except:
            return None

    async def toggle_song_loop(self) -> Optional[Union[Iterable, Song]]:
        """It toggles on/off the looping

        :raises NotPlaying: When no song is being played
        :return: The currently playing song or the looped queue
        :rtype: Optional[Union[Iterable, Song]]
        """        
        try:
            song = self.music.queue[self.ctx.guild.id][0]
        except:
            raise NotPlaying("Cannot loop because nothing is being played")
        if not song.is_looping:
            song.is_looping = True
        else:
            song.is_looping = False
        if self.on_loop_toggle_func:
            await self.on_loop_toggle_func(self.ctx, song)
        return song

    async def change_volume(self, vol: int) -> Tuple[Song, int]:
        """Change the song volume of the currently played song

        :param vol: The amount by the volume needs to increased or decreased
        :type vol: int
        :raises NotPlaying: When no song is played
        :return: (The song which is being played, volume no by which the song's volume was increased or decreased)
        :rtype: Tuple[Song, int]
        """        
        self.voice.source.volume = vol
        try:
            song = self.music.queue[self.ctx.guild.id][0]
        except:
            raise NotPlaying("Cannot loop because nothing is being played")
        if self.on_volume_change_func:
            await self.on_volume_change_func(self.ctx, song, vol)
        return (song, vol)

    async def remove_from_queue(self, index: int) -> Song:
        """The utility function to remove :class:`Song` from the queue

        :param index: The index at which the :class:`Song` is located
        :type index: int
        :raises NotPlaying: When nothing is player by the player
        :return: The song to be removed from the player
        :rtype: Song
        """        
        if index == 0:
            try:
                song = self.music.queue[self.ctx.guild.id][0]
            except:
                raise NotPlaying("Cannot loop because nothing is being played")
            await self.skip(force=True)
            return song
        song = self.music.queue[self.ctx.guild.id][index]
        self.music.queue[self.ctx.guild.id].pop(index)
        if self.on_remove_from_queue_func:
            await self.on_remove_from_queue_func(self.ctx, song)
        return song

    def delete(self) -> None:
        """Removes the song from the queue
        """        
        self.music.players.remove(self)


class Music:
    """The manager class to initiate and music and manage its player

    :raises RuntimeError: Is raised when the package is install without the .[voice] parameters
    :raises NotConnectedToVoice: See :func:`create_player`
    """    
    __slots__ = ['queue', 'players']
    def __init__(self):
        if not has_voice:
            raise RuntimeError("DiscordUtils[voice] install needed in order to use voice")

        self.queue: dict = {}
        self.players: list = []

    def create_player(self, ctx: commands.Context, **kwargs) -> MusicPlayer:
        """It create a music player, using which the music will be played in the `voice channels`

        :param ctx: The commands `context`
        :type ctx: commands.Context
        :raises NotConnectedToVoice: When the client is not connect to any of the voice channel
        :return: The music player using the user will have the control over its requested songs
        :rtype: MusicPlayer
        """        
        if not ctx.voice_client:
            raise NotConnectedToVoice(
                "Cannot create the player because bot is not connected to voice"
            )
        player = MusicPlayer(ctx, self, **kwargs)
        self.players.append(player)
        return player

    def get_player(self, **kwargs) -> Optional[MusicPlayer]:
        """Its gets the `MusicPlayer` of the specified `guild` or `voice channel`

        :return: See above
        :rtype: Optional[MusicPlayer]
        """        
        guild = kwargs.get("guild_id")
        channel = kwargs.get("channel_id")
        for player in self.players:
            if (guild and channel and player.ctx.guild.id == guild and player.voice.channel.id == channel):
                return player
            elif not guild and channel and player.voice.channel.id == channel:
                return player
            elif not channel and guild and player.ctx.guild.id == guild:
                return player

        return None
