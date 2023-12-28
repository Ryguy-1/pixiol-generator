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

    pipe = StableDiffusionXLPipeline.from_single_file(
        model_path,
        torch_dtype=torch.float16,
        use_safetensors=True,
    ).to("cuda")
    pipe.enable_model_cpu_offload()

    image = pipe(
        prompt="a couple walking on the beach romantic picture",
        num_inference_steps=50,
    ).images[0]

    image.save("test.png")


if __name__ == "__main__":
    main()
