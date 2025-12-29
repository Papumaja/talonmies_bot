from pathlib import Path
from PIL import ImageFile, Image
import uuid

IMG_PATH = Path().cwd().resolve() / "data" / "images"


def save_image_to_disk(img: ImageFile) -> str:
    if not IMG_PATH.exists():
        IMG_PATH.mkdir(parents=True, exist_ok=True)

    name = f"{str(uuid.uuid4())}.{img.format}"
    img.save(IMG_PATH / name)
    return name


def load_image_from_diks(name: str):
    if (IMG_PATH / name).exists():
        try:
            return Image.open(IMG_PATH / name)
        except Exception as e:
            print(e)
            return None
