from abc import ABC, abstractmethod
from textwrap import dedent, indent
from typing import List, Tuple
import functools
import inspect

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
    System Instructions:
    - You are an AI agent capable of writing a Python function to achieve the desired goal stated by the user.
    - While most questions will not be coding questions, you will use code as a method to communicate your process and result.
    - Use standard Python syntax.
    - You may use any standard Python library functions, but make sure to import properly within the function.
    - Extra functions will also be available that are already pre-defined by the system (listed under "Available Extra Functions").
    - Your function must return the final answer and only the final answer.
    - You may only write a single function that must have the signature "def answer_question() -> str".

    Available Extra Functions:
    [
    {function_list}
    ]

    Example Function 1:
    def answer_question() -> str:
        result = multiply(2, 3)
        result = divide_num1_by_num2(result, 2)
        return result

    Example Function 2:
    def answer_question() -> str:
        import random
        def append_hello(text: str) -> str:
            return f"Hello {{text}}!"
        result1 = wikipedia_search("Python (programming language)")
        result2 = wikipedia_search("Python (genus)")
        result = random.choice([result1, result2])
        result = append_hello(result)
        return result

    Example Function 3:
    def answer_question() -> str:
        return "A long time ago in a galaxy far, far away...."
        

    === Now it's your turn ===

    User Goal:
    {user_goal}

    Your Function:
    """
)


@store_function_signature
def add(num1: float, num2: float) -> float:
    return num1 + num2


@store_function_signature
def subtract_num2_from_num1(num1: float, num2: float) -> float:
    return num1 - num2


USER_GOAL = "write an article on the history of the Star Wars franchise"
model = OllamaLLMPipe(model_name="mistral-openorca", temperature=0)

prompt = prompt.format(
    function_list=indent(get_formatted_function_signatures(), " " * 4),
    user_goal=USER_GOAL,
)
print(prompt)

while True:
    llm_function_in_text = model(prompt)
    print(llm_function_in_text)
    try:
        exec(llm_function_in_text)
        print(answer_question())  # type: ignore (defined by llm)
        break
    except Exception as e:
        print(e)
        print("Sending Back to LLM...")
        continue

# EVALUATE
