from config import *
from llm_generator.in_out import OllamaInOut
from diffusion_generator.text_to_image import DiffusersTextToImage
from classifiers.nsfw_classify import HuggingfaceNSFWClassify
from api_integration.upload import ContentfulUploadAPI
from api_integration.fetch import ContentfulFetchAPI
from datetime import datetime
from typing import Tuple
import random


def main() -> None:
    """Run Indefinitely Creating and Publishing New Articles"""
    while True:
        try:
            create_novel_article(*initialize_apis())
        except Exception as e:
            print(str(e))


def initialize_apis() -> (
    Tuple[
        ContentfulFetchAPI,
        OllamaInOut,
        OllamaInOut,
        DiffusersTextToImage,
        HuggingfaceNSFWClassify,
        ContentfulUploadAPI,
    ]
):
    """Initialize All APIs"""
    fetch_api = ContentfulFetchAPI(
        management_api_token=CONTENTFUL_MANAGEMENT_API_TOKEN,
        space_id=CONTENTFUL_SPACE_ID,
        environment_id=CONTENTFUL_ENVIRONMENT_ID,
    )
    llm_idea_generator = OllamaInOut(
        model_name=OLLAMA_MODEL, temperature=TEMPERATURE_IDEA_GENERATOR
    )
    llm_writer = OllamaInOut(model_name=OLLAMA_MODEL, temperature=TEMPERATURE_WRITER)
    gen = DiffusersTextToImage(
        pretrained_model_name_or_path=HUGGINGFACE_DIFFUSERS_PRETRAINED_MODEL_NAME_OR_PATH
    )
    nsfw_classify = HuggingfaceNSFWClassify(
        pretrained_model_name_or_path=HUGGINGFACE_NSFW_CLASSIFIER_PRETRAINED_MODEL_NAME_OR_PATH
    )
    upload_api = ContentfulUploadAPI(
        management_api_token=CONTENTFUL_MANAGEMENT_API_TOKEN,
        space_id=CONTENTFUL_SPACE_ID,
        environment_id=CONTENTFUL_ENVIRONMENT_ID,
    )
    return fetch_api, llm_idea_generator, llm_writer, gen, nsfw_classify, upload_api


def create_novel_article(
    fetch_api: ContentfulFetchAPI,
    llm_idea_generator: OllamaInOut,
    llm_writer: OllamaInOut,
    gen: DiffusersTextToImage,
    nsfw_classify: HuggingfaceNSFWClassify,
    upload_api: ContentfulUploadAPI,
) -> None:
    """Creates a New Article and Publishes"""

    all_categories = fetch_api.fetch_categories()
    if len(all_categories) == 0:
        quit("No Categories Found, Exiting...")
    category_constraint = [x.title for x in all_categories]

    kill_vram_processes()
    random_category = random.choice(category_constraint)
    article_idea = llm_idea_generator.generate_random_article_idea(
        category_injection=random_category
    )

    article = llm_writer.write_news_article(
        article_idea=article_idea,
        category_constraint=category_constraint,
    )

    kill_vram_processes()
    img = gen.generate_image(
        prompt=article["header_img_description"],
        negative_prompt=NEGATIVE_PROMPT_FILTER,
    )

    if nsfw_classify.check_is_nsfw(img):
        return

    uploaded_asset = upload_api.upload_asset(img)
    upload_api.upload_news_article(
        title=article["title"],
        content=article["body"],
        publishedDate=datetime.now(),
        featuredImage=uploaded_asset,
        categories=[x for x in all_categories if x.title in article["category_list"]],
    )


def kill_vram_processes() -> None:
    """Used to Kill VRAM Processes Before Continuing"""
    OllamaInOut.kill()
    DiffusersTextToImage.kill()


if __name__ == "__main__":
    main()
