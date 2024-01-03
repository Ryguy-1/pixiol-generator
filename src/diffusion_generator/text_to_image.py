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

    @staticmethod
    @abstractmethod
    def kill() -> None:
        """
        Kills all processes that are using VRAM.
        """
        pass


class DiffusersTextToImage(TextToImage):
    def __init__(
        self,
        pretrained_model_name_or_path: str,
        num_inference_steps: Optional[int] = 50,
        enable_cpu_offload: Optional[bool] = True,
    ) -> None:
        """
        Loads local SDXL model.

        Args:
            pretrained_model_name_or_path (str): Huggingface Diffusers Download Path.
            num_inference_steps (int, optional): Number of inference steps.
            enable_cpu_optim (bool, optional): Enables CPU optimization. (use when not enough VRAM or no GPU)
        """
        from diffusers import DiffusionPipeline

        self._pretrained_model_name_or_path = pretrained_model_name_or_path
        self._num_inference_steps = num_inference_steps
        self._pipe = DiffusionPipeline.from_pretrained(
            self._pretrained_model_name_or_path,
            torch_dtype=torch.float16,
        )
        if enable_cpu_offload:
            self._pipe.enable_sequential_cpu_offload()
        else:
            self._pipe.to("cuda")

    def generate_image(self, prompt: str, negative_prompt: str) -> Image:
        image = self._pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=self._num_inference_steps,
        ).images[0]
        return image

    @staticmethod
    def kill() -> None:
        pass  # Diffusers automatically implements this
