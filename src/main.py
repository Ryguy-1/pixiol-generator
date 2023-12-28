from config import *


def main():
    from llm_generator.in_out import write_news_article
    article = write_news_article(article_description="why dogs are cool")
    print(article.get(''))

    # from api_integration.upload import ContentfulUploadAPI
    # import os

    # api = ContentfulUploadAPI(
    #     management_api_token=CONTENTFUL_MANAGEMENT_API_TOKEN,
    #     space_id=CONTENTFUL_SPACE_ID,
    #     environment_id=CONTENTFUL_ENVIRONMENT_ID,
    # )
    # from diffusion_generator.text_to_image import LocalSDXLTextToImage

    # gen = LocalSDXLTextToImage(model_path=os.path.join(SDXL_PATH))
    # img = gen.generate_image("image of a rainbow umbrella in the rain very bright")
    # uploaded_asset = api.upload_asset(img)
    # print(uploaded_asset)


if __name__ == "__main__":
    main()
