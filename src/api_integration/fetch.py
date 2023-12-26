from abc import ABC, abstractmethod
from typing import Optional, List
from api_integration.data_models import (
    PersistedCategory,
)
import contentful_management
import os


class FetchAPI(ABC):
    @abstractmethod
    def fetch_categories(self) -> List[PersistedCategory]:
        """Fetches all categories from the API and returns them as a list."""
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

    def fetch_categories(self) -> List[PersistedCategory]:
        """Fetches all categories from the API and returns them as a list."""
        space = self._client.spaces().find(self._space_id)
        environment = space.environments().find(self._environment_id)
        entries = environment.entries().all({"content_type": "category"})
        return [PersistedCategory(x.id, x.fields()["title"]) for x in entries]
