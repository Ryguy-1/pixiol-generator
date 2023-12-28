from abc import ABC
from langchain.llms.ollama import Ollama
from langchain_core.messages import HumanMessage, SystemMessage
from typing import Dict
import json


class InOut(ABC):
    def __init__(self, llm):
        self._llm = llm

    def write_news_article(self, article_description: str) -> Dict:
        system_message = """
=== High Level ===
- You are a professional AI journalist trained in writing long (10+ min read), informative, and engaging articles
- You must use eye-catching markdown (highly varied and interesting syntax akin to high quality medium artiles)
- Allowed Markdown Elements: [ ## H2, ### H3, **bold**, *italic*, > blockquote, 1. ol item, - ul item, `code`, ---, [title](url), ![alt text](image.jpg) ]

=== Output Format ===
- Output must be valid JSON (checked with json.loads)
- Output must have exactly 3 keys: [ title, header_img_description, body ]
- Example Format: {"title": "SEO Optimized Title", "header_img_description": "hyper-detailed description of image to use for header image", "body": "## Intro Paragraph\n\nFollowed by entire rest of article all in raw markdown."}
        """
        messages = [
            SystemMessage(content=system_message),
            HumanMessage(content=f"An article about {article_description}"),
        ]

        while True:
            try:
                generated_text = self._llm.invoke(input=messages)
                generated_text = generated_text.strip()
                generated_text = generated_text.replace("\n", "\\n")
                loaded_json = json.loads(generated_text)
                expected_keys = ["title", "header_img_description", "body"]
                assert all([key in loaded_json for key in expected_keys])
                assert all([isinstance(loaded_json[key], str) for key in expected_keys])
                assert all([len(loaded_json[key]) > 0 for key in expected_keys])
                return loaded_json
            except Exception as e:
                print(str(e))


class OllamaInOut(InOut):
    def __init__(self, model_name: str, temperature: int):
        llm = Ollama(model=model_name, temperature=temperature)
        super().__init__(llm)
