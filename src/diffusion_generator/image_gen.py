from diffusers import AutoPipelineForText2Image
from PIL import Image
import torch

pipeline = AutoPipelineForText2Image.from_pretrained(
    "runwayml/stable-diffusion-v1-5", torch_dtype=torch.float16, variant="fp16"
).to("cuda")

image = pipeline("dog, photorealistic, christmas sweater").images[0]
image.save("test.png")