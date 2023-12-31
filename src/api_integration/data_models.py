from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class PersistedAsset:
    """Represents a Persisted Asset in Storage"""

    id: str
    url: str


@dataclass(frozen=True)
class PersistedCategory:
    """Represents a Persisted Category in Storage"""

    id: str
    title: str


@dataclass(frozen=True)
class PersistedNewsArticle:
    """Represents a Persisted News Article in Storage"""

    id: str
    title: str
    content: str
    publishedDate: str
    featuredImage: PersistedAsset
    categories: List[PersistedCategory]
