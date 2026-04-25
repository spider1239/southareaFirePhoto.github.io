#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path


SITE_DIR = Path(__file__).resolve().parent.parent
SOURCE_DIR = SITE_DIR / "src"
OUTPUT_JSON = SITE_DIR / "gallery-data.json"
OUTPUT_JS = SITE_DIR / "gallery-data.js"
DRIVE_FILE_MAP = SITE_DIR / "drive-file-map.json"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
THUMBNAIL_DIR_NAME = "縮略圖"
GROUP_ORDER = {"新人組": 0, "公開組": 1, "團舞": 2, "其他": 3}


def natural_sort_key(value: str) -> list[int | str]:
    parts = re.split(r"(\d+)", value)
    key: list[int | str] = []
    for part in parts:
        if not part:
            continue
        key.append(int(part) if part.isdigit() else part.casefold())
    return key


def classify_group(category_name: str) -> str:
    if category_name.startswith("新人組"):
        return "新人組"
    if category_name.startswith("公開組"):
        return "公開組"
    if category_name.startswith("團舞"):
        return "團舞"
    return "其他"


def relative_site_path(path: Path) -> str:
    return str(path.relative_to(SITE_DIR)).replace("\\", "/")


def versioned_asset_path(asset_path: str, src: Path) -> str:
    stat = src.stat()
    version = f"{stat.st_mtime_ns}-{stat.st_size}"
    return f"{asset_path}?v={version}"


def load_drive_file_map() -> dict[str, dict[str, str]]:
    if not DRIVE_FILE_MAP.exists():
        return {}
    return json.loads(DRIVE_FILE_MAP.read_text(encoding="utf-8"))


def drive_view_url(file_id: str) -> str:
    return f"https://drive.google.com/uc?export=view&id={file_id}"


def drive_embed_url(file_id: str, size: str = "w4000") -> str:
    return f"https://lh3.googleusercontent.com/d/{file_id}={size}"


def drive_download_url(file_id: str) -> str:
    return f"https://drive.google.com/uc?export=download&id={file_id}"


def drive_share_url(file_id: str) -> str:
    return f"https://drive.google.com/file/d/{file_id}/view"


def build_manifest() -> dict:
    categories = []
    drive_file_map = load_drive_file_map()

    category_dirs = sorted(
        (p for p in SOURCE_DIR.iterdir() if p.is_dir()),
        key=lambda path: (GROUP_ORDER.get(classify_group(path.name), 99), natural_sort_key(path.name)),
    )

    for category_dir in category_dirs:
        images = []
        thumbnail_dir = category_dir / THUMBNAIL_DIR_NAME
        local_image_paths = {
            path.name: path
            for path in category_dir.iterdir()
            if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
        }
        image_names = sorted(
            set(local_image_paths) | set(drive_file_map.get(category_dir.name, {})),
            key=natural_sort_key,
        )

        for image_name in image_names:
            image_path = local_image_paths.get(image_name)
            drive_file_id = drive_file_map.get(category_dir.name, {}).get(image_name)

            if image_path:
                relative_asset_path = relative_site_path(image_path)
                cache_busted_asset_path = versioned_asset_path(relative_asset_path, image_path)
            else:
                cache_busted_asset_path = ""

            thumbnail_path = thumbnail_dir / image_name
            if thumbnail_path.is_file() and thumbnail_path.suffix.lower() in IMAGE_EXTENSIONS:
                preview_asset_path = relative_site_path(thumbnail_path)
                preview_src = versioned_asset_path(preview_asset_path, thumbnail_path)
            else:
                preview_src = cache_busted_asset_path if cache_busted_asset_path else drive_embed_url(drive_file_id, "w1600")

            src = drive_embed_url(drive_file_id, "w4000") if drive_file_id else cache_busted_asset_path
            download = drive_download_url(drive_file_id) if drive_file_id else cache_busted_asset_path
            share_url = drive_share_url(drive_file_id) if drive_file_id else cache_busted_asset_path

            images.append(
                {
                    "name": Path(image_name).stem,
                    "filename": image_name,
                    "src": src,
                    "previewSrc": preview_src,
                    "download": download,
                    "shareUrl": share_url,
                }
            )

        categories.append(
            {
                "group": classify_group(category_dir.name),
                "name": category_dir.name,
                "count": len(images),
                "images": images,
            }
        )

    return {
        "title": SOURCE_DIR.name,
        "categoryCount": len(categories),
        "imageCount": sum(category["count"] for category in categories),
        "categories": categories,
    }


def main() -> None:
    manifest = build_manifest()
    manifest_json = json.dumps(manifest, ensure_ascii=False, indent=2)
    OUTPUT_JSON.write_text(manifest_json + "\n", encoding="utf-8")
    OUTPUT_JS.write_text(
        f"window.__GALLERY_DATA__ = {manifest_json};\n",
        encoding="utf-8",
    )
    print(f"Built gallery with {manifest['imageCount']} images across {manifest['categoryCount']} categories.")


if __name__ == "__main__":
    main()
