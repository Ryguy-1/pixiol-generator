from abc import ABC, abstractmethod
from PIL import Image


class NSFWClassify(ABC):
    @abstractmethod
    def check_is_nsfw(self, image: Image) -> bool:
        """
        Checks if image is NSFW.

        Args:
            image (Image): Image to check.

        Returns:
            bool: True if NSFW else False.
        """
        pass

    @staticmethod
    @abstractmethod
    def kill() -> None:
        """
        Kills all processes that are using VRAM.
        """
        pass


class HuggingfaceNSFWClassify(NSFWClassify):
    def __init__(
        self,
        pretrained_model_name_or_path: str,
    ) -> None:
        """
        Huggingface NSFW classifier.

        Args:
            pretrained_model_name_or_path (str): Pretrained model name or path.
        """
        from transformers import pipeline

        self._pretrained_model_name_or_path = pretrained_model_name_or_path
        self._classifier = pipeline(
            "image-classification", model=self._pretrained_model_name_or_path
        )

    def check_is_nsfw(self, image: Image) -> bool:
        result = self._classifier(image)
        return result[0]["label"] == "nsfw"

    @staticmethod
    def kill() -> None:
        pass  # No VRAM processes to kill (auto-cleaned)
