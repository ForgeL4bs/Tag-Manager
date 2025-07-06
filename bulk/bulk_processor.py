# Bulk tagging logic
from pathlib import Path
from PIL import Image
from tagger.model_runner import ONNXTagger


def tag_single_image(image_path: Path, tagger: ONNXTagger, output_dir: Path):
    try:
        image = Image.open(image_path)
        sorted_general, rating, sorted_character, general_res = tagger.predict(image)
        tags = sorted_general + sorted_character
        output_path = output_dir / f"{image_path.stem}.txt"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(", ".join(tags))
        return (image_path.name, True, None)
    except Exception as e:
        return (image_path.name, False, str(e))


def bulk_tag_images(tagger, folder_path: str, general_mcut=False, character_mcut=False):
    folder = Path(folder_path)
    image_exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    images = [p for p in folder.iterdir() if p.suffix.lower() in image_exts]
    print(f"Found {len(images)} images.")
    results = []
    for img_path in images:
        try:
            image = Image.open(img_path)
            sorted_general, rating, sorted_character, general_res = tagger.predict(
                image, general_mcut=general_mcut, character_mcut=character_mcut
            )
            tags = sorted_general + sorted_character
            txt_path = img_path.with_suffix(".txt")
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(", ".join(tags))
            results.append((img_path.name, True, None))
        except Exception as e:
            print(f"Failed to process {img_path.name}: {e}")
            results.append((img_path.name, False, str(e)))
    return results
