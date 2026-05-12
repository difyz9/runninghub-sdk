"""Download the generated popular aesthetics text-to-image outputs.

Usage:
    python download_popular_aesthetics_images.py
    python download_popular_aesthetics_images.py --output-dir ./downloads/custom
"""

from __future__ import annotations

import argparse
from pathlib import Path
from urllib.parse import urlparse

import httpx


# IMAGE_URLS = [
#     "https://rh-images.xiaoyaoyou.com/c91531cbf3337fbe998612da4112ea99/output/ComfyUI_00001_jdtov_1778449972.png",
#     "https://rh-images.xiaoyaoyou.com/c91531cbf3337fbe998612da4112ea99/output/ComfyUI_00002_xfcxo_1778449972.png",
#     "https://rh-images.xiaoyaoyou.com/c91531cbf3337fbe998612da4112ea99/output/ComfyUI_00003_mtcls_1778449972.png",
#     "https://rh-images.xiaoyaoyou.com/c91531cbf3337fbe998612da4112ea99/output/ComfyUI_00004_evlje_1778449973.png",
#     "https://rh-images.xiaoyaoyou.com/c91531cbf3337fbe998612da4112ea99/output/ComfyUI_00005_ttylx_1778449973.png",
#     "https://rh-images.xiaoyaoyou.com/c91531cbf3337fbe998612da4112ea99/output/ComfyUI_00006_tpglk_1778449973.png",
#     "https://rh-images.xiaoyaoyou.com/c91531cbf3337fbe998612da4112ea99/output/ComfyUI_00007_huzoi_1778450034.png",
#     "https://rh-images.xiaoyaoyou.com/c91531cbf3337fbe998612da4112ea99/output/ComfyUI_00008_vpgpo_1778450034.png",
#     "https://rh-images.xiaoyaoyou.com/c91531cbf3337fbe998612da4112ea99/output/ComfyUI_00009_mvczo_1778450034.png",
#     "https://rh-images.xiaoyaoyou.com/c91531cbf3337fbe998612da4112ea99/output/ComfyUI_00010_oiaji_1778450035.png",
#     "https://rh-images.xiaoyaoyou.com/c91531cbf3337fbe998612da4112ea99/output/ComfyUI_00011_kueoa_1778450035.png",
#     "https://rh-images.xiaoyaoyou.com/c91531cbf3337fbe998612da4112ea99/output/ComfyUI_00012_ioghz_1778450035.png",
# ]

IMAGE_URLS = [

"https://rh-images-1252422369.cos.ap-beijing.myqcloud.com/c91531cbf3337fbe998612da4112ea99/output/ComfyUI_00001_tppnh_1778575569.png",
"https://rh-images-1252422369.cos.ap-beijing.myqcloud.com/c91531cbf3337fbe998612da4112ea99/output/ComfyUI_00002_lfjhn_1778575569.png",
"https://rh-images-1252422369.cos.ap-beijing.myqcloud.com/c91531cbf3337fbe998612da4112ea99/output/ComfyUI_00003_auyle_1778575569.png",
"https://rh-images-1252422369.cos.ap-beijing.myqcloud.com/c91531cbf3337fbe998612da4112ea99/output/ComfyUI_00004_lslil_1778575570.png",
"https://rh-images-1252422369.cos.ap-beijing.myqcloud.com/c91531cbf3337fbe998612da4112ea99/output/ComfyUI_00005_jusch_1778575570.png",
"https://rh-images-1252422369.cos.ap-beijing.myqcloud.com/c91531cbf3337fbe998612da4112ea99/output/ComfyUI_00006_klqhz_1778575570.png",

]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        default=str(Path(__file__).resolve().parent / "downloads" / "popular_aesthetics"),
        help="Directory where the images will be saved.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing files if they already exist.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=60.0,
        help="Per-request timeout in seconds.",
    )
    return parser.parse_args()


def filename_from_url(url: str, index: int) -> str:
    parsed = urlparse(url)
    name = Path(parsed.path).name
    return name or f"image_{index:02d}.png"


def download_image(client: httpx.Client, url: str, output_path: Path, overwrite: bool) -> Path:
    if output_path.exists() and not overwrite:
        print(f"skip_existing: {output_path}")
        return output_path

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with client.stream("GET", url) as response:
        response.raise_for_status()
        with output_path.open("wb") as file_obj:
            for chunk in response.iter_bytes():
                file_obj.write(chunk)
    return output_path


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir).expanduser().resolve()

    print("download_count:", len(IMAGE_URLS))
    print("output_dir:", output_dir)

    with httpx.Client(timeout=args.timeout, follow_redirects=True) as client:
        for index, url in enumerate(IMAGE_URLS, start=1):
            filename = filename_from_url(url, index)
            target = output_dir / filename
            saved_path = download_image(client, url, target, overwrite=args.overwrite)
            print(f"[{index}] saved: {saved_path}")

    print("All images downloaded successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())