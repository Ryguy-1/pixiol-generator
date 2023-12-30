from abc import ABC, abstractmethod
from PIL import Image
import torch
from typing import Optional


class TextToImage(ABC):
    @abstractmethod
    def generate_image(self, prompt: str, negative_prompt: str) -> Image:
        """
        Generates image from prompt.

        Args:
            prompt (str): Prompt to generate image from.
            negative_prompt (str): Negative prompt to generate image from.

        Returns:
            Image: Generated image.
        """
        pass


class DiffusersTextToImage(TextToImage):
    def __init__(
        self,
        pretrained_model_name_or_path: str,
        num_inference_steps: Optional[int] = 50,
    ) -> None:
        """
        Loads local SDXL model.

        Args:
            pretrained_model_name_or_path (str): Huggingface Diffusers Download Path.
            num_inference_steps (int, optional): Number of inference steps. Defaults to 50.
        """
        from diffusers import DiffusionPipeline

        self._pretrained_model_name_or_path = pretrained_model_name_or_path
        self._num_inference_steps = num_inference_steps
        self._pipe = DiffusionPipeline.from_pretrained(
            self._pretrained_model_name_or_path,
            torch_dtype=torch.float16,
        )
        self._pipe.enable_sequential_cpu_offload()

    def generate_image(self, prompt: str, negative_prompt: str) -> Image:
        image = self._pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=self._num_inference_steps,
        ).images[0]
        return image
