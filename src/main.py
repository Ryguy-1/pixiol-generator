from abc import ABC, abstractmethod
from textwrap import dedent, indent
import functools
import inspect


INSTALLED_PACKAGES = [
    "wikipedia",
    "requests",
    "bs4",  # beautifulsoup4
    "numpy",
    "pandas",
    "Pillow",
]

function_signatures = []


def store_function_signature(func):
    sig = inspect.signature(func)
    function_signatures.append(f"{func.__name__}{sig}")

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


def get_formatted_function_signatures():
    return ",\n".join(function_signatures)


def get_formatted_installed_packages():
    return ",\n".join(INSTALLED_PACKAGES)


class LLMPipe(ABC):
    """Abstract class for taking input and outputting a message"""

    @abstractmethod
    def __call__(self, prompt: str) -> str:
        """Take prompt and output a message."""
        pass


class OllamaLLMPipe(LLMPipe):
    """Ollama Language Model"""

    def __init__(self, model_name: str, temperature: float):
        from langchain.llms.ollama import Ollama

        self._model = Ollama(model=model_name, temperature=temperature)

    def __call__(self, prompt: str) -> str:
        return self._model(prompt).strip().removesuffix("<|im_end|>")


prompt = dedent(
    """
    \"""
    System Instructions:
    - You are an AI agent capable of writing Python code to produce the desired result as stated by the user.
    - If you use any packages, be sure to import them.
    - Use no try/except blocks, as in the event of an error, you will have more chances.
    - Use standard Python syntax - your string will be ran using exec().
    - Your code must have a function with signature "def get_result() -> str:" that returns the final result created for the user.

    Installed Packages:
    [
    {packages_list}
    ]

    Pre-Defined Custom Functions:
    [
    {function_list}
    ]

    === Example Code 1 ===
    def get_result() -> str:
        result = 2 * 3
        return str(result)

    === Example Code 2 ===
    def get_random_number() -> int:
        import random
        return random.randint(0, 100)
    def get_result() -> str:
    result = get_random_number() + 2

    === Example Code 3 ===
    def get_result() -> str:
        from textwrap import dedent
        return dedent(
            \"""
                # Top 10 Things to Do in San Diego
                1. Visit the San Diego Zoo
                2. Visit the San Diego Zoo Safari Park
                3. Go to the beach
                ### ...
            \"""
        )



    === Now it's your turn ===

    User Goal:
    {user_goal}

    # Your Code (answer returned with "def get_result() -> str"):
    \"""
    """
)


@store_function_signature
def add(num1: float, num2: float) -> float:
    return num1 + num2


@store_function_signature
def subtract_num2_from_num1(num1: float, num2: float) -> float:
    return num1 - num2


# USER_GOAL = dedent(
#     """
#     write me a markdown news article about the best coding tools for beginners.
#     be sure to use advanced markdown because you are a professional. Don't put a title, but make sure to use
#     proper markdown headings like ##, ###, ####, etc.
#     """
# )
USER_GOAL = dedent(
    """
    search the internet for a hd image of a goat and give me the url
    """
)
model = OllamaLLMPipe(model_name="mistral-openorca", temperature=0.8)

prompt = prompt.format(
    packages_list=indent(get_formatted_installed_packages(), " " * 4),
    function_list=indent(get_formatted_function_signatures(), " " * 4),
    user_goal=USER_GOAL,
)
print(prompt)

while True:
    print("================")
    llm_function_in_text = model(prompt)
    print(llm_function_in_text)

    # NOTE: Prevent model from using try/except
    if "try:" in llm_function_in_text:
        print("Sending Back to LLM...")
        continue

    # Evaluate function and get result
    try:
        exec(llm_function_in_text)
        result = get_result()  # type: ignore (defined by llm)
        if result is None:
            raise Exception("Function returned None")
        print(result)
        break
    except Exception as e:
        print(e)
        continue

# EVALUATE
