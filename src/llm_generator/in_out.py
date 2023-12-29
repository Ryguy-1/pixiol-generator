from abc import ABC
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.llms.ollama import Ollama
from typing import Dict, List
from textwrap import dedent
import subprocess
import json
import re


class InOut(ABC):
    def __init__(self, llm):
        self._llm = llm

    def write_news_article(
        self, article_description: str, category_constraint: List[str]
    ) -> Dict:
        """
        Writes a news article.

        Args:
            article_description (str): Description of article.
            category_constraint (List[str]): List of categories to constrain output selection to.

        Returns:
            Dict: News article.

        Return Format:
            {
                "title": "Title Here"
                "category_list": ["category_1", "category_2"],
                "header_img_description": "Description of Header Image",
                "body": "## Intro Paragraph\n\nFollowed by entire rest of article all in raw markdown."
            }
        """
        system_message = dedent(
            """
            === High Level ===
            - You are a professional AI journalist trained in writing long (10+ min read), informative, and engaging articles
            - You must use eye-catching markdown (highly varied and interesting syntax akin to high quality medium artiles)
            - Allowed Markdown Elements: [ ## H2, ### H3, **bold**, *italic*, > blockquote, 1. ol item, - ul item, `code`, ---, [title](url), ![alt text](image.jpg) ]

            === Output Format ===
            - Output must be valid JSON (checked with json.loads)
            - Output must have exactly 4 keys: [ title, category_list, header_img_description, body ]
            - Output example format: 
                {
                    "title": "Long, Specific, and SEO Optimized Title", 
                    "category_list": ["category_1", "category_2"], 
                    "header_img_description": "hyper-detailed description of image to use for header image", 
                    "body": "## Article Here\\n\\nEntire rest of article all in raw markdown."
                }
            """
        )
        print(system_message)
        messages = [
            SystemMessage(content=system_message),
            HumanMessage(
                content=f"Article Description: '{article_description}', Categories to Choose From: {category_constraint}"
            ),
        ]

        while True:
            try:
                generated_text = self._llm.invoke(input=messages)
                generated_text = generated_text.strip()
                generated_text = self._clean_json_string_newline(generated_text)
                print(f"Generated Text: {generated_text}")
                loaded_json = json.loads(generated_text)
                str_expected_keys = [
                    "title",
                    "header_img_description",
                    "body",
                ]
                for key in str_expected_keys:
                    assert key in loaded_json
                    assert isinstance(loaded_json[key], str)
                    assert len(loaded_json[key]) > 0
                list_expected_keys = ["category_list"]
                for key in list_expected_keys:
                    assert key in loaded_json
                    assert isinstance(loaded_json[key], list)
                    assert len(loaded_json[key]) > 0
                    assert all(isinstance(item, str) for item in loaded_json[key])
                    # check that all categories are in the constraint
                    assert all(
                        category in category_constraint for category in loaded_json[key]
                    )

                return loaded_json
            except Exception as e:
                print(str(e))

    def _clean_json_string_newline(self, json_string: str) -> str:
        """
        Replaces internal newlines with escaped newlines in JSON string.

        Args:
            json_string (str): JSON string.

        Returns:
            str: JSON string with internal newlines replaced with escaped newlines.
        """

        def replace_newlines(match):
            return match.group(0).replace("\n", "\\n")

        return re.sub(r'\"([^"]*)\"', replace_newlines, json_string)


class OllamaInOut(InOut):
    def __init__(self, model_name: str, temperature: int):
        print(f"Pulling Ollama model: {model_name}")
        subprocess.run(["ollama", "pull", model_name], check=True)
        print(f"Running Ollama model: {model_name}")
        llm = Ollama(model=model_name, temperature=temperature)
        super().__init__(llm)

    @staticmethod
    def kill():
        """
        Finds and kills the Ollama runner process. Useful for freeing up VRAM.
        (must run as sudo, should be ok in docker container)
        """
        try:
            result = subprocess.run(
                ["pgrep", "-f", "ollama-runner"], capture_output=True, text=True
            )
            pid = result.stdout.strip()
            if pid:
                subprocess.run(["sudo", "kill", "-9", pid], check=True)
                print(f"Ollama runner with PID {pid} has been successfully killed.")
            else:
                print("Ollama runner process not found.")
        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")
