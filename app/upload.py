"""Secure helpers for handling file uploads."""

from __future__ import annotations

import uuid
from pathlib import Path

MAX_BYTES = 5_000_000
ALLOWED_TYPES = {"image/png", "image/jpeg"}

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
JPEG_SOI = b"\xff\xd8"
JPEG_EOI = b"\xff\xd9"


def sniff_image_type(data: bytes) -> str | None:
    """Return the media type if the bytes match a supported image signature."""
    if data.startswith(PNG_MAGIC):
        return "image/png"
    if data.startswith(JPEG_SOI) and data.endswith(JPEG_EOI):
        return "image/jpeg"
    return None


def secure_save(
    base_dir: str | Path, filename_hint: str, data: bytes
) -> tuple[bool, str]:
    """Persist validated image payloads with canonical path and UUID filenames."""
    if len(data) > MAX_BYTES:
        return False, "too_big"

    media_type = sniff_image_type(data)
    if media_type not in ALLOWED_TYPES:
        return False, "bad_type"

    base_path = Path(base_dir)
    if base_path.is_symlink():
        return False, "symlink_parent"

    try:
        root = base_path.resolve(strict=True)
    except FileNotFoundError:
        return False, "missing_base"

    extension = ".png" if media_type == "image/png" else ".jpg"
    generated_name = f"{uuid.uuid4()}{extension}"
    target = root / generated_name

    if any(parent.is_symlink() for parent in target.parents if parent != root):
        return False, "symlink_parent"

    resolved_target = target.resolve()

    if not resolved_target.is_relative_to(root):
        return False, "path_traversal"

    try:
        with open(resolved_target, "xb") as destination:
            destination.write(data)
    except FileExistsError:
        return False, "collision"

    return True, str(resolved_target)
