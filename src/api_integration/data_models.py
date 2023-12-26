from dataclasses import dataclass
from typing import List
from datetime import datetime


@dataclass(frozen=True)
class Asset:
    id: str
    url: str


@dataclass(frozen=True)
class Category:
    id: int
    title: str


@dataclass(frozen=True)
class NewsArticle:
    id: int
    title: str
    content: str
    featuredImage: Asset
    publishedDate: datetime
    categories: List[Category]
