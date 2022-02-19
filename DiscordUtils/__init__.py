from __future__ import annotations

from .invitetracker import InviteTracker
from .music import Music, MusicPlayer, NotPlaying, NotConnectedToVoice, EmptyQueue
from .embeds import *
from .paginator import *

__all__ = [
    'InviteTracker', 
    'Music',
    'MusicPlayer',
    'Embed',
    'ErrorEmbed',
    'SuccessEmbed',
    'StarboardEmbed',
    'RoboPages',
    'FieldPageSource',
    'TextPageSource',
    'SimplePageSource',
    'SimplePages',
    'EmbedPageSource',
    'EmbedPaginator',
    'NotPlaying',
    'NotConnectedToVoice',
    'EmptyQueue'
]

__title__ = "DiscordUtils"
__version__ = "1.3.5"
__author__ = "Dhruvacube"
__license__ = "MIT"
