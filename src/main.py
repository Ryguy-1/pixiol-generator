from config import *


def main():
    from llm_generator.in_out import OllamaInOut

    llm = OllamaInOut(model_name=OLLAMA_MODEL, temperature=OLLAMA_TEMPERATURE)
    article = llm.write_news_article(article_description="date ideas for the winter")
    print(f"Title: {article.get('title')}")
    print(f"Header Image Description: {article.get('header_img_description')}")
    print(f"Body: {article.get('body')}")

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
