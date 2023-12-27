from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class PersistedAsset:
    id: str
    url: str


@dataclass(frozen=True)
class PersistedCategory:
    id: str
    title: str


@dataclass(frozen=True)
class PersistedNewsArticle:
    id: str
    title: str
    content: str
    publishedDate: str
    featuredImage: PersistedAsset
    categories: List[PersistedCategory]
