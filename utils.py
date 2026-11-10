import base64
import hashlib
import io

from PIL import Image, ImageOps, UnidentifiedImageError

MAX_FILE_BYTES = 10 * 1024 * 1024  # 10MB
MAX_SIDE = 1024


class ImageError(Exception):
    """Raised with a user-facing message when an image can't be used."""


def image_hash(image_bytes: bytes) -> str:
    return hashlib.sha256(image_bytes).hexdigest()


def preprocess(image_bytes: bytes) -> bytes:
    """Validate, fix orientation, downscale and re-encode an image as JPEG bytes."""
    if len(image_bytes) > MAX_FILE_BYTES:
        raise ImageError("파일이 너무 커요. 10MB 이하의 사진을 올려주세요.")

    try:
        img = Image.open(io.BytesIO(image_bytes))
        img.load()
    except (UnidentifiedImageError, OSError):
        raise ImageError("이미지 파일을 열 수 없어요. JPG, PNG, WEBP 사진을 올려주세요.")

    img = ImageOps.exif_transpose(img)
    if img.mode != "RGB":
        img = img.convert("RGB")
    img.thumbnail((MAX_SIDE, MAX_SIDE))  # keeps aspect ratio, only shrinks

    out = io.BytesIO()
    img.save(out, format="JPEG", quality=90)
    return out.getvalue()


def to_data_url(image_bytes: bytes, mime_type: str = "image/jpeg") -> str:
    """Encode raw image bytes as a base64 data URL for the OpenAI vision API."""
    encoded = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"
