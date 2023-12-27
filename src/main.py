from api_integration.upload import ContentfulUploadAPI
from api_integration.fetch import ContentfulFetchAPI
from datetime import datetime
from config import *


def main():
    upload_api = ContentfulUploadAPI(
        management_api_token=CONTENTFUL_MANAGEMENT_API_TOKEN,
        space_id=CONTENTFUL_SPACE_ID,
        environment_id=CONTENTFUL_ENVIRONMENT_ID,
    )
    uploaded_baloons = upload_api.upload_asset("src/balloons.jpg")  # upload baloon
    fetch_api = ContentfulFetchAPI(
        management_api_token=CONTENTFUL_MANAGEMENT_API_TOKEN,
        space_id=CONTENTFUL_SPACE_ID,
        environment_id=CONTENTFUL_ENVIRONMENT_ID,
    )
    medicine = None  # get medicine category
    for category in fetch_api.fetch_categories():
        if category.title == "Medicine":
            medicine = category
            break
    if medicine is None:
        raise ValueError("Medicine category not found")

    uploaded_news_article = upload_api.upload_news_article(
        title="Test News Article",
        content="# This is a test news article!",
        featuredImage=uploaded_baloons,
        publishedDate=datetime.now(),
        categories=[medicine],
    )
    print(uploaded_news_article)


if __name__ == "__main__":
    main()
