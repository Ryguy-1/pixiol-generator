from config import *


def main():
    import os
    import torch

    # print torch gpu info
    print("torch.cuda.is_available():", torch.cuda.is_available())

    model_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "models",
        "juggernautXL_v7Rundiffusion.safetensors",
    )

    from diffusers import StableDiffusionXLPipeline

    pipeline = StableDiffusionXLPipeline.from_single_file(
        model_path,
        torch_dtype=torch.float16,
        variant="fp16",
    ).to("cuda")
    pipeline.enable_xformers_memory_efficient_attention()

    image = pipeline("test image").images[0]

    image.save("test.png")


if __name__ == "__main__":
    main()
