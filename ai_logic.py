import os
from huggingface_hub import InferenceClient
from config import HF_TOKEN


def generate_image(prompt: str, save_path: str, model: str = "black-forest-labs/FLUX.1-schnell") -> str:
    client = InferenceClient(token=HF_TOKEN, provider="hf-inference")
    image = client.text_to_image(prompt, model=model)
    
    directory = os.path.dirname(save_path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    
    image.save(save_path)
    return save_path