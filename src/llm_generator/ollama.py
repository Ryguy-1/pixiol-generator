from llm_generator.prompts import SystemMessage
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.llms.ollama import Ollama
from typing import Optional


class OllamaModel(object):
    def __init__(
        self,
        ollama_model_name: str,
        system_message: SystemMessage,
        temperature: float,
    ) -> None:
        """
        Initialize the Ollama Model.

        Params:
            ollama_model_name (str): The Ollama model name to use.
            system_message (SystemMessage): The System Message to use for the prompt.
            temperature (float): The temperature to use for the model.
        """
        self.ollama_model_name = ollama_model_name
        self.system_message = system_message
        self.temperature = temperature
        self.llm = Ollama(model=ollama_model_name, temperature=temperature)

    def run(self, human: Optional[str] = None) -> str:
        """
        Run the Model and return the output.

        Params:
            human (str): The human input to use for the model (optional).
        """
        chat_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.system_message.value),
                ("human", "{human_placeholder}"),
            ]
        )
        chain = chat_prompt | self.llm | StrOutputParser()
        output = chain.invoke({"human_placeholder": human})
        output = output.strip()
        return output
