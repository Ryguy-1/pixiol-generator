from api_integration.upload import ContentfulUploadAPI
from api_integration.fetch import ContentfulFetchAPI
from config import *


def main():
    api = ContentfulUploadAPI(
        management_api_token=CONTENTFUL_MANAGEMENT_API_TOKEN,
        space_id=CONTENTFUL_SPACE_ID,
        environment_id=CONTENTFUL_ENVIRONMENT_ID,
    )
    # print(api.upload_asset("src/balloons.jpg"))
    # print(api.upload_category("Test Category"))
    api = ContentfulFetchAPI(
        management_api_token=CONTENTFUL_MANAGEMENT_API_TOKEN,
        space_id=CONTENTFUL_SPACE_ID,
        environment_id=CONTENTFUL_ENVIRONMENT_ID,
    )
    print(api.fetch_categories())


if __name__ == "__main__":
    main()
