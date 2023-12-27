from abc import ABC, abstractmethod
from typing import Optional, List
from api_integration.data_models import (
    PersistedAsset,
    PersistedCategory,
    PersistedNewsArticle,
)
import contentful_management
import os


class FetchAPI(ABC):
    @abstractmethod
    def fetch_asset_by_id(self, asset_id: str) -> PersistedAsset:
        """Fetches an asset by ID from the API and returns it."""
        pass

    @abstractmethod
    def fetch_assets(self) -> List[PersistedAsset]:
        """Fetches all assets from the API and returns them as a list."""
        pass

    @abstractmethod
    def fetch_category_by_id(self, category_id: str) -> PersistedCategory:
        """Fetches a category by ID from the API and returns it."""
        pass

    @abstractmethod
    def fetch_categories(self) -> List[PersistedCategory]:
        """Fetches all categories from the API and returns them as a list."""
        pass

    @abstractmethod
    def fetch_news_article_by_id(self, news_article_id: str) -> PersistedNewsArticle:
        """Fetches a news article by ID from the API and returns it."""
        pass

    @abstractmethod
    def fetch_news_articles(self) -> List[PersistedNewsArticle]:
        """Fetches all news articles from the API and returns them as a list."""
        pass


class ContentfulFetchAPI(FetchAPI):
    def __init__(
        self,
        management_api_token: Optional[str],
        space_id: Optional[str] = None,
        environment_id: Optional[str] = None,
    ) -> None:
        """
        Initializes the Contentful API client.
        If not provided, all variables will be read from the environment.

        Args:
            management_api_token: The Contentful management API token.
            space_id: The ID of the space to upload the asset to.
            environment_id: The ID of the environment to upload the asset to.

        Environment Variables:
            CONTENTFUL_MANAGEMENT_API_TOKEN
            CONTENTFUL_SPACE_ID
            CONTENTFUL_ENVIRONMENT_ID
        """
        if management_api_token is None:
            management_api_token = os.environ["CONTENTFUL_MANAGEMENT_API_TOKEN"]
        if space_id is None:
            space_id = os.environ["CONTENTFUL_SPACE_ID"]
        if environment_id is None:
            environment_id = os.environ["CONTENTFUL_ENVIRONMENT_ID"]
        if None in [management_api_token, space_id, environment_id]:
            raise ValueError(
                "Must Set CONTENTFUL_MANAGEMENT_API_TOKEN, CONTENTFUL_SPACE_ID, and CONTENTFUL_ENVIRONMENT_ID"
            )
        self._client = contentful_management.Client(management_api_token)
        self._space_id = space_id
        self._environment_id = environment_id

    def fetch_asset_by_id(self, asset_id: str) -> PersistedAsset:
        """Fetches an asset by ID from the API and returns it."""
        space = self._client.spaces().find(self._space_id)
        environment = space.environments().find(self._environment_id)
        asset = environment.assets().find(asset_id)
        return PersistedAsset(asset.id, asset.fields()["file"]["url"])

    def fetch_assets(self) -> List[PersistedAsset]:
        """Fetches all assets from the API and returns them as a list."""
        space = self._client.spaces().find(self._space_id)
        environment = space.environments().find(self._environment_id)
        assets = environment.assets().all()
        return [PersistedAsset(x.id, x.fields()["file"]["url"]) for x in assets]

    def fetch_category_by_id(self, category_id: str) -> PersistedCategory:
        """Fetches a category by ID from the API and returns it."""
        space = self._client.spaces().find(self._space_id)
        environment = space.environments().find(self._environment_id)
        entry = environment.entries().find(category_id)
        return PersistedCategory(entry.id, entry.fields()["title"])

    def fetch_categories(self) -> List[PersistedCategory]:
        """Fetches all categories from the API and returns them as a list."""
        space = self._client.spaces().find(self._space_id)
        environment = space.environments().find(self._environment_id)
        entries = environment.entries().all({"content_type": "category"})
        return [PersistedCategory(x.id, x.fields()["title"]) for x in entries]

    def fetch_news_article_by_id(self, news_article_id: str) -> PersistedNewsArticle:
        """Fetches a news article by ID from the API and returns it."""
        space = self._client.spaces().find(self._space_id)
        environment = space.environments().find(self._environment_id)
        entry = environment.entries().find(news_article_id)
        # Note: Contentful Quirk: use _ separator for camelCase fields here
        return PersistedNewsArticle(
            id=entry.id,
            title=entry.fields()["title"],
            content=entry.fields()["content"],
            publishedDate=entry.fields()["published_date"],
            featuredImage=self.fetch_asset_by_id(entry.fields()["featured_image"].id),
            categories=[
                self.fetch_category_by_id(x.id) for x in entry.fields()["categories"]
            ],
        )

    def fetch_news_articles(self) -> List[PersistedNewsArticle]:
        """Fetches all news articles from the API and returns them as a list."""
        space = self._client.spaces().find(self._space_id)
        environment = space.environments().find(self._environment_id)
        entries = environment.entries().all({"content_type": "newsArticle"})
        # Note: Contentful Quirk: use _ separator for camelCase fields here
        return [
            PersistedNewsArticle(
                id=x.id,
                title=x.fields()["title"],
                content=x.fields()["content"],
                publishedDate=x.fields()["published_date"],
                featuredImage=self.fetch_asset_by_id(x.fields()["featured_image"].id),
                categories=[
                    self.fetch_category_by_id(y.id) for y in x.fields()["categories"]
                ],
            )
            for x in entries
        ]
