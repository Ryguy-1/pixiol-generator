from config import *


def main():
    publish_new_article(
        article_description="top 10 things to do with your dog in the summer in san diego"
    )


def publish_new_article(article_description: str) -> None:
    from llm_generator.in_out import OllamaInOut
    from diffusion_generator.text_to_image import LocalSDXLTextToImage
    from api_integration.upload import ContentfulUploadAPI
    from api_integration.fetch import ContentfulFetchAPI
    from datetime import datetime
    import os

    fetch_api = ContentfulFetchAPI(
        management_api_token=CONTENTFUL_MANAGEMENT_API_TOKEN,
        space_id=CONTENTFUL_SPACE_ID,
        environment_id=CONTENTFUL_ENVIRONMENT_ID,
    )
    all_categories = fetch_api.fetch_categories()
    category_constraint = [x.title for x in all_categories]
    print(f"Category Constraint: {category_constraint}")

    llm = OllamaInOut(model_name=OLLAMA_MODEL, temperature=OLLAMA_TEMPERATURE)
    article = llm.write_news_article(
        article_description=article_description, category_constraint=category_constraint
    )
    print(f"Title: {article['title']}")
    print(f"Category List: {article['category_list']}")
    print(f"Header Image Description: {article['header_img_description']}")
    print(f"Body: {article['body']}")

    gen = LocalSDXLTextToImage(model_path=os.path.join(SDXL_PATH))
    img = gen.generate_image(article["header_img_description"])

    upload_api = ContentfulUploadAPI(
        management_api_token=CONTENTFUL_MANAGEMENT_API_TOKEN,
        space_id=CONTENTFUL_SPACE_ID,
        environment_id=CONTENTFUL_ENVIRONMENT_ID,
    )
    uploaded_asset = upload_api.upload_asset(img)
    print(uploaded_asset)
    chosen_categories = [
        x for x in all_categories if x.title in article["category_list"]
    ]
    print(chosen_categories)
    upload_api.upload_news_article(
        title=article["title"],
        content=article["body"],
        publishedDate=datetime.now(),
        featuredImage=uploaded_asset,
        categories=chosen_categories,
    )


if __name__ == "__main__":
    main()
