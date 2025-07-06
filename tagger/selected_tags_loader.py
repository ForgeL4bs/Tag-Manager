import pandas as pd
from pathlib import Path


class SelectedTagsLoader:
    def __init__(self, csv_path: Path):
        self.csv_path = csv_path

    def load_tags(self):
        df = pd.read_csv(self.csv_path)
        tag_names = df["name"].tolist()
        rating_indexes = list(df.index[df["category"] == 9])
        general_indexes = list(df.index[df["category"] == 0])
        character_indexes = list(df.index[df["category"] == 4])
        return tag_names, rating_indexes, general_indexes, character_indexes

    def get_tag_by_index(self, index: int) -> str:
        if 0 <= index < len(self.tags):
            return self.tags[index]
        return ""

    def get_all_tags(self) -> list[str]:
        return self.tags
