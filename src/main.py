from config import *
from llm_generator.in_out import OllamaInOut
from diffusion_generator.text_to_image import DiffusersTextToImage
from api_integration.upload import ContentfulUploadAPI
from api_integration.fetch import ContentfulFetchAPI
from datetime import datetime
from inquirer import prompt, Confirm


def main():
    fetch_api = ContentfulFetchAPI(
        management_api_token=CONTENTFUL_MANAGEMENT_API_TOKEN,
        space_id=CONTENTFUL_SPACE_ID,
        environment_id=CONTENTFUL_ENVIRONMENT_ID,
    )
    llm = OllamaInOut(model_name=OLLAMA_MODEL, temperature=OLLAMA_TEMPERATURE)
    gen = DiffusersTextToImage(
        pretrained_model_name_or_path=HUGGINGFACE_DIFFUSERS_PRETRAINED_MODEL_NAME_OR_PATH
    )
    upload_api = ContentfulUploadAPI(
        management_api_token=CONTENTFUL_MANAGEMENT_API_TOKEN,
        space_id=CONTENTFUL_SPACE_ID,
        environment_id=CONTENTFUL_ENVIRONMENT_ID,
    )
    while True:
        # Fetch Categories
        all_categories = fetch_api.fetch_categories()
        category_constraint = [x.title for x in all_categories]

        # Generate Random Article Ideas
        kill_vram_processes()
        article_idea = llm.generate_random_article_description(
            category_init=category_constraint  # use constrain as init prompt
        )
        print(f"Article Idea: {article_idea}\n\n")

        # Generate Article For That Idea
        article = llm.write_news_article(
            article_description=article_idea,
            category_constraint=category_constraint,
        )
        print(f"Title: {article['title']}")
        print(f"Category List: {article['category_list']}")
        print(f"Image Description: {article['header_img_description']}")
        print(f"Body Start: {article['body']}")

        # ask if should publish
        should_publish = prompt(
            [
                Confirm(
                    "should_publish",
                    message="Should Publish?",
                    default=False,
                )
            ]
        )["should_publish"]
        if not should_publish:
            continue

        # Generate Image
        kill_vram_processes()
        img = gen.generate_image(article["header_img_description"])

        # Publish Article
        uploaded_asset = upload_api.upload_asset(img)
        print(f"Uploaded Asset: {uploaded_asset}")

        uploaded_article = upload_api.upload_news_article(
            title=article["title"],
            content=article["body"],
            publishedDate=datetime.now(),
            featuredImage=uploaded_asset,
            categories=[
                x for x in all_categories if x.title in article["category_list"]
            ],
        )
        print(f"Uploaded Article: {uploaded_article}")

        # ask if should generate another
        should_generate_another = prompt(
            [
                Confirm(
                    "should_generate_another",
                    message="Should Generate Another?",
                    default=True,
                )
            ]
        )["should_generate_another"]
        if not should_generate_another:
            break


def kill_vram_processes() -> None:
    """Used to Kill VRAM Processes Before Continuing"""
    OllamaInOut.kill()


if __name__ == "__main__":
    main()
