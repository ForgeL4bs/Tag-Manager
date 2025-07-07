import os
from pathlib import Path
import requests
from tqdm import tqdm

MODEL_DIR = Path("models")
MODEL_DIR.mkdir(parents=True, exist_ok=True)

# urls for models and csv file
FILES_TO_DOWNLOAD = {
    "wd-vit-tagger-v3.onnx": "https://huggingface.co/SmilingWolf/wd-vit-tagger-v3/resolve/main/model.onnx",
    "wd-vit-large-tagger-v3.onnx": "https://huggingface.co/SmilingWolf/wd-vit-large-tagger-v3/resolve/main/model.onnx",
    "selected_tags.csv": "https://huggingface.co/SmilingWolf/wd-vit-large-tagger-v3/resolve/main/selected_tags.csv",
}


def download_file(url: str, dest: Path):
    if dest.exists():
        print(f"[✔]  {dest.name} already exists, skipping download.")
        return

    response = requests.get(url, stream=True)
    total = int(response.headers.get("content-length", 0))

    with open(dest, "wb") as file, tqdm(
        desc=f"Downloading {dest.name}",
        total=total,
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for chunk in response.iter_content(chunk_size=1024):
            size = file.write(chunk)
            bar.update(size)


if __name__ == "__main__":
    for filename, url in FILES_TO_DOWNLOAD.items():
        dest_path = MODEL_DIR / filename
        download_file(url, dest_path)

    print("\n✅ All model files downloaded successfully.")
