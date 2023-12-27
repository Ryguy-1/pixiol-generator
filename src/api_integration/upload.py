from abc import ABC, abstractmethod
from typing import Optional, List
from api_integration.data_models import (
    PersistedAsset,
    PersistedCategory,
    PersistedNewsArticle,
)
from datetime import datetime
import contentful_management
import uuid
import os


class UploadAPI(ABC):
    @abstractmethod
    def upload_asset(self, local_file_path: str) -> PersistedAsset:
        """Uploads a file to the API and returns the created PersistedAsset object."""
        pass

    @abstractmethod
    def upload_category(self, category_title: str) -> PersistedCategory:
        """Uploads a category to the API and returns the created PersistedCategory object."""
        pass

    @abstractmethod
    def upload_news_article(
        self,
        title: str,
        content: str,
        publishedDate: datetime,
        featuredImage: PersistedAsset,
        categories: List[PersistedCategory],
    ) -> PersistedNewsArticle:
        """Uploads a news article to the API and returns the created PersistedNewsArticle object."""


class ContentfulUploadAPI(UploadAPI):
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

    def upload_asset(self, local_file_path: str) -> PersistedAsset:
        """Uploads a file to the API and returns the created Asset object."""
        unique_id = str(uuid.uuid4())
        extension = local_file_path.split(".")[-1]
        with open(local_file_path, "rb") as image_file:
            upload = self._client.uploads(self._space_id).create(image_file)
        asset = self._client.assets(self._space_id, self._environment_id).create(
            unique_id,
            {
                "fields": {
                    "title": {"en-US": unique_id},
                    "description": {"en-US": "Auto-Uploaded by Pixiol-Generator."},
                    "file": {
                        "en-US": {
                            "fileName": f"{uuid.uuid4()}.{extension}",
                            "contentType": f"image/{extension}",
                            "uploadFrom": upload.to_link().to_json(),
                        }
                    },
                }
            },
        )
        asset.process()
        asset = self._client.assets(self._space_id, self._environment_id).find(
            asset.id
        )  # refresh
        asset.publish()
        return PersistedAsset(id=asset.id, url=f"https:{asset.fields()['file']['url']}")

    def upload_category(self, category_title: str) -> PersistedCategory:
        """Uploads a category to the API and returns the created Category object."""
        unique_id = str(uuid.uuid4())
        category = self._client.entries(self._space_id, self._environment_id).create(
            unique_id,
            {
                "content_type_id": "category",
                "fields": {"title": {"en-US": category_title}},
            },
        )
        category.publish()
        return PersistedCategory(id=category.id, title=category_title)

    def upload_news_article(
        self,
        title: str,
        content: str,
        publishedDate: datetime,
        featuredImage: PersistedAsset,
        categories: List[PersistedCategory],
    ) -> PersistedNewsArticle:
        """Uploads a news article to the API and returns the created NewsArticle object."""
        unique_id = str(uuid.uuid4())
        formatted_datetime = publishedDate.strftime("%Y-%m-%dT%H:%M")
        news_article = self._client.entries(
            self._space_id, self._environment_id
        ).create(
            unique_id,
            {
                "content_type_id": "newsArticle",
                "fields": {
                    "title": {"en-US": title},
                    "content": {"en-US": content},
                    "featuredImage": {
                        "en-US": {
                            "sys": {
                                "id": featuredImage.id,
                                "type": "Link",
                                "linkType": "Asset",
                            }
                        }
                    },
                    "publishedDate": {
                        "en-US": formatted_datetime,
                    },
                    "categories": {
                        "en-US": [
                            {
                                "sys": {
                                    "id": category.id,
                                    "type": "Link",
                                    "linkType": "Entry",
                                }
                            }
                            for category in categories
                        ]
                    },
                },
            },
        )
        news_article.publish()
        return PersistedNewsArticle(
            id=news_article.id,
            title=title,
            content=content,
            publishedDate=formatted_datetime,
            featuredImage=featuredImage,
            categories=categories,
        )
