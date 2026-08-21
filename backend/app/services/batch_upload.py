from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from io import BytesIO
from pathlib import PurePosixPath
import zipfile


MAX_BATCH_FILES = 500
MAX_BATCH_IMAGE_SIZE = 10 * 1024 * 1024
MAX_BATCH_ARCHIVE_SIZE = 100 * 1024 * 1024
MAX_BATCH_TOTAL_SIZE = 100 * 1024 * 1024


@dataclass(frozen=True)
class BatchImage:
    filename: str
    content: bytes
    content_type: str
    suffix: str
    image_hash: str


@dataclass(frozen=True)
class SkippedBatchFile:
    filename: str
    detail: str


@dataclass(frozen=True)
class BatchImageCollection:
    images: list[BatchImage]
    skipped: list[SkippedBatchFile]


class BatchUploadError(ValueError):
    pass


def is_zip_filename(filename: str) -> bool:
    return filename.lower().endswith(".zip")


def is_zip_content(content: bytes) -> bool:
    return zipfile.is_zipfile(BytesIO(content))


def detect_image_type(content: bytes) -> tuple[str, str] | None:
    if content.startswith(b"\xff\xd8\xff"):
        return "image/jpeg", ".jpg"
    if content.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png", ".png"
    if content.startswith((b"GIF87a", b"GIF89a")):
        return "image/gif", ".gif"
    if content.startswith(b"RIFF") and content[8:12] == b"WEBP":
        return "image/webp", ".webp"
    return None


def _make_image(filename: str, content: bytes) -> BatchImage | SkippedBatchFile:
    detected_type = detect_image_type(content)

    if detected_type is None:
        return SkippedBatchFile(filename=filename, detail="不是支持的图片文件")

    if len(content) > MAX_BATCH_IMAGE_SIZE:
        return SkippedBatchFile(filename=filename, detail="图片超过 10MB 限制")

    content_type, suffix = detected_type
    return BatchImage(
        filename=filename,
        content=content,
        content_type=content_type,
        suffix=suffix,
        image_hash=sha256(content).hexdigest(),
    )


def _safe_zip_entry_name(filename: str) -> str:
    path = PurePosixPath(filename.replace("\\", "/"))

    if path.is_absolute() or ".." in path.parts:
        raise BatchUploadError("压缩包包含不安全的文件路径")

    return path.name


def _collect_zip_images(content: bytes, archive_name: str) -> BatchImageCollection:
    images: list[BatchImage] = []
    skipped: list[SkippedBatchFile] = []
    total_size = 0

    try:
        with zipfile.ZipFile(BytesIO(content)) as archive:
            for entry in archive.infolist():
                if entry.is_dir():
                    continue

                filename = _safe_zip_entry_name(entry.filename)

                if entry.flag_bits & 0x1:
                    skipped.append(SkippedBatchFile(filename=filename, detail="不支持加密压缩包内容"))
                    continue

                if entry.file_size > MAX_BATCH_IMAGE_SIZE:
                    skipped.append(SkippedBatchFile(filename=filename, detail="图片超过 10MB 限制"))
                    continue

                total_size += entry.file_size
                if total_size > MAX_BATCH_TOTAL_SIZE:
                    raise BatchUploadError("压缩包解压后的图片总大小不能超过 100MB")

                if len(images) + len(skipped) >= MAX_BATCH_FILES:
                    raise BatchUploadError("单次最多导入 500 个文件")

                item = _make_image(filename, archive.read(entry))
                if isinstance(item, BatchImage):
                    images.append(item)
                else:
                    skipped.append(item)
    except zipfile.BadZipFile as error:
        raise BatchUploadError(f"{archive_name} 不是可用的 ZIP 压缩包") from error

    return BatchImageCollection(images=images, skipped=skipped)


def collect_batch_images(files: list[tuple[str, bytes]]) -> BatchImageCollection:
    images: list[BatchImage] = []
    skipped: list[SkippedBatchFile] = []
    total_size = 0

    for filename, content in files:
        if is_zip_filename(filename) or is_zip_content(content):
            if len(content) > MAX_BATCH_ARCHIVE_SIZE:
                raise BatchUploadError("ZIP 压缩包不能超过 100MB")

            collection = _collect_zip_images(content, filename)
            images.extend(collection.images)
            skipped.extend(collection.skipped)
        else:
            item = _make_image(filename, content)
            if isinstance(item, BatchImage):
                images.append(item)
            else:
                skipped.append(item)

        if len(images) + len(skipped) > MAX_BATCH_FILES:
            raise BatchUploadError("单次最多导入 500 个文件")

    for image in images:
        total_size += len(image.content)
        if total_size > MAX_BATCH_TOTAL_SIZE:
            raise BatchUploadError("单次导入的图片总大小不能超过 100MB")

    return BatchImageCollection(images=images, skipped=skipped)
