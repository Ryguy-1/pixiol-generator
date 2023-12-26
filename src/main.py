from api_integration.upload import ContentfulUploadAPI
from config import *


def main():
    api = ContentfulUploadAPI(
        management_api_token=CONTENTFUL_MANAGEMENT_API_TOKEN,
        space_id=CONTENTFUL_SPACE_ID,
        environment_id=CONTENTFUL_ENVIRONMENT_ID,
    )
    # print(api.upload_asset("src/balloons.jpg"))
    # print(api.upload_category("Test Category"))
    


if __name__ == "__main__":
    main()
