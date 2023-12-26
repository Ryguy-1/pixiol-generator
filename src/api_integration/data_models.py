from dataclasses import dataclass
from typing import List
from datetime import datetime


@dataclass(frozen=True)
class PersistedAsset:
    id: str
    url: str


@dataclass(frozen=True)
class PersistedCategory:
    id: int
    title: str


@dataclass(frozen=True)
class PersistedNewsArticle:
    id: int
    title: str
    content: str
    featuredImage: PersistedAsset
    publishedDate: datetime
    categories: List[PersistedCategory]
