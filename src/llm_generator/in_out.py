from abc import ABC
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.llms.base import BaseLLM
from langchain.llms.ollama import Ollama
from typing import Dict, List
from textwrap import dedent
import subprocess
import json
import re


class InOut(ABC):
    """InOut class for interacting with LLMs."""

    def __init__(self, llm: BaseLLM) -> None:
        """Initializes InOut class."""
        self._llm = llm

    def generate_random_article_idea(self, category_injection: str) -> str:
        """
        Generates a random article idea.

        Args:
            phrase_init (str): Word to initialize the article idea with.
            category_injection (str): Category to inject into prompt for latent space activation.

        Returns:
            str: Random article idea.
        """
        system_message = dedent(
            """
            === High Level ===
            - You are an AI writer on medium.com who comes up with great article ideas (single phrase ideas similar to titles)
            - All article ideas should answer questions people search for on Google
            - Be sure to explore a wide variety of topics - this is critically important (ideate in all categories equally)
            - Both domain-specific and general topics are allowed, and a mix of both is encouraged
            - Ideas shuold be hyper-sepcific and long-tail
            - Ideas must be interesting for the rest of time (not time-sensitive content)
            - Ideas must be non-controvertial in any way (no politics, no religion, no ethics, nothing illegal, etc.)

            === Output Format ===
            - Output must just be single line article idea (no JSON, no newlines, etc.)
            """
        )

        messages = [
            SystemMessage(content=system_message),
            HumanMessage(
                content=f"Request: 'Please give me one idea exactly', Broad Category Idea: '{category_injection}'"
            ),
        ]
        generated_text = self._llm.invoke(input=messages)
        generated_text = generated_text.replace("<|im_end|>", "")
        generated_text = generated_text.replace("\n", " ")
        generated_text = generated_text.replace('"', "")
        generated_text = generated_text.replace(".", "")
        generated_text = generated_text.strip()

        return generated_text

    def write_news_article(
        self, article_idea: str, category_constraint: List[str]
    ) -> Dict:
        """
        Writes a news article.

        Args:
            article_idea (str): Idea for article.
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
            - You must use eye-catching markdown (highly varied and interesting syntax akin to high quality medium.com articles)
            - Your article must be at least 1000 words in length - this is important because it should have a medium.com-level of detail (very in depth)
            - Never cut an article short - always write until the end with no ellipses (e.g. never end with "..." or "to be continued", etc.)
            - Each section of the article must be a minimum of 5 sentences long and ideally 10+ sentences long (as formatting allows)
            - Allowed Markdown Elements: [ ## H2, ### H3, **bold**, *italic*, > blockquote, 1. ol item, - ul item, `code`, --- ]
            
            === Output Format ===
            - Output must be valid JSON (checked with json.loads)
            - Output must have exactly 4 keys: [ title, category_list, header_img_description, body ]
            - Output example format: 
                {
                    "title": "<Long, Specific, and SEO Optimized Title>", 
                    "category_list": <["category_1", "category_2"]>, 
                    "header_img_description": "<hyper-detailed description of image to use for header image>", 
                    "body": "<## Body in Markdown\\n\\nShould use expressive markdown syntax.>"
                }
            """
        )
        messages = [
            SystemMessage(content=system_message),
            HumanMessage(
                content=f"Article Idea: '{article_idea}', Categories to Choose From: {category_constraint}"
            ),
        ]

        while True:
            try:
                generated_text = self._llm.invoke(input=messages)
                generated_text = generated_text.replace("<|im_end|>", "")
                generated_text = self._clean_output_json_newline(generated_text)
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

    @staticmethod
    def _clean_output_json_newline(json_string: str) -> str:
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
                subprocess.run(["kill", "-9", pid], check=True)
                print(f"Ollama runner with PID {pid} has been successfully killed.")
            else:
                print("Ollama runner process not found.")
        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")
