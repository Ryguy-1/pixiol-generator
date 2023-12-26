from abc import ABC, abstractmethod
from typing import Optional
import contentful_management
import uuid
import os


class UploadAPI(ABC):
    @abstractmethod
    def upload_asset(self, local_file_path: str) -> str:
        """Uploads a file to the API and returns the URL of the uploaded file."""
        pass


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
        self._client = contentful_management.Client("MANAGEMENT_API_TOKEN")
        self._space_id = space_id
        self._environment_id = environment_id

    def upload_asset(self, local_file_path: str) -> str:
        """Uploads a file to Contentful and returns the URL of the uploaded file."""
        unique_id = str(uuid.uuid4())
        extension = local_file_path.split(".")[-1]
        with open(local_file_path, "rb") as image_file:
            upload = self._client.uploads(self._space_id).create(image_file)
        asset = self._client.assets(self._space_id, self._environment_id).create(
            unique_id,
            {
                "fields": {
                    "file": {
                        "en-US": {
                            "fileName": f"{uuid.uuid4()}.{extension}",  # ex: 1234-1234-1234-1234.png
                            "contentType": f"image/{extension}",  # ex: image/png
                            "uploadFrom": upload.to_link().to_json(),
                        }
                    }
                }
            },
        )
        asset.process()
        asset.publish()
        public_url = asset.fields["file"]["en-US"]["url"]
        return public_url
