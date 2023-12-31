from abc import ABC, abstractmethod
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

    SYSTEM_PROMPTS = {
        "generate_random_article_idea": dedent(
            """
            === High Level ===
            - You are an AI writer on medium.com who comes up with great article ideas (single phrase ideas similar to titles)
            - All article ideas should answer questions people search for on Google
            - Be sure to explore a wide variety of topics - this is critically important
            - Both domain-specific and general topics are allowed, and a mix of both is encouraged
            - Ideas shuold be hyper-sepcific and long-tail
            - Ideas must be interesting for the rest of time (not time-sensitive content)
            - Ideas must be non-controvertial in any way (no politics, no religion, no ethics, nothing illegal, etc.)

            === Output Format ===
            - Output must just be single line article idea (no JSON, no newlines, etc.)
            """
        ),
        "write_news_article": dedent(
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
            - Output example format (<> = replace with your own content):
                {
                    "title": "<Long, Specific, and SEO Optimized Title>", 
                    "category_list": <["category_1", "category_2"]>, 
                    "header_img_description": "<hyper-detailed description of image to use for header image>", 
                    "body": "<## Body in Markdown\\n\\nShould use expressive markdown syntax with proper \\"escape\\" characters>"
                }
            """
        ),
    }

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

        messages = [
            SystemMessage(content=self.SYSTEM_PROMPTS["generate_random_article_idea"]),
            HumanMessage(
                content=f"Request: 'Please give me one idea exactly', Broad Category Idea: '{category_injection}'"
            ),
        ]
        return self._parse_single_line_output(self._llm.invoke(input=messages))

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
                "title": "<Long, Specific, and SEO Optimized Title>",
                "category_list": <["category_1", "category_2"]>,
                "header_img_description": "<hyper-detailed description of image to use for header image>",
                "body": "<## Body in Markdown\\n\\nShould use expressive markdown syntax with proper \\"escape\\" characters>"
            }
        """
        messages = [
            SystemMessage(content=self.SYSTEM_PROMPTS["write_news_article"]),
            HumanMessage(
                content=f"Article Idea: '{article_idea}', Categories to Choose From: {category_constraint}"
            ),
        ]
        while True:
            try:
                generated_text = self._llm.invoke(input=messages)
                loaded_json = self._parse_json_output(generated_text)
                self._raise_for_bad_json_output(
                    input_json=loaded_json,
                    expected_keys_to_type={
                        "title": str,
                        "category_list": list,
                        "header_img_description": str,
                        "body": str,
                    },
                )
                # Custom validation -> (1-3 categories)
                assert len(loaded_json["category_list"]) in list(range(1, 4))
                # Custom validation -> all categories in constraint
                assert all(
                    category in category_constraint
                    for category in loaded_json["category_list"]
                )
                return loaded_json
            except Exception as e:
                print(str(e))

    @staticmethod
    def _parse_single_line_output(input: str) -> str:
        """
        Parses single line output from LLM.

        Args:
            input (str): Input string to clean.

        Returns:
            str: Cleaned string.
        """
        input = input.replace("<|im_end|>", "")
        input = input.replace("\n", " ")
        input = input.replace('"', "")
        input = input.replace(".", "")
        input = input.strip()
        return input

    @staticmethod
    def _parse_json_output(json_string: str) -> Dict:
        """
        Parses JSON output from LLM.

        Args:
            json_string (str): JSON string to clean.

        Returns:
            Dict: Cleaned JSON.

        Raises:
            JSONDecodeError: If JSON string is not valid.
        """
        json_string = json_string.replace("<|im_end|>", "")
        removed_internal_newlines = re.sub(
            r'\"([^"]*)\"',  # match anything in quotes including quotes
            lambda match: match.group(0).replace("\n", "\\n"),
            json_string,
        )
        return json.loads(removed_internal_newlines)

    @staticmethod
    def _raise_for_bad_json_output(
        input_json: Dict, expected_keys_to_type: Dict
    ) -> None:
        """
        Raises for bad JSON format.

        Args:
            input_json (Dict): Loaded JSON.
            expected_keys_to_type (Dict): Expected keys to type mapping.

        Raises:
            AssertionError: If JSON is not valid.
        """
        assert isinstance(input_json, dict), "Output is not valid JSON."
        assert set(input_json.keys()) == set(
            expected_keys_to_type.keys()
        ), "Output keys do not match expected keys."
        for input_key, input_value in input_json.items():
            assert (
                type(input_value) == expected_keys_to_type[input_key]
            ), f"Value for key '{input_key}' is not of expected type '{expected_keys_to_type[input_key]}'."

    @staticmethod
    @abstractmethod
    def kill() -> None:
        """Kills LLM runner process."""
        pass


class OllamaInOut(InOut):
    def __init__(self, model_name: str, temperature: int):
        print(f"Pulling Ollama model: {model_name}")
        subprocess.run(["ollama", "pull", model_name], check=True)
        print(f"Running Ollama model: {model_name}")
        llm = Ollama(model=model_name, temperature=temperature)
        super().__init__(llm)

    @staticmethod
    def kill():
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
