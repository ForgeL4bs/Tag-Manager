import onnxruntime as ort
import numpy as np
from PIL import Image
from pathlib import Path

MODEL_INPUT_SIZE = (448, 448)


def mcut_threshold(probs):
    sorted_probs = probs[probs.argsort()[::-1]]
    difs = sorted_probs[:-1] - sorted_probs[1:]
    t = difs.argmax()
    thresh = (sorted_probs[t] + sorted_probs[t + 1]) / 2
    return thresh


class ONNXTagger:
    def __init__(
        self,
        model_path: Path,
        tag_names: list,
        rating_indexes: list,
        general_indexes: list,
        character_indexes: list,
        general_threshold: float = 0.35,
        character_threshold: float = 0.85,
    ):
        self.model_path = model_path
        self.tag_names = tag_names
        self.rating_indexes = rating_indexes
        self.general_indexes = general_indexes
        self.character_indexes = character_indexes
        self.general_threshold = general_threshold
        self.character_threshold = character_threshold
        self.session = ort.InferenceSession(
            str(model_path), providers=["CPUExecutionProvider"]
        )
        self.input_name = self.session.get_inputs()[0].name
        self.target_size = self.session.get_inputs()[0].shape[1]

    def prepare_image(self, image: Image.Image, target_size: int) -> np.ndarray:
        if image.mode == "RGBA":
            canvas = Image.new("RGBA", image.size, (255, 255, 255))
            canvas.alpha_composite(image)
            image = canvas.convert("RGB")
        else:
            image = image.convert("RGB")
        max_dim = max(image.size)
        pad_left = (max_dim - image.size[0]) // 2
        pad_top = (max_dim - image.size[1]) // 2
        padded = Image.new("RGB", (max_dim, max_dim), (255, 255, 255))
        padded.paste(image, (pad_left, pad_top))
        if max_dim != target_size:
            padded = padded.resize((target_size, target_size), Image.BICUBIC)
        image_np = np.asarray(padded, dtype=np.float32)
        image_np = image_np[:, :, ::-1]
        image_np = np.expand_dims(image_np, axis=0)
        return image_np

    def predict(self, image: Image.Image, general_mcut=False, character_mcut=False):
        input_tensor = self.prepare_image(image, self.target_size)
        preds = self.session.run(None, {self.input_name: input_tensor})[0][0]
        labels = list(zip(self.tag_names, preds.astype(float)))

        ratings = [labels[i] for i in self.rating_indexes]
        rating = dict(ratings)

        general_names = [labels[i] for i in self.general_indexes]
        general_probs = np.array([x[1] for x in general_names])
        general_thresh = (
            mcut_threshold(general_probs) if general_mcut else self.general_threshold
        )
        general_res = [x for x in general_names if x[1] > general_thresh]
        general_res = dict(general_res)

        character_names = [labels[i] for i in self.character_indexes]
        character_probs = np.array([x[1] for x in character_names])
        character_thresh = (
            mcut_threshold(character_probs)
            if character_mcut
            else self.character_threshold
        )
        character_res = [x for x in character_names if x[1] > character_thresh]
        character_res = dict(character_res)

        sorted_general = sorted(general_res.items(), key=lambda x: x[1], reverse=True)
        sorted_general = [x[0] for x in sorted_general]
        sorted_character = sorted(
            character_res.items(), key=lambda x: x[1], reverse=True
        )
        sorted_character = [x[0] for x in sorted_character]
        return sorted_general, rating, sorted_character, general_res

    def set_thresholds(self, general, character):
        self.general_threshold = general
        self.character_threshold = character

    def get_model_info(self) -> str:
        return (
            f"Model: {self.model_path.name}, "
            f"General Threshold: {self.general_threshold}, "
            f"Character Threshold: {self.character_threshold}, "
            f"Labels: {len(self.tag_names)}"
        )
