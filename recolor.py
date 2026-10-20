"""Recolor the dark parts of a PDF by rendering each page as an image."""

import io

import fitz  # PyMuPDF
import numpy as np
from PIL import Image

DPI = 300

PALETTE = {
    "blue": ("Blue", (0, 0, 255)),
    "navy": ("Navy", (27, 42, 107)),
    "red": ("Red", (200, 16, 46)),
    "green": ("Green", (0, 112, 60)),
    "violet": ("Violet", (91, 42, 134)),
}

LUMA_WEIGHTS = np.array([0.299, 0.587, 0.114], dtype=np.float32)


def recolor_pdf(data: bytes, target_rgb: tuple[int, int, int]) -> bytes:
    source = fitz.open(stream=data, filetype="pdf")
    output = fitz.open()
    try:
        for page in source:
            _append_recolored_page(output, page, target_rgb)
        return output.tobytes(garbage=3, deflate=True)
    finally:
        output.close()
        source.close()


def _append_recolored_page(output: fitz.Document, page: fitz.Page, target_rgb: tuple[int, int, int]) -> None:
    image = _render_recolored(page, target_rgb)
    new_page = output.new_page(width=page.rect.width, height=page.rect.height)
    new_page.insert_image(new_page.rect, stream=_encode_png(image))


def _render_recolored(page: fitz.Page, target_rgb: tuple[int, int, int]) -> Image.Image:
    zoom = DPI / 72
    pixmap = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), colorspace=fitz.csRGB, alpha=False)
    rgb = _pixmap_to_array(pixmap)
    return _tint(_darkness(rgb), target_rgb)


def _pixmap_to_array(pixmap: fitz.Pixmap) -> np.ndarray:
    raw = np.frombuffer(pixmap.samples, dtype=np.uint8)
    return raw.reshape(pixmap.h, pixmap.w, pixmap.n)[:, :, :3].astype(np.float32)


def _darkness(rgb: np.ndarray) -> np.ndarray:
    """0 for white, 1 for black. Grays in between keep their anti-aliasing."""
    luminance = rgb @ LUMA_WEIGHTS
    return 1.0 - luminance / 255.0


def _tint(darkness: np.ndarray, target_rgb: tuple[int, int, int]) -> Image.Image:
    target = np.array(target_rgb, dtype=np.float32)
    tinted = 255.0 - (255.0 - target) * darkness[..., np.newaxis]
    return Image.fromarray(np.clip(tinted, 0, 255).astype(np.uint8), "RGB")


def _encode_png(image: Image.Image) -> bytes:
    buffer = io.BytesIO()
    image.save(buffer, format="PNG", optimize=True)
    return buffer.getvalue()
