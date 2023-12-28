from diffusers import StableDiffusionXLPipeline
from abc import ABC, abstractmethod
from PIL import Image
import torch
from typing import Optional


class TextToImage(ABC):
    @abstractmethod
    def generate_image(self, prompt: str) -> bytes:
        """
        Generates image from prompt.

        Args:
            prompt (str): Prompt to generate image from.

        Returns:
            bytes: Image as bytes.
        """
        pass


class LocalSDXLTextToImage(TextToImage):
    def __init__(
        self, model_path: str, num_inference_steps: Optional[int] = 50
    ) -> None:
        """
        Loads local SDXL model.

        Args:
            model_path (str): Path to SDXL model.
            num_inference_steps (int, optional): Number of inference steps. Defaults to 50.
        """
        self._model_path = model_path
        self._num_inference_steps = num_inference_steps
        self._pipe = StableDiffusionXLPipeline.from_single_file(
            model_path,
            torch_dtype=torch.float16,
            use_safetensors=True,
        ).to("cuda")
        self._pipe.enable_model_cpu_offload()  # low vram optimization

    def generate_image(self, prompt: str) -> Image:
        image = self._pipe(
            prompt=prompt,
            num_inference_steps=self._num_inference_steps,
        ).images[0]
        return image
